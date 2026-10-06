import { describe, it, expect } from 'vitest';
import { diatomicVibration, wienPeak, dimming, parallax } from '../src/lib/physics';
import fs from 'fs';
import path from 'path';

describe('Physics Modules', () => {
    it('matches golden.json values', () => {
        const goldenPath = path.resolve(__dirname, '../../physics/golden.json');
        const golden = JSON.parse(fs.readFileSync(goldenPath, 'utf8'));
        
        const co_k = golden.spectroscopy.co_k_N_m;
        const nu_12_16 = diatomicVibration(co_k, 12, 15.9949);
        expect(Math.abs(nu_12_16 - golden.spectroscopy.co_12_16_wavenumber_cm_1)).toBeLessThan(1.0);
        
        const wave_12_16 = 10000.0 / nu_12_16;
        expect(Math.abs(wave_12_16 - golden.spectroscopy.co_12_16_wavelength_um)).toBeLessThan(0.01);
        
        const nu_13_16 = diatomicVibration(co_k, 13.00335, 15.9949);
        const wave_13_16 = 10000.0 / nu_13_16;
        expect(Math.abs(wave_13_16 - golden.spectroscopy.co_13_16_wavelength_um)).toBeLessThan(0.02);
        
        expect(Math.abs(wienPeak(golden.wiens_law.temp_k) - golden.wiens_law.peak_wavelength_um)).toBeLessThan(0.1);
        expect(Math.abs(dimming(30, 500) - golden.planet_x.dimming_30_to_500_au)).toBeLessThan(1.0);
        expect(Math.abs(parallax(500) - 825.0)).toBeLessThan(8.25);
        expect(Math.abs(golden.planet_x.parallax_shift_500_au_arcsec - 825.0)).toBeLessThan(8.25);
    });
});
