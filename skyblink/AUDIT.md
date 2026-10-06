# Audit Report

**(a) Does core/run.py main() run the real pipeline or write empty lists?**
`core/run.py` main() runs a mocked/simulated pipeline. It writes dummy `np.zeros` diff FITS files and hard-codes synthetic candidates with fixed properties (e.g., `snr: 10.0`, `p_local: 1e-6`) rather than running the real image processing pipeline (no actual provider query, reprojection, background fitting, or difference imaging happens). 

**(b) Which of these exist and are tested: follow-an-object forced photometry, fixed-source spectra, injection-recovery, known-object recovery, false-positive audit, validation.json?**
None of them exist or are tested.
- `pipeline/skyblink_pipeline/validate` does not exist.
- `web/public/data/validation.json` does not exist.
- Follow-an-object forced photometry and fixed-source spectra are entirely missing from the pipeline.

**(c) Which values in the UI are hard-coded (candidates, SNR, p-values, spectrum bump, follow-object frames, image sources)?**
They are all hard-coded in the frontend or provided through the fake pipeline output:
- **Spectrum bump:** The UI code contains `Math.exp` generating a fake bump at `4.27` in `SpectrumView.tsx`.
- **Image sources:** The UI loads "mock PNGs" for viewing.
- **Candidates / SNR / p-values:** Sourced from the fake JSON files produced by `run.py`.
- **Simulated banner:** Hard-coded text in the `/limits` page.
