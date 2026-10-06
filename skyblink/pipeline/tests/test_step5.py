import os
import tempfile
import json
from pipeline.skyblink_pipeline.core.run import crossmatch_candidates, export_candidates
from pipeline.skyblink_pipeline.core.models import CandidateRecord

def test_crossmatch_flagging():
    with tempfile.TemporaryDirectory() as td:
        cat_file = os.path.join(td, "catalog.json")
        with open(cat_file, 'w') as fp:
            json.dump([{"id": "star1", "ra": 10.0, "dec": 20.0}], fp)
            
        cands = [
            {"ra": 10.0, "dec": 20.0, "id": "cand1"},
            {"ra": 50.0, "dec": 50.0, "id": "cand2"}
        ]
        
        res = crossmatch_candidates(cands, [cat_file])
        assert res[0]['status'] == 'known'
        assert res[0]['crossmatch']['id'] == 'star1'
        assert res[1]['status'] == 'candidate'

def test_export_schema():
    with tempfile.TemporaryDirectory() as td:
        cands = [{
            "id": "c1",
            "field_id": "F1",
            "ra_deg": 10.0,
            "dec_deg": 20.0,
            "band_um": 1.25,
            "epochs": ["e1", "e2"],
            "snr": 10.0,
            "p_local": 1e-6,
            "p_trials_adjusted": 0.05,
            "kind": "pair",
            "dipole_separation_arcsec": 0.0,
            "sharpness": 1.0,
            "chi2_psf": 1.0,
            "persistent_in_other_pass": False,
            "type_label": "unidentified",
            "crossmatch": {"catalog": None, "id": None, "sep_arcsec": None},
            "status": "candidate",
            "tiles": {"epoch_a": "a", "epoch_b": "b", "diff": "d", "snr": "s"},
            "notes": ""
        }]
        
        export_candidates(cands, "F1", td)
        
        with open(os.path.join(td, "F1.json")) as fp:
            data = json.load(fp)
            rec = CandidateRecord(**data[0])
            assert rec.id == "c1"
