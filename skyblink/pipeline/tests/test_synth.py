import os
import yaml
from astropy.io import fits

def test_band_coverage():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/fits"))
    config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config"))
    
    bands = [1.25, 2.20, 3.30, 4.27]
    delta = 0.02
    
    for f in os.listdir(os.path.join(config_dir, "fields")):
        with open(os.path.join(config_dir, "fields", f)) as yaml_file:
            field = yaml.safe_load(yaml_file)
            
        if field["pair_status"] == "ok":
            f_dir = os.path.join(data_dir, field["id"])
            passes = field["passes_available"]
            for p_idx, _ in enumerate(passes):
                for b in bands:
                    matched = False
                    for exp_file in os.listdir(f_dir):
                        if f"_pass{p_idx+1}_" in exp_file:
                            hdul = fits.open(os.path.join(f_dir, exp_file))
                            wave = hdul["WAVELENGTH"].data
                            if (wave.min() <= b + delta) and (wave.max() >= b - delta):
                                matched = True
                                hdul.close()
                                break
                            hdul.close()
                    assert matched, f"Field {field['id']} pass {p_idx+1} is missing band {b}"
