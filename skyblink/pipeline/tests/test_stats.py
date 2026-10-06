import scipy.stats as stats
import math

def test_trials_factor():
    p_local = stats.norm.sf(5.0)
    assert abs(p_local - 2.866515718791933e-07) < 1e-9
    
    trials = 1e6
    expected_false = trials * p_local
    assert abs(expected_false - 0.28665) < 0.01

def test_matched_filter_snr():
    f = 100.0
    p = 1.0
    var = 15.0**2
    snr = (f*p/var) / math.sqrt(p*p/var)
    assert abs(snr - (100.0/15.0)) < 1e-5

