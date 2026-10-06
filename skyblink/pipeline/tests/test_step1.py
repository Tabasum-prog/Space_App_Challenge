import numpy as np
from pipeline.skyblink_pipeline.core.run import band_match_and_combine

def test_exposures_outside_tolerance_never_contribute():
    target_band = 1.25
    delta = 0.02
    
    exp1 = {
        'flux': np.full((10, 10), 100.0),
        'var': np.full((10, 10), 2.0),
        'wave': np.full((10, 10), 1.25)
    }
    exp2 = {
        'flux': np.full((10, 10), 999.0),
        'var': np.full((10, 10), 1.0),
        'wave': np.full((10, 10), 2.0)
    }
    
    wcs_out = {'CRVAL1': 0, 'CRVAL2': 0, 'CRPIX1': 5, 'CRPIX2': 5, 'CDELT1': 1, 'CDELT2': 1, 'CTYPE1': 'RA---TAN', 'CTYPE2': 'DEC--TAN', 'NAXIS': 2, 'NAXIS1': 10, 'NAXIS2': 10}
    exp1['header'] = wcs_out
    exp2['header'] = wcs_out
    exp1['flags'] = np.zeros((10, 10), dtype=int)
    exp2['flags'] = np.zeros((10, 10), dtype=int)
    flux, var = band_match_and_combine([exp1, exp2], wcs_out, target_band, delta)
    assert np.allclose(flux, 100.0)
    assert np.allclose(var, 2.0)

def test_combined_variance_analytic():
    target_band = 1.25
    delta = 0.02
    
    exp1 = {
        'flux': np.full((10, 10), 100.0),
        'var': np.full((10, 10), 4.0),
        'wave': np.full((10, 10), 1.25)
    }
    exp2 = {
        'flux': np.full((10, 10), 100.0),
        'var': np.full((10, 10), 4.0),
        'wave': np.full((10, 10), 1.25)
    }
    
    wcs_out = {'CRVAL1': 0, 'CRVAL2': 0, 'CRPIX1': 5, 'CRPIX2': 5, 'CDELT1': 1, 'CDELT2': 1, 'CTYPE1': 'RA---TAN', 'CTYPE2': 'DEC--TAN', 'NAXIS': 2, 'NAXIS1': 10, 'NAXIS2': 10}
    exp1['header'] = wcs_out
    exp2['header'] = wcs_out
    exp1['flags'] = np.zeros((10, 10), dtype=int)
    exp2['flags'] = np.zeros((10, 10), dtype=int)
    flux, var = band_match_and_combine([exp1, exp2], wcs_out, target_band, delta)
    assert np.allclose(flux, 100.0)
    assert np.allclose(var, 2.0)
