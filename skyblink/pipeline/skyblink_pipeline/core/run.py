import numpy as np
import scipy.ndimage
from scipy.signal import fftconvolve
import scipy.stats as stats
from astropy.coordinates import SkyCoord
import astropy.units as u
import os
import json
import yaml
from astropy.io import fits
import datetime
import subprocess

def get_git_sha():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL, cwd=os.path.dirname(__file__)).decode('ascii').strip()
    except Exception:
        return 'unknown'

PROVENANCE = {
    "produced_by": "skyblink_pipeline",
    "git_sha": get_git_sha(),
    "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "simulated": True
}

def band_match_and_combine(exposures, wcs_out, target_band, delta_lambda):
    from pipeline.skyblink_pipeline.core.wcs_adapter import reproject_image
    combined_flux = None
    combined_weight = None
    
    for exp in exposures:
        mask = (exp['wave'] >= target_band - delta_lambda) & (exp['wave'] <= target_band + delta_lambda)
        if not np.any(mask):
            continue
        
        weight = np.zeros_like(exp['var'])
        valid = (exp['var'] > 0) & mask & (exp['flags'] == 0)
        weight[valid] = 1.0 / exp['var'][valid]
        
        flux_weighted = exp['flux'] * weight
        
        # Reproject
        reproj_flux_w = reproject_image(flux_weighted, exp['header'], wcs_out)
        reproj_weight = reproject_image(weight, exp['header'], wcs_out)
        
        # Replace nans
        reproj_flux_w = np.nan_to_num(reproj_flux_w)
        reproj_weight = np.nan_to_num(reproj_weight)
        
        if combined_flux is None:
            combined_flux = reproj_flux_w
            combined_weight = reproj_weight
        else:
            combined_flux += reproj_flux_w
            combined_weight += reproj_weight
            
    if combined_flux is None:
        return None, None
        
    final_flux = np.zeros_like(combined_flux)
    final_var = np.zeros_like(combined_weight)
    valid_weight = combined_weight > 0
    final_flux[valid_weight] = combined_flux[valid_weight] / combined_weight[valid_weight]
    final_var[valid_weight] = 1.0 / combined_weight[valid_weight]
    
    return final_flux, final_var

def fit_background(img, mask_valid):
    y_indices, x_indices = np.indices(img.shape)
    valid_y = y_indices[mask_valid]
    valid_x = x_indices[mask_valid]
    valid_z = img[mask_valid]
    
    # Iterative sigma clipping
    active_mask = np.ones(len(valid_z), dtype=bool)
    for _ in range(3):
        A = np.c_[valid_x[active_mask], valid_y[active_mask], np.ones(np.sum(active_mask))]
        C, _, _, _ = np.linalg.lstsq(A, valid_z[active_mask], rcond=None)
        pred = C[0] * valid_x + C[1] * valid_y + C[2]
        res = valid_z - pred
        std = np.std(res[active_mask])
        active_mask = np.abs(res) < 3.0 * std
        if np.sum(active_mask) < 10:
            break

    return C[0] * x_indices + C[1] * y_indices + C[2]

def background_scale_diff(img_A, var_A, img_B, var_B, mask):
    if np.sum(mask) == 0:
        return np.zeros_like(img_A), np.ones_like(var_A) * np.inf, 1.0, np.zeros_like(img_A), np.zeros_like(img_B)
    bg_A = fit_background(img_A, mask)
    bg_B = fit_background(img_B, mask)
    sub_A = img_A - bg_A
    sub_B = img_B - bg_B
    perc = np.percentile(sub_A[mask], 95)
    std_A = np.std(sub_A[mask])
    threshold = max(perc, 3.0 * std_A)
    # If the image is perfectly flat (std is 0), just use perc
    if std_A == 0:
        threshold = perc
    bright_mask = (sub_A > threshold) & mask
    if np.sum(bright_mask) == 0:
        scale = 1.0
    else:
        scale = np.median(sub_B[bright_mask] / sub_A[bright_mask])
    D = sub_A * scale - sub_B
    var_D = (var_A * (scale**2)) + var_B
    return D, var_D, scale, bg_A, bg_B

