import os
from astropy.io import fits
import numpy as np

f_dir = r"d:\Space App Challenge\skyblink\data\fits\F_COMET"
for p_idx in range(3):
    print(f"Pass {p_idx+1}:")
    exp_files = [f for f in os.listdir(f_dir) if f'_pass{p_idx+1}_' in f]
    for exp_file in exp_files:
        hdul = fits.open(os.path.join(f_dir, exp_file))
        cy = 128 + p_idx * 5
        cx = 128
        wave_val = hdul['WAVELENGTH'].data[cy, cx]
        flux = hdul[0].data[cy, cx]
        dist = abs(wave_val - 4.27)
        if dist < 0.1:
            print(f"  File {exp_file} - wave: {wave_val:.3f}, dist: {dist:.3f}, flux: {flux:.3f}")
        hdul.close()
