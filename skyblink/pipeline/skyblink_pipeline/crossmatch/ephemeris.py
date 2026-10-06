import json
import os

class SyntheticCrossMatch:
    def __init__(self, cat_dir):
        mpc_file = os.path.join(cat_dir, "synthetic_mpc.json")
        gaia_file = os.path.join(cat_dir, "synthetic_gaia.json")
        self.objects = {}
        
        if os.path.exists(mpc_file):
            with open(mpc_file) as f:
                for obj in json.load(f):
                    self.objects[obj['id']] = obj
                    
        if os.path.exists(gaia_file):
            with open(gaia_file) as f:
                for obj in json.load(f):
                    # Stars might not have epoch/pmra defined as fully, ensure defaults
                    if 'epoch' not in obj:
                        obj['epoch'] = 60000.0
                    if 'pmra' not in obj:
                        obj['pmra'] = 0.0
                    if 'pmdec' not in obj:
                        obj['pmdec'] = 0.0
                    self.objects[obj['id']] = obj

    def ephemeris(self, obj_id, mjd):
        if obj_id not in self.objects:
            return None
        obj = self.objects[obj_id]
        dt = mjd - obj['epoch']
        ra = obj['ra'] + obj['pmra'] * dt
        dec = obj['dec'] + obj['pmdec'] * dt
        return {'ra': ra, 'dec': dec}

    def get_all_ids(self):
        return list(self.objects.keys())
