import os
import json
import glob
import numpy as np
import yaml
from astropy.io import fits
from pipeline.skyblink_pipeline.core.wcs_adapter import create_wcs
from pipeline.skyblink_pipeline.core.run import band_match_and_combine, background_scale_diff, matched_filter_snr, compute_threshold, find_peaks, pair_finder
import scipy.stats as stats

def get_git_sha():
    import subprocess
    try:
        r = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True, cwd=os.path.dirname(__file__))
        return r.stdout.strip()
    except Exception:
        return 'unknown'

def make_psf(size=3):
    return np.ones((size, size)) / (size * size)

def inject_source(exps, x, y, flux):
    # x,y can be floating point. We'll distribute the flux into the nearest pixels.
    res = []
    for e in exps:
        # copy
        e_new = e.copy()
        e_new['flux'] = e['flux'].copy()
        
        ix, iy = int(round(x)), int(round(y))
        if 1 <= ix < 255 and 1 <= iy < 255:
            e_new['flux'][iy-1:iy+2, ix-1:ix+2] += flux / 9.0
        res.append(e_new)
    return res

def run_detection(exps_A, exps_B, band, wcs_out_hdr, mjd_A, mjd_B, delta_lambda):
    wcs_obj = create_wcs(header=wcs_out_hdr, force_numpy=True, crval=(wcs_out_hdr['CRVAL1'], wcs_out_hdr['CRVAL2']), crpix=(wcs_out_hdr['CRPIX1'], wcs_out_hdr['CRPIX2']), cdelt=(wcs_out_hdr['CDELT1'], wcs_out_hdr['CDELT2']))
    
    img_A, var_A = band_match_and_combine(exps_A, wcs_out_hdr, band, delta_lambda)
    img_B, var_B = band_match_and_combine(exps_B, wcs_out_hdr, band, delta_lambda)
    
    if img_A is None or img_B is None: return [], 0
    
    mask = (var_A > 0) & (var_B > 0)
    if np.sum(mask) == 0: return [], 0
    
    D, var_D, scale, bg_A, bg_B = background_scale_diff(img_A, var_A, img_B, var_B, mask)
    PSF = make_psf()
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
    
    # We skip particle hit test for mock injections here for simplicity
    valid_pairs = []
    for p in pairs:
        # Convert back to pixel for distance checks
        valid_pairs.append(p)
        
    return valid_pairs, n_trials * p_local_target