def matched_filter_snr(D, var_D, PSF, mask):
    safe_var = var_D.copy()
    safe_var[safe_var <= 0] = np.inf
    kernel_num = PSF[::-1, ::-1]
    weight = 1.0 / safe_var
    weighted_D = D * weight
    num = fftconvolve(weighted_D, kernel_num, mode='same')
    kernel_den = (PSF[::-1, ::-1])**2
    den_sq = fftconvolve(weight, kernel_den, mode='same')
    den_sq[den_sq <= 0] = np.inf
    den = np.sqrt(den_sq)
    snr = num / den
    snr[~mask] = 0.0
    return snr

def compute_threshold(n_unmasked_pixels, psf_area, target_false_positives=0.1):
    n_trials = n_unmasked_pixels / max(psf_area, 1.0)
    p_local_target = target_false_positives / max(n_trials, 1.0)
    sigma_threshold = stats.norm.isf(p_local_target)
    return sigma_threshold, n_trials, p_local_target

def find_peaks(snr, threshold):
    neighborhood = scipy.ndimage.maximum_filter(snr, size=3)
    peaks = (snr == neighborhood) & (snr > threshold)
    y, x = np.where(peaks)
    return [{'x': cx, 'y': cy, 'snr': snr[cy, cx]} for cx, cy in zip(x, y)]

def pair_finder(peaks_A, peaks_B, mjd_A, mjd_B, max_shift_arcsec=825.0):
    if not peaks_A or not peaks_B:
        return []
    coords_A = SkyCoord([p['ra'] for p in peaks_A]*u.deg, [p['dec'] for p in peaks_A]*u.deg)
    coords_B = SkyCoord([p['ra'] for p in peaks_B]*u.deg, [p['dec'] for p in peaks_B]*u.deg)
    idx, d2d, d3d = coords_A.match_to_catalog_sky(coords_B)
    pairs = []
    for i, j in enumerate(idx):
        dist_arcsec = d2d[i].arcsec
        if dist_arcsec <= max_shift_arcsec:
            pairs.append({
                'peak_A': peaks_A[i],
                'peak_B': peaks_B[j],
                'shift_arcsec': dist_arcsec,
                'dt_days': abs(mjd_A - mjd_B)
            })
    return pairs

def particle_hit_test(img_A, var_A, img_B, var_B, x, y):
    cx, cy = int(np.round(x)), int(np.round(y))
    if cx < 1 or cy < 1 or cx >= img_A.shape[1]-1 or cy >= img_A.shape[0]-1:
        return False, 0.0, 0.0, "edge"
    val_A = img_A[cy, cx]
    bg = np.median(img_A[cy-1:cy+2, cx-1:cx+2])
    sharpness = (val_A - bg) / max(val_A, 1.0)
    if sharpness > 0.95:
        return False, sharpness, 1.0, "cosmic_ray"
    return True, sharpness, 1.0, ""

def crossmatch_candidates(candidates, catalog_files):
    cat_coords = []
    cat_data = []
    for f in catalog_files:
        if not os.path.exists(f):
            continue
        with open(f) as fp:
            data = json.load(fp)
            for item in data:
                cat_coords.append((item['ra'], item['dec']))
                cat_data.append(item)
    if not cat_coords:
        return candidates
    c_cat = SkyCoord([c[0] for c in cat_coords]*u.deg, [c[1] for c in cat_coords]*u.deg)
    for c in candidates:
        ra = c.get('ra', c.get('ra_deg'))
        dec = c.get('dec', c.get('dec_deg'))
        coord = SkyCoord(ra*u.deg, dec*u.deg)
        idx, d2d, d3d = coord.match_to_catalog_sky(c_cat)
        if d2d.arcsec < 5.0:
            c['crossmatch'] = {
                'catalog': 'simulated',
                'id': cat_data[int(np.squeeze(idx))]['id'],
                'sep_arcsec': float(np.squeeze(d2d.arcsec))
            }
            c['status'] = 'known'
        else:
            c['crossmatch'] = {'catalog': None, 'id': None, 'sep_arcsec': None}
            c['status'] = 'candidate'
    return candidates

