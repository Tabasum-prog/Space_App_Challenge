import json
import os

def test_mover_found():
    cand_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../web/public/data/candidates/F_MOVER.json"))
    assert os.path.exists(cand_file)
    with open(cand_file) as f:
        cands = json.load(f)
    assert len(cands) > 0
    assert any(c['kind'] == 'pair' for c in cands)

def test_empty_field_respects_threshold():
    cand_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../web/public/data/candidates/F_EMPTY.json"))
    assert os.path.exists(cand_file)
    with open(cand_file) as f:
        cands = json.load(f)
    assert len(cands) < 5