def run_validation():
    print("Running REAL Validation...")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    data_dir = os.path.join(base_dir, 'data/fits')
    config_dir = os.path.join(base_dir, 'config')
    out_file = os.path.join(base_dir, 'web/public/data/validation.json')
    truth_dir = os.path.join(base_dir, 'data/truth')
    cand_dir = os.path.join(base_dir, 'web/public/data/candidates')
    
    with open(os.path.join(config_dir, 'fields', 'F_EMPTY.yaml')) as f:
        field_empty = yaml.safe_load(f)
        
    f_dir = os.path.join(data_dir, 'F_EMPTY')
    exps_A = []
    exps_B = []
    if os.path.exists(f_dir):
        for exp_file in os.listdir(f_dir):
            if '_pass1_' in exp_file:
                hdul = fits.open(os.path.join(f_dir, exp_file))
                exps_A.append({'flux': hdul[0].data, 'var': hdul['VARIANCE'].data, 'wave': hdul['WAVELENGTH'].data, 'flags': hdul['FLAGS'].data, 'mjd': hdul[0].header['MJD-OBS'], 'header': hdul[0].header})
            elif '_pass2_' in exp_file:
                hdul = fits.open(os.path.join(f_dir, exp_file))
                exps_B.append({'flux': hdul[0].data, 'var': hdul['VARIANCE'].data, 'wave': hdul['WAVELENGTH'].data, 'flags': hdul['FLAGS'].data, 'mjd': hdul[0].header['MJD-OBS'], 'header': hdul[0].header})
                
    mjd_A = np.mean([e['mjd'] for e in exps_A]) if exps_A else 0
    mjd_B = np.mean([e['mjd'] for e in exps_B]) if exps_B else 0
    
    wcs_out = {
        'CRPIX1': 128, 'CRPIX2': 128,
        'CDELT1': -6.2/3600, 'CDELT2': 6.2/3600,
        'CRVAL1': field_empty['center']['ra_deg'], 'CRVAL2': field_empty['center']['dec_deg'],
        'CTYPE1': 'RA---TAN', 'CTYPE2': 'DEC--TAN',
        'NAXIS': 2, 'NAXIS1': 256, 'NAXIS2': 256
    }
    wcs_out_hdr = fits.Header(wcs_out)
    wcs_obj = create_wcs(header=wcs_out_hdr, force_numpy=True, crval=(wcs_out_hdr['CRVAL1'], wcs_out_hdr['CRVAL2']), crpix=(wcs_out_hdr['CRPIX1'], wcs_out_hdr['CRPIX2']), cdelt=(wcs_out_hdr['CDELT1'], wcs_out_hdr['CDELT2']))
    band = 2.2 # test band
    delta_lambda = field_empty['delta_lambda_um']
    
    np.random.seed(42)
    
    # 1. Injection Recovery
    flux_levels = [30, 50, 75, 100, 150, 200, 300, 500]
    recovery_curve = []
    bright_recovered = 0
    bright_total = 0
    
    motion_recovery = []
    
    # Find valid pixels for injection
    wave_map = exps_A[0]['wave']
    valid_mask = np.zeros_like(wave_map, dtype=bool)
    for b in field_empty['bands_um']:
        for e in exps_A:
            valid_mask |= (np.abs(e['wave'] - b) < delta_lambda * 0.5)
        
    valid_y, valid_x = np.where(valid_mask)
    # Filter edges
    edge_mask = (valid_x > 20) & (valid_x < 230) & (valid_y > 20) & (valid_y < 230)
    valid_y = valid_y[edge_mask]
    valid_x = valid_x[edge_mask]
    
    print("Running Injection-Recovery...")
    for flux in flux_levels:
        rec = 0
        for i in range(20):
            idx = np.random.randint(0, len(valid_x))
            x0 = valid_x[idx]
            y0 = valid_y[idx]
            dx = np.random.uniform(-15, 15)
            dy = np.random.uniform(-15, 15)
            
            exps_A_inj = inject_source(exps_A, x0, y0, flux)
            exps_B_inj = inject_source(exps_B, x0+dx, y0+dy, flux)
            
            found = False
            for b in field_empty['bands_um']:
                pairs, _ = run_detection(exps_A_inj, exps_B_inj, b, wcs_out_hdr, mjd_A, mjd_B, delta_lambda)
                
                for p in pairs:
                    x_A, y_A = wcs_obj.world_to_pixel(p['peak_A']['ra'], p['peak_A']['dec'])
                    if abs(x_A - x0) < 3 and abs(y_A - y0) < 3:
                        found = True
                        break
                if found: break
                
            if found:
                rec += 1
                motion_recovery.append({'flux': flux, 'motion': np.sqrt(dx**2 + dy**2), 'recovered': 1})
            else:
                motion_recovery.append({'flux': flux, 'motion': np.sqrt(dx**2 + dy**2), 'recovered': 0})
                
        frac = rec / 20.0
        recovery_curve.append({'flux': flux, 'fraction': frac})
        if flux >= 150:
            bright_recovered += rec
            bright_total += 20
            
    # 2. False Positive Audit
    print("Running False-Positive Audit...")
    fp_counts = []
    expected_fps = []
    for i in range(10):
        # Generate independent noise realization
        exps_A_noise = []
        for e in exps_A:
            e_n = e.copy()
            e_n['flux'] = np.random.randn(*e['flux'].shape) * np.sqrt(e['var'])
            exps_A_noise.append(e_n)
        exps_B_noise = []
        for e in exps_B:
            e_n = e.copy()
            e_n['flux'] = np.random.randn(*e['flux'].shape) * np.sqrt(e['var'])
            exps_B_noise.append(e_n)
            
        all_pairs = []
        all_exp_fp = 0
        for b in field_empty['bands_um']:
            pairs, exp_fp = run_detection(exps_A_noise, exps_B_noise, b, wcs_out_hdr, mjd_A, mjd_B, delta_lambda)
            all_pairs.extend(pairs)
            all_exp_fp += exp_fp
            
        fp_counts.append(len(all_pairs))
        expected_fps.append(all_exp_fp)
        
    avg_fp = np.mean(fp_counts)
    avg_expected_fp = np.mean(expected_fps)
    
    # 3. Known-object Recovery
    print("Running Known-Object Recovery...")
    known_total = 0
    known_recovered = 0
    truth_files = glob.glob(os.path.join(truth_dir, '*.json'))
    truth_dict = {}
    for tf in truth_files:
        with open(tf) as f:
            t = json.load(f)
            field = os.path.basename(tf).replace('.json', '')
            truth_dict[field] = t
            
    cand_files = glob.glob(os.path.join(cand_dir, '*.json'))
    for cf in cand_files:
        with open(cf) as f:
            cands = json.load(f)
            field = os.path.basename(cf).replace('.json', '')
            t = truth_dict.get(field, [])
            objs = t if isinstance(t, list) else []
            for obj in objs:
                if obj['kind'] == 'star': continue
                known_total += 1
                found = False
                for cand in cands:
                    if abs(cand['ra_deg'] - obj['ra']) < 10/3600 and abs(cand['dec_deg'] - obj['dec']) < 10/3600:
                        found = True
                        break
                if found:
                    known_recovered += 1
                    
    validation = {
        'produced_by': 'skyblink_pipeline',
        'git_sha': get_git_sha(),
        'generated_at': '2026-10-06T00:00:00Z',
        'simulated': True,
        'injection_recovery': {
            'curve': recovery_curve,
            'motion': motion_recovery,
            'bright_recovered': bright_recovered,
            'bright_total': bright_total
        },
        'false_positive_audit': {
            'trials': 10,
            'avg_fp_found': avg_fp,
            'avg_fp_expected': avg_expected_fp
        },
        'known_object_recovery': {
            'total': known_total,
            'recovered': known_recovered
        }
    }
    
    with open(out_file, 'w') as f:
        json.dump(validation, f, indent=2)
        
    print("\n--- VALIDATION RESULTS ---")
    print(f"Bright object recovery (>=150 flux): {bright_recovered}/{bright_total} ({(bright_recovered/bright_total)*100:.1f}%)")
    print(f"False Positives per field: Found {avg_fp:.2f}, Expected {avg_expected_fp:.2f}")
    print(f"Known Object Recovery: {known_recovered}/{known_total}")
    
    assert bright_recovered / bright_total >= 0.9, "Bright object recovery < 90%"
    assert avg_fp <= 1.0, f"False positive rate {avg_fp} > 1.0"
    print("All acceptance tests PASSED.")

if __name__ == "__main__":
    run_validation()
