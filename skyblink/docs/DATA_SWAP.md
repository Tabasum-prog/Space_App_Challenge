# Data Swap Instructions

To plug in real IRSA data, you need to implement the `IrsaProvider` in `pipeline/skyblink_pipeline/providers/irsa.py`.

1. Implement `query(ra, dec)` using `pyvo` or `astroquery` against IRSA's ObsTAP/SIA service.
2. Implement `wavelength_at(exposure, ra, dec)` using the spectral WCS information.
3. Implement `fetch_cutout(exposure, ra, dec, size_deg)` to fetch image cutouts using the IRSA cutout service.
4. Choose real fields and create the YAML configurations in `config/fields/`.
5. Run the pipeline with `SKYBLINK_ONLINE=1`.
