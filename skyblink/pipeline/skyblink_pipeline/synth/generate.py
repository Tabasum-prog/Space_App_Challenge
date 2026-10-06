import os
import yaml
import numpy as np
from astropy.io import fits
import json
import scipy.stats as stats

def set_seed(seed=42):
    np.random.seed(seed)

def read_yaml_fields(config_dir):
    fields = []
    fields_dir = os.path.join(config_dir, "fields")
    for f in os.listdir(fields_dir):
        if f.endswith(".yaml"):
            with open(os.path.join(fields_dir, f)) as yaml_file:
                field = yaml.safe_load(yaml_file)
                field["passes"] = len(field["passes_available"])
                fields.append(field)
    return fields

def make_fits(filename, flux, variance, flags, header_dict, wavelength_map):
    hdr = fits.Header()
    for k, v in header_dict.items():
        hdr[k] = v
    hdu_flux = fits.PrimaryHDU(data=flux, header=hdr)
    hdu_var = fits.ImageHDU(data=variance, name="VARIANCE")
    hdu_flags = fits.ImageHDU(data=flags, name="FLAGS")
    hdu_wave = fits.ImageHDU(data=wavelength_map, name="WAVELENGTH")
    hdul = fits.HDUList([hdu_flux, hdu_var, hdu_flags, hdu_wave])
    hdul.writeto(filename, overwrite=True)

def generate_exposure(field, pass_idx, exp_idx, out_dir):
    shape = (256, 256)
    
    base_wave = -1.0 + (exp_idx * 0.125) 
    x = np.arange(shape[1])
    wave_1d = base_wave + x * (4.0 / 256.0) 
    wavelength_map = np.tile(wave_1d, (shape[0], 1))
    
    zodi = np.linspace(10, 20, shape[1])
    flux = np.tile(zodi, (shape[0], 1))
    flux = np.random.poisson(flux).astype(float)
    flux += np.random.normal(0, 5.0, shape) # Reduced noise
    
    variance = np.full(shape, 5.0**2) + np.tile(zodi, (shape[0], 1))
    flags = np.zeros(shape, dtype=np.int32)
    
    hot_x = np.random.randint(0, shape[1], 10)
    hot_y = np.random.randint(0, shape[0], 10)
    flux[hot_y, hot_x] += 1000
    flags[hot_y, hot_x] |= 1 
    
    for _ in range(5):
        cx, cy = np.random.randint(0, shape[1]), np.random.randint(0, shape[0])
        deposit = float(stats.levy.rvs(loc=100, scale=50))
        if deposit > 10000: deposit = 10000.0
        if deposit < 0: deposit = 0.0
        flux[cy, cx] += deposit
    
    dither_x = np.random.uniform(-5, 5)
    dither_y = np.random.uniform(-5, 5)
    
    # Base CRPIX considering dither
    crpix1 = 128 + dither_x
    crpix2 = 128 + dither_y
    cdelt = 6.2/3600
    
    # Target positions based on field ID
    mjd = 60000.0 + pass_idx * 180.0 + exp_idx * 0.01
    
    if field['id'] == 'F_MOVER':
        # Parallax-like mover: shifts in RA in pass 2
        shift_pix = 10 if pass_idx == 1 else 0
        cy_ast = int(np.round(128 + dither_y))
        cx_ast = int(np.round(128 + dither_x + shift_pix))
        if 0 <= cy_ast < 256 and 0 <= cx_ast < 256:
            flux[cy_ast, cx_ast] += 200.0
            
        # fixed source
        cy_star = int(np.round(128 + dither_y))
        cx_star = int(np.round(128 + dither_x))
        if 0 <= cy_star < 256 and 0 <= cx_star < 256:
            flux[cy_star, cx_star] += 300.0
        
    if field['id'] == 'F_COMET':
        # Comet moving 5 pixels per pass
        cy = int(np.round(128 + dither_y + pass_idx * 5))
        cx = int(np.round(128 + dither_x))
        if 0 <= cy < 256 and 0 <= cx < 256:
            # Comet has a bump near 4.27 um
            # wavelength_map[cy, cx] is the wavelength
            band_wave = wavelength_map[cy, cx]
            bump = 0.0
            if abs(band_wave - 4.27) < 0.2:
                bump = 500.0 # SNR > 3 (noise is 5)
            flux[cy, cx] += 100.0 + bump

    header = {
        "CRPIX1": crpix1,
        "CRPIX2": crpix2,
        "CDELT1": -cdelt,
        "CDELT2": cdelt,
        "CRVAL1": field["center"]["ra_deg"],
        "CRVAL2": field["center"]["dec_deg"],
        "CTYPE1": "RA---TAN",
        "CTYPE2": "DEC--TAN",
        "MJD-OBS": mjd
    }
    
    filename = os.path.join(out_dir, f"{field['id']}_pass{pass_idx+1}_exp{exp_idx}.fits")
    make_fits(filename, flux, variance, flags, header, wavelength_map)
    return filename

def generate_mock_data():
    set_seed(42)
    config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../config"))
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/fits"))
    os.makedirs(data_dir, exist_ok=True)
    
    fields = read_yaml_fields(config_dir)
    
    print("Generating FITS files (41 exposures * passes per field)...")
    for f in fields:
        f_dir = os.path.join(data_dir, f["id"])
        os.makedirs(f_dir, exist_ok=True)
        count = 0
        for p in range(f["passes"]):
            for exp in range(41):
                generate_exposure(f, p, exp, f_dir)
                count += 1
        print(f"| {f['id']:<15} | {count} files generated |")
                
    cat_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/catalogs"))
    os.makedirs(cat_dir, exist_ok=True)
    with open(os.path.join(cat_dir, "synthetic_gaia.json"), "w") as out:
        json.dump([{"id": "star1", "ra": 10.0, "dec": 20.0, "pmra": 0.1}], out)
    with open(os.path.join(cat_dir, "synthetic_mpc.json"), "w") as out:
        json.dump([
            {"id": "ast1", "ra": 10.0, "dec": 20.0},
            {"id": "comet1", "ra": 30.0, "dec": 40.0}
        ], out)
        
    print("Synthetic data generated successfully.")

if __name__ == "__main__":
    generate_mock_data()
