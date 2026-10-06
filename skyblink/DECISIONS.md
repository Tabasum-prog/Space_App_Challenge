# Decisions

## Step 1
Edited `generate.py` to add `pmra`, `pmdec` (proper motion) and `epoch` to the objects in `synthetic_mpc.json`. This was necessary so that `SyntheticCrossMatch` could compute the dynamic ephemeris for moving objects (asteroid and comet) at any given MJD, allowing us to remove the hard-coded coordinates from `core/run.py`.
