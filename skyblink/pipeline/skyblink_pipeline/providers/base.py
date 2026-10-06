from abc import ABC, abstractmethod
from typing import List, Tuple, Any

class ExposureRef:
    def __init__(self, id: str, mjd: float):
        self.id = id
        self.mjd = mjd

class ImageProvider(ABC):
    @abstractmethod
    def query(self, ra: float, dec: float) -> List[ExposureRef]:
        pass

    @abstractmethod
    def wavelength_at(self, exposure: ExposureRef, ra: float, dec: float) -> float:
        pass

    @abstractmethod
    def fetch_cutout(self, exposure: ExposureRef, ra: float, dec: float, size_deg: float) -> Tuple[Any, Any, Any, Any, Any, float]:
        """
        Returns: (flux, variance, flags, celestial_wcs, wavelength_map, mjd)
        """
        pass
