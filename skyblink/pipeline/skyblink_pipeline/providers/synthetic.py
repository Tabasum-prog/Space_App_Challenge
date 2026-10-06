from .base import ImageProvider, ExposureRef
from typing import List, Tuple, Any
import numpy as np

class SyntheticProvider(ImageProvider):
    def query(self, ra: float, dec: float) -> List[ExposureRef]:
        # Return mock exposures
        return [ExposureRef("sim_exp_1", 60000.0), ExposureRef("sim_exp_2", 60180.0)]

    def wavelength_at(self, exposure: ExposureRef, ra: float, dec: float) -> float:
        # Simulate LVF gradient
        return 3.30 

    def fetch_cutout(self, exposure: ExposureRef, ra: float, dec: float, size_deg: float) -> Tuple[Any, Any, Any, Any, Any, float]:
        # Generate random noise for flux and variance
        shape = (256, 256)
        flux = np.random.normal(0, 15.0, shape)
        variance = np.full(shape, 15.0**2)
        flags = np.zeros(shape, dtype=int)
        celestial_wcs = None # Placeholder
        wavelength_map = np.full(shape, 3.30)
        return flux, variance, flags, celestial_wcs, wavelength_map, exposure.mjd
