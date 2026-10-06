from pipeline.skyblink_pipeline.physics.formulas import diatomic_vibration, wien_peak, dimming, parallax
import json
import os

def test_physics_golden():
    golden_path = os.path.join(os.path.dirname(__file__), "../../physics/golden.json")
    with open(golden_path) as f:
        golden = json.load(f)
        
    co_k = golden["spectroscopy"]["co_k_N_m"]
    nu_12_16 = diatomic_vibration(co_k, 12, 15.9949)
    assert abs(nu_12_16 - golden["spectroscopy"]["co_12_16_wavenumber_cm_1"]) < 1.0
    
    wave_12_16 = 10000.0 / nu_12_16 
    assert abs(wave_12_16 - golden["spectroscopy"]["co_12_16_wavelength_um"]) < 0.01
    
    nu_13_16 = diatomic_vibration(co_k, 13.00335, 15.9949)
    wave_13_16 = 10000.0 / nu_13_16
    assert abs(wave_13_16 - golden["spectroscopy"]["co_13_16_wavelength_um"]) < 0.02
    
    assert abs(wien_peak(golden["wiens_law"]["temp_k"]) - golden["wiens_law"]["peak_wavelength_um"]) < 0.1
    
    assert abs(dimming(30, 500) - golden["planet_x"]["dimming_30_to_500_au"]) < 1.0
    
    assert abs(parallax(500) - 825.0) < 8.25
    assert abs(golden["planet_x"]["parallax_shift_500_au_arcsec"] - 825.0) < 8.25
