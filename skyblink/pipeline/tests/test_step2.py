import numpy as np
from pipeline.skyblink_pipeline.core.run import background_scale_diff

def test_recover_background_gradient():
    shape = (100, 100)
    y, x = np.indices(shape)
    
    bg_A = 0.5 * x + 0.2 * y + 10.0
    img_A = bg_A.copy()
    
    bg_B = 0.1 * x + 0.8 * y + 5.0
    img_B = bg_B.copy()
    
    mask = np.ones(shape, dtype=bool)
    var_A = np.ones(shape)
    var_B = np.ones(shape)
    
    D, var_D, scale, fit_bg_A, fit_bg_B = background_scale_diff(img_A, var_A, img_B, var_B, mask)
    
    assert np.allclose(bg_A, fit_bg_A)
    assert np.allclose(bg_B, fit_bg_B)

def test_recover_known_scale_factor():
    shape = (100, 100)
    img_A = np.full(shape, 10.0)
    img_B = np.full(shape, 10.0)
    
    img_A[50, 50] = 1000.0 + 10.0
    img_B[50, 50] = (1000.0 * 2.5) + 10.0
    
    mask = np.ones(shape, dtype=bool)
    var = np.ones(shape)
    
    D, var_D, scale, fit_bg_A, fit_bg_B = background_scale_diff(img_A, var, img_B, var, mask)
    
    assert abs(scale - 2.5) / 2.5 < 0.02
