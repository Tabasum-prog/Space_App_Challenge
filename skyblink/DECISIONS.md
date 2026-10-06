# SkyBlink Decisions

- Architecture: Pre-compute processing pipeline on simulated data, save artifacts locally, serve Next.js statically for frontend if needed, and FastAPI for live processing and dynamic interactions.
- Simulation Framework: Create mock SPHEREx dataset mimicking Linear Variable Filters (LVF) by matching position and wavelength, but treating time (epochs) differently.
- Cross-match: Simulate cross-matching data for the frontend display since it runs fully offline by default.
- UI Framework: Next.js + TailwindCSS + Plotly for interactive plots (with React-Plotly).
- Python Pipeline: Standard array processing with numpy/scipy/astropy. Convolution via FFT for matched filtering.
- WCSAdapter: Since astropy C-extensions can fail due to Windows AppLocker policies, we implemented `WCSAdapter` to gracefully fall back to a pure-numpy linear TAN projection and `scipy.ndimage.map_coordinates` when `astropy.wcs` or `reproject` imports fail.


- **Parallax Unit Error**: The physics report stated 0.825 arcsec, but the correct value for a 500 AU object is ~825 arcsec (using 1/d in parsecs, where 1 pc = 206265 AU, yielding 412530/d for total shift). The formula 412530.0 / d in formulas.py correctly computed 825.06 arcsec, and golden.json correctly stored 825.06. The typo was purely in the documentation text. Tests now explicitly assert 825 arcsec within 1%.
