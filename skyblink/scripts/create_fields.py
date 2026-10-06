import os
import yaml

def create_yaml_fields(config_dir):
    fields = [
        {"id": "F_MOVER", "name": "Mover Field", "passes": 3, "center": (10, 20)},
        {"id": "F_COMET", "name": "Comet Field", "passes": 3, "center": (30, 40)},
        {"id": "F_DENSE", "name": "Dense Star Field", "passes": 3, "center": (50, 60)},
        {"id": "F_EMPTY", "name": "Empty Field", "passes": 3, "center": (70, 80)},
        {"id": "F_ONE", "name": "One Pass Field", "passes": 1, "center": (90, 10)},
        {"id": "F_VAR", "name": "Variable Star Field", "passes": 3, "center": (110, 20)},
        {"id": "F_OTHER1", "name": "Other Field 1", "passes": 3, "center": (130, 40)},
        {"id": "F_OTHER2", "name": "Other Field 2", "passes": 3, "center": (150, 60)},
    ]
    
    os.makedirs(os.path.join(config_dir, "fields"), exist_ok=True)
    
    for f in fields:
        data = {
            "id": f["id"],
            "name": f["name"],
            "center": {"ra_deg": f["center"][0], "dec_deg": f["center"][1]},
            "size_deg": 0.2,
            "bands_um": [1.25, 2.20, 3.30, 4.27],
            "delta_lambda_um": 0.02,
            "passes_available": [f"2025-pass{i+1}" for i in range(f["passes"])],
            "pair_status": "ok" if f["passes"] >= 2 else "not_enough_epochs",
            "expected_objects": [],
            "story": "",
            "notes": ""
        }
        with open(os.path.join(config_dir, "fields", f"{f['id']}.yaml"), "w") as out:
            yaml.dump(data, out)
    print("YAML fields created.")

if __name__ == "__main__":
    create_yaml_fields(os.path.abspath(os.path.join(os.path.dirname(__file__), "../config")))
