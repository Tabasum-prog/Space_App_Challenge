import numpy as np
import scipy.stats as stats
from pipeline.skyblink_pipeline.core.run import matched_filter_snr, compute_threshold

def test_matched_filter_snr_injected():
    shape = (50, 50)
    D = np.zeros(shape)
    var_D = np.full(shape, 2.0**2)
    mask = np.ones(shape, dtype=bool)
    
    PSF = np.array([[0.1, 0.2, 0.1],
                    [0.2, 0.8, 0.2],
                    [0.1, 0.2, 0.1]])
    PSF /= np.sum(PSF)
    
    flux = 100.0
    center = (25, 25)
    D[center[0]-1:center[0]+2, center[1]-1:center[1]+2] += flux * PSF
    
    snr_map = matched_filter_snr(D, var_D, PSF, mask)
    
    psf_sq_sum = np.sum(PSF**2)
    analytic_snr = flux * np.sqrt(psf_sq_sum / 4.0)
    
    measured_snr = snr_map[center]
    
    assert abs(measured_snr - analytic_snr) / analytic_snr < 0.10

def test_threshold_formulas():
    psf_area = 5.0
    n_unmasked = 5e6
    sigma_th, n_trials, p_local = compute_threshold(n_unmasked, psf_area, target_false_positives=0.29)
    
    assert abs(n_trials - 1e6) < 1.0
    assert abs(p_local - 2.9e-7) < 1e-8
    assert abs(sigma_th - 5.0) < 0.1
