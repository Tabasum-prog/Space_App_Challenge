from pipeline.skyblink_pipeline.core.run import pair_finder, particle_hit_test
import numpy as np

def test_pair_finder_rejection():
    peaks_A = [{'ra': 10.0, 'dec': 20.0}]
    
    # 900 arcsec shift (rejected)
    shift_deg = 900.0 / 3600.0
    peaks_B_reject = [{'ra': 10.0, 'dec': 20.0 + shift_deg}]
    pairs1 = pair_finder(peaks_A, peaks_B_reject, 60000.0, 60180.0, max_shift_arcsec=825.0)
    assert len(pairs1) == 0
    
    # 800 arcsec shift (kept)
    shift_deg2 = 800.0 / 3600.0
    peaks_B_keep = [{'ra': 10.0, 'dec': 20.0 + shift_deg2}]
    pairs2 = pair_finder(peaks_A, peaks_B_keep, 60000.0, 60180.0, max_shift_arcsec=825.0)
    assert len(pairs2) == 1
    assert abs(pairs2[0]['shift_arcsec'] - 800.0) < 1.0

def test_dipole():
    peaks_A = [{'ra': 10.0, 'dec': 20.0}]
    peaks_B = [{'ra': 10.0, 'dec': 20.0 + 1.0/3600.0}]
    pairs = pair_finder(peaks_A, peaks_B, 60000.0, 60000.1)
    assert len(pairs) == 1

def test_separated_pair():
    peaks_A = [{'ra': 10.0, 'dec': 20.0}]
    peaks_B = [{'ra': 10.0, 'dec': 20.0 + 500.0/3600.0}]
    pairs = pair_finder(peaks_A, peaks_B, 60000.0, 60180.0)
    assert len(pairs) == 1

def test_appeared():
    peaks_A = []
    peaks_B = [{'ra': 10.0, 'dec': 20.0}]
    pairs = pair_finder(peaks_A, peaks_B, 60000.0, 60180.0)
    assert len(pairs) == 0

def test_disappeared():
    peaks_A = [{'ra': 10.0, 'dec': 20.0}]
    peaks_B = []
    pairs = pair_finder(peaks_A, peaks_B, 60000.0, 60180.0)
    assert len(pairs) == 0

def test_cosmic_ray_rejection():
    img_A = np.zeros((10, 10))
    img_A[5, 5] = 1000.0
    var_A = np.ones((10, 10))
    img_B = np.zeros((10, 10))
    var_B = np.ones((10, 10))
    
    passed, sharpness, chi2, reason = particle_hit_test(img_A, var_A, img_B, var_B, 5, 5)
    assert not passed
    assert reason == "cosmic_ray"
