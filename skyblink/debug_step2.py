import os
import json
import numpy as np

def debug_step2():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'web/public/data'))
    with open(os.path.join(data_dir, 'follow_object.json')) as f:
        follow_all = json.load(f)
        
    for c in follow_all:
        print(f"Object {c['id']}: {len(c.get('track', []))} track points")
        
    ast = next(c for c in follow_all if c['id'] == 'ast1')
    comet = next((c for c in follow_all if c['id'] == 'comet1'), None)
    
    print("--- Asteroid Track ---")
    for t in ast['track'][:5]:
        print(f"MJD: {t['mjd']:.2f}, X: {t['x']:.2f}, Y: {t['y']:.2f}, Flux: {t['flux']:.2f}")
        
    if comet:
        print("\n--- Comet Spectrum ---")
        for s in comet['spectrum']:
            print(f"Wave: {s['wave']:.2f}, Flux: {s['flux']:.2f}, SNR: {s['flux']/s['flux_err']:.2f}")

    # (a) asteroid track positions recovered within 1 pixel
    # True asteroid shifts in pass 2: +10 pixels in X.
    # We will check if x varies by ~10 between pass1 and pass2
    xs_pass1 = [t['x'] for t in ast['track'] if t['pass'] == '2025-pass1']
    xs_pass2 = [t['x'] for t in ast['track'] if t['pass'] == '2025-pass2']
    if xs_pass1 and xs_pass2:
        diff = np.mean(xs_pass2) - np.mean(xs_pass1)
        print(f"Asteroid X shift pass1 -> pass2: {diff:.2f} (Expected ~10)")

    if comet:
        # (b) comet excess at 4.27 um over continuum
        waves = [s['wave'] for s in comet['spectrum']]
        fluxes = [s['flux'] for s in comet['spectrum']]
        if waves:
            # find 4.27
            idx_427 = np.argmin(np.abs(np.array(waves) - 4.27))
            print(f"Bump flux at {waves[idx_427]:.2f}: {fluxes[idx_427]:.2f}")

if __name__ == '__main__':
    debug_step2()
