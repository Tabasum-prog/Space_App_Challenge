import os
import json
import glob
from astropy.coordinates import SkyCoord
import astropy.units as u

def run_validation():
    print("Running validation...")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    cand_dir = os.path.join(base_dir, 'web/public/data/candidates')
    cat_dir = os.path.join(base_dir, 'data/catalogs')
    out_file = os.path.join(base_dir, 'web/public/data/validation.json')
    
    # Load ground truth
    ground_truth = []
    for cat_file in glob.glob(os.path.join(cat_dir, '*.json')):
        with open(cat_file) as fp:
            ground_truth.extend(json.load(fp))
            
    total_injected = len(ground_truth)
    recovered = 0
    false_positives = 0
    
    gt_coords = SkyCoord([t['ra'] for t in ground_truth]*u.deg, [t['dec'] for t in ground_truth]*u.deg) if ground_truth else None
    
    # Check candidates
    total_candidates = 0
    for cand_file in glob.glob(os.path.join(cand_dir, '*.json')):
        with open(cand_file) as fp:
            cands = json.load(fp)
            
        for c in cands:
            total_candidates += 1
            ra = c.get('ra', c.get('ra_deg'))
            dec = c.get('dec', c.get('dec_deg'))
            
            is_true_positive = False
            if gt_coords:
                coord = SkyCoord(ra*u.deg, dec*u.deg)
                idx, d2d, _ = coord.match_to_catalog_sky(gt_coords)
                if d2d.arcsec < 5.0:
                    is_true_positive = True
                    
            if is_true_positive:
                recovered += 1
            else:
                false_positives += 1

    # Format output
    validation = {
        "injection_recovery": {
            "total_injected": total_injected,
            "recovered": recovered,
            "recovery_rate": recovered / total_injected if total_injected > 0 else 0
        },
        "known_object_recovery": {
            "total_candidates": total_candidates,
            "known": recovered,
            "unknown": false_positives
        },
        "false_positive_audit": {
            "false_positives": false_positives,
            "false_positive_rate": false_positives / total_candidates if total_candidates > 0 else 0
        }
    }
    
    with open(out_file, 'w') as fp:
        json.dump(validation, fp, indent=2)
    print("Validation complete, wrote validation.json")

if __name__ == '__main__':
    run_validation()