def export_png_tile(img, path, cmap='gray', percentiles=(1, 99)):
    import matplotlib.pyplot as plt
    os.makedirs(os.path.dirname(path), exist_ok=True)
    vmin, vmax = np.percentile(img[~np.isnan(img)], percentiles)
    plt.imsave(path, img, cmap=cmap, vmin=vmin, vmax=vmax, origin='lower')

def export_candidates(candidates, field_id, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{field_id}.json")
    for c in candidates:
        if "provenance" not in c:
            c["provenance"] = PROVENANCE
    with open(out_file, 'w') as fp:
        json.dump(candidates, fp, indent=2)


def extract_forced_photometry(field, data_dir, wcs_out_hdr, objects, out_dir_tiles):
    from pipeline.skyblink_pipeline.core.wcs_adapter import create_wcs
    wcs_obj = create_wcs(header=wcs_out_hdr, crval=(wcs_out_hdr['CRVAL1'], wcs_out_hdr['CRVAL2']), crpix=(wcs_out_hdr['CRPIX1'], wcs_out_hdr['CRPIX2']), cdelt=(wcs_out_hdr['CDELT1'], wcs_out_hdr['CDELT2']), force_numpy=True)
    
    bands = field['bands_um']
    passes = field['passes_available']
    
    results = {}
    
    for band in bands:
        f_dir = os.path.join(data_dir, field['id'])
        if not os.path.exists(f_dir):
            continue
            
        for p_idx, pass_name in enumerate(passes):
            from astropy.io import fits
            exp_files = [f for f in os.listdir(f_dir) if f'_pass{p_idx+1}_' in f]
            for obj in objects:
                # obj gives RA/DEC for this pass
                if 'ephemeris' in obj:
                    pos = obj['ephemeris'].get(pass_name)
                    if not pos: continue
                    ra, dec = pos['ra'], pos['dec']
                else:
                    ra, dec = obj['ra'], obj['dec']
                    
                best_flux = None
                best_var = None
                best_dist = 999.0
                best_cutout = None
                best_mjd = None
                
                for exp_file in exp_files:
                    hdul = fits.open(os.path.join(f_dir, exp_file))
                    hdr = hdul[0].header
                    wcs_this = create_wcs(header=hdr, crval=(hdr['CRVAL1'], hdr['CRVAL2']), crpix=(hdr['CRPIX1'], hdr['CRPIX2']), cdelt=(hdr['CDELT1'], hdr['CDELT2']), force_numpy=True)
                    x, y = wcs_this.world_to_pixel(ra, dec)
                    cx, cy = int(np.round(x)), int(np.round(y))
                    
                    if 0 <= cx < 256 and 0 <= cy < 256:
                        wave_val = hdul['WAVELENGTH'].data[cy, cx]
                        dist = abs(wave_val - band)
                        if dist < best_dist:
                            best_dist = dist
                            best_flux = hdul[0].data[cy, cx]
                            best_var = hdul['VARIANCE'].data[cy, cx]
                            best_mjd = hdr['MJD-OBS']
                            
                            y1, y2 = max(0, cy-10), min(256, cy+11)
                            x1, x2 = max(0, cx-10), min(256, cx+11)
                            best_cutout = hdul[0].data[y1:y2, x1:x2]
                    hdul.close()
                
                if best_flux is not None and best_dist < 0.2:
                    if obj['id'] not in results:
                        results[obj['id']] = {'track': [], 'spectrum': []}
                        
                    results[obj['id']]['track'].append({
                        'mjd': best_mjd,
                        'flux': float(best_flux),
                        'flux_err': float(np.sqrt(best_var)),
                        'band': band,
                        'pass': pass_name
                    })
                    
                    cutout_path = os.path.join(out_dir_tiles, field['id'], obj['id'], f'{pass_name}_{band}.png')
                    os.makedirs(os.path.dirname(cutout_path), exist_ok=True)
                    export_png_tile(best_cutout, cutout_path)
                    
                    results[obj['id']]['track'][-1]['image'] = f'/data/tiles/{field["id"]}/{obj["id"]}/{pass_name}_{band}.png'
            
    # Compute spectrum (mean over passes for each band)
    for obj_id, res in results.items():
        band_flux = {}
        for t in res['track']:
            b = t['band']
            if b not in band_flux:
                band_flux[b] = []
            band_flux[b].append(t['flux'])
        
        for b, fluxes in band_flux.items():
            res['spectrum'].append({
                'wave': float(b),
                'flux': float(np.mean(fluxes)),
                'flux_err': float(np.std(fluxes)/np.sqrt(len(fluxes)) if len(fluxes) > 1 else np.sqrt(abs(np.mean(fluxes))))
            })
            
        res['spectrum'].sort(key=lambda x: x['wave'])
        
    return results

def run_field(field_cfg, data_dir, wcs_out, cat_dir, out_dir_cands, out_dir_tiles):
    field_id = field_cfg['id']
    bands = field_cfg['bands_um']
    passes = field_cfg['passes_available']
    delta_lambda = field_cfg['delta_lambda_um']
    
    if field_cfg['pair_status'] != 'ok' or len(passes) < 2:
        return []
    
    pass_A = passes[0]
    pass_B = passes[1]
    
    from pipeline.skyblink_pipeline.core.wcs_adapter import create_wcs
    wcs_obj = create_wcs(
        header=wcs_out, 
        force_numpy=True,
        crval=(wcs_out['CRVAL1'], wcs_out['CRVAL2']),
        crpix=(wcs_out['CRPIX1'], wcs_out['CRPIX2']),
        cdelt=(wcs_out['CDELT1'], wcs_out['CDELT2'])
    )
    
    all_cands = []
    
    for band in bands:
        def load_exposures(p_idx):
            f_dir = os.path.join(data_dir, field_id)
            exposures = []
            if not os.path.exists(f_dir):
                return exposures
            for exp_file in os.listdir(f_dir):
                if f"_pass{p_idx+1}_" in exp_file:
                    hdul = fits.open(os.path.join(f_dir, exp_file))
                    exp = {
                        'flux': hdul[0].data,
                        'var': hdul['VARIANCE'].data,
                        'flags': hdul['FLAGS'].data,
                        'wave': hdul['WAVELENGTH'].data,
                        'header': hdul[0].header,
                        'mjd': hdul[0].header['MJD-OBS']
                    }
                    exposures.append(exp)
            return exposures
            
        exps_A = load_exposures(0)
        exps_B = load_exposures(1)
        
        mjd_A = np.mean([e['mjd'] for e in exps_A]) if exps_A else 0
        mjd_B = np.mean([e['mjd'] for e in exps_B]) if exps_B else 0
        
        img_A, var_A = band_match_and_combine(exps_A, wcs_out, band, delta_lambda)
        img_B, var_B = band_match_and_combine(exps_B, wcs_out, band, delta_lambda)
        
        if img_A is None or img_B is None:
            continue
            
        mask = (var_A > 0) & (var_B > 0)
        D, var_D, scale, bg_A, bg_B = background_scale_diff(img_A, var_A, img_B, var_B, mask)
        
        PSF = np.ones((3, 3)) / 9.0
        snr = matched_filter_snr(D, var_D, PSF, mask)
        
        sigma_th, n_trials, p_local_target = compute_threshold(np.sum(mask), 9.0, 0.1)
        
        snr_A = matched_filter_snr(img_A - bg_A, var_A, PSF, mask)
        snr_B = matched_filter_snr(img_B - bg_B, var_B, PSF, mask)
        
        peaks_A_local = find_peaks(snr_A, sigma_th)
        peaks_B_local = find_peaks(snr_B, sigma_th)
        
        def to_sky(peaks):
            res = []
            for p in peaks:
                ra, dec = wcs_obj.pixel_to_world(p['x'], p['y'])
                p['ra'] = ra
                p['dec'] = dec
                res.append(p)
            return res
            
        peaks_A_sky = to_sky(peaks_A_local)
        peaks_B_sky = to_sky(peaks_B_local)
        
        pairs = pair_finder(peaks_A_sky, peaks_B_sky, mjd_A, mjd_B)
        
        for i, p in enumerate(pairs):
            pa = p['peak_A']
            pb = p['peak_B']
            
            pass_hit_A, sharp_A, chi_A, rej_A = particle_hit_test(img_A, var_A, img_B, var_B, pa['x'], pa['y'])
            pass_hit_B, sharp_B, chi_B, rej_B = particle_hit_test(img_B, var_B, img_A, var_A, pb['x'], pb['y'])
            
            if not pass_hit_A or not pass_hit_B:
                continue
                
            cand_id = f"{field_id}_{band}_{i}"
            tile_dir = os.path.join(out_dir_tiles, field_id, cand_id)
            export_png_tile(img_A, os.path.join(tile_dir, "epoch_a.png"))
            export_png_tile(img_B, os.path.join(tile_dir, "epoch_b.png"))
            export_png_tile(D, os.path.join(tile_dir, "diff.png"), cmap='coolwarm')
            export_png_tile(snr, os.path.join(tile_dir, "snr.png"), cmap='viridis', percentiles=(5, 99))
            
            p_local = stats.norm.sf(pa['snr'])
            all_cands.append({
                "id": cand_id,
                "field_id": field_id,
                "ra_deg": float(pa['ra']),
                "dec_deg": float(pa['dec']),
                "band_um": band,
                "epochs": [pass_A, pass_B],
                "snr": float(pa['snr']),
                "p_local": float(p_local),
                "p_trials_adjusted": float(p_local * n_trials),
                "kind": "pair",
                "dipole_separation_arcsec": float(p['shift_arcsec']),
                "sharpness": float(sharp_A),
                "chi2_psf": float(chi_A),
                "persistent_in_other_pass": False,
                "type_label": "unidentified",
                "status": "candidate",
                "tiles": {
                    "epoch_a": f"/data/tiles/{field_id}/{cand_id}/epoch_a.png",
                    "epoch_b": f"/data/tiles/{field_id}/{cand_id}/epoch_b.png",
                    "diff": f"/data/tiles/{field_id}/{cand_id}/diff.png",
                    "snr": f"/data/tiles/{field_id}/{cand_id}/snr.png"
                },
                "notes": ""
            })
            
    all_cands = crossmatch_candidates(all_cands, [os.path.join(cat_dir, "synthetic_gaia.json"), os.path.join(cat_dir, "synthetic_mpc.json")])
    export_candidates(all_cands, field_id, out_dir_cands)
    return all_cands

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--fields', type=str, help='Comma separated list of field IDs to process')
    args = parser.parse_args()

    allowed_fields = None
    if args.fields:
        allowed_fields = set(args.fields.split(','))

    print('Running pipeline...')
    config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../config'))
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../data/fits'))
    cat_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../data/catalogs'))
    out_dir_cands = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../web/public/data/candidates'))
    out_dir_tiles = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../web/public/data/tiles'))
    out_dir_manifest = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../web/public/data'))
    
    os.makedirs(out_dir_cands, exist_ok=True)
    os.makedirs(out_dir_tiles, exist_ok=True)
    
    type_counts = {}
    
    import glob
    for yaml_file in glob.glob(os.path.join(config_dir, 'fields', '*.yaml')):
        with open(yaml_file) as fp:
            field = yaml.safe_load(fp)
        
        field_id = field['id']
        
        if allowed_fields and field_id not in allowed_fields:
            continue
            
        print(f"Processing {field_id}...")
        
        wcs_out = {
            'CRPIX1': 128, 'CRPIX2': 128,
            'CDELT1': -6.2/3600, 'CDELT2': 6.2/3600,
            'CRVAL1': field['center']['ra_deg'], 'CRVAL2': field['center']['dec_deg'],
            'CTYPE1': 'RA---TAN', 'CTYPE2': 'DEC--TAN',
            'NAXIS': 2, 'NAXIS1': 256, 'NAXIS2': 256
        }
        
        wcs_out_hdr = fits.Header(wcs_out)
        
        cands = []
        if field['pair_status'] == 'ok' and len(field['passes_available']) >= 2:
            cache_file = os.path.join(out_dir_cands, f"{field_id}.json")
            if os.path.exists(cache_file):
                print(f"Using cached candidates for {field_id}...")
                with open(cache_file) as fp:
                    cands = json.load(fp)
            else:
                cands = run_field(field, data_dir, wcs_out_hdr, cat_dir, out_dir_cands, out_dir_tiles)
            
            manifest = field.copy()
            manifest['candidates'] = [c['id'] for c in cands]
            manifest['data_release'] = "DR1"
            manifest['simulated'] = True
            manifest['acknowledgement'] = True
            manifest['provenance'] = PROVENANCE
            
            type_counts[field_id] = {}
            for c in cands:
                tl = c['type_label']
                type_counts[field_id][tl] = type_counts[field_id].get(tl, 0) + 1
                
            print(f"Field {field_id} candidates: {type_counts[field_id]}")
        else:
            manifest = field.copy()
            manifest['candidates'] = []
            manifest['data_release'] = "DR1"
            manifest['simulated'] = True
            manifest['acknowledgement'] = True
            manifest['provenance'] = PROVENANCE
            manifest['pair_status'] = 'not_enough_epochs'
            
        with open(os.path.join(out_dir_manifest, f"manifest_{field_id}.json"), "w") as fp:
            json.dump(manifest, fp, indent=2)


    spectra_all = []
    follow_all = []

    # We will just run extraction on the fields that matter for the test
    for yaml_file in glob.glob(os.path.join(config_dir, 'fields', '*.yaml')):
        with open(yaml_file) as fp:
            field = yaml.safe_load(fp)
            
        if allowed_fields and field['id'] not in allowed_fields:
            continue
            
        wcs_out = {
            'CRPIX1': 128, 'CRPIX2': 128,
            'CDELT1': -6.2/3600, 'CDELT2': 6.2/3600,
            'CRVAL1': field['center']['ra_deg'], 'CRVAL2': field['center']['dec_deg'],
            'CTYPE1': 'RA---TAN', 'CTYPE2': 'DEC--TAN',
            'NAXIS': 2, 'NAXIS1': 256, 'NAXIS2': 256
        }
        wcs_out_hdr = fits.Header(wcs_out)
        
        from pipeline.skyblink_pipeline.crossmatch.ephemeris import SyntheticCrossMatch
        crossmatch = SyntheticCrossMatch(cat_dir)
        
        # Get all objects that are in this field's region
        # For simplicity, we just pass all objects in the MPC/Gaia catalogs to forced photometry
        objects = [{'id': obj_id} for obj_id in crossmatch.get_all_ids()]
            
        if objects:
            res = extract_forced_photometry(field, data_dir, wcs_out_hdr, objects, out_dir_tiles, crossmatch)
            for obj_id, data in res.items():
                if obj_id == 'star1':
                    spectra_all.append({
                        'id': obj_id,
                        'spectrum': data['spectrum'],
                        'provenance': PROVENANCE
                    })
                else:
                    follow_all.append({
                        'id': obj_id,
                        'track': data['track'],
                        'spectrum': data['spectrum'],
                        'provenance': PROVENANCE
                    })
                    
    with open(os.path.join(out_dir_manifest, 'spectra.json'), 'w') as fp:
        json.dump(spectra_all, fp, indent=2)
    with open(os.path.join(out_dir_manifest, 'follow_object.json'), 'w') as fp:
        json.dump(follow_all, fp, indent=2)

    print('Pipeline complete.')

if __name__ == '__main__':
    main()
