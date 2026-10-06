# Methods

## Pipeline
1. **Query and band matching**: Select exposures within a wavelength tolerance ($\Delta\lambda$) at the pixel level.
2. **Cutouts and alignment**: Reproject all cutouts to a common celestial grid.
3. **Background and masking**: Subtract zodiacal light and mask flagged pixels.
4. **Photometric scaling**: Scale epochs robustly using known stars to remove drift.
5. **Difference image and detection**: D = A - B.
   SNR = $\sum (f_i p_i / \sigma_i^2) / \sqrt{\sum (p_i^2 / \sigma_i^2)}$
6. **Cross-match**: Match candidates against known bodies.

## Physics
- **Quantum spectroscopy**: Diatomic vibrational wavenumber $\tilde{\nu} = \frac{1}{2\pi c} \sqrt{\frac{k}{\mu}}$
- **Nuclear mass-thresholds**: Classification boundaries for planet, brown dwarf, and star.
- **Planet X Detectability**: Brightness scales as $r^{-4}$. Parallax shift for a 2 AU baseline is $\approx 412530 / d$ arcseconds.

## Data Acknowledgement
TODO: paste the official SPHEREx data acknowledgement from the IRSA SPHEREx page.
QR2 DOI 10.26131/IRSA652
