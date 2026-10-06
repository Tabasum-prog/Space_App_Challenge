import math

def diatomic_vibration(k, m1, m2):
    amu_kg = 1.66053906660e-27
    c = 299792458 * 100 
    mu = (m1 * m2) / (m1 + m2) * amu_kg
    nu = (1 / (2 * math.pi * c)) * math.sqrt(k / mu)
    return nu

def wien_peak(t):
    return 2897.8 / t

def dimming(d1, d2):
    return (d2/d1)**4

def parallax(d):
    return 412530.0 / d
