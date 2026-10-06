from .base import ImageProvider, ExposureRef
from typing import List, Tuple, Any
import os

class IrsaProvider(ImageProvider):
    def query(self, ra: float, dec: float) -> List[ExposureRef]:
        if os.environ.get("SKYBLINK_ONLINE") != "1":
            raise NotImplementedError("Live IRSA queries require SKYBLINK_ONLINE=1")
        # UNVERIFIED: confirm against current IRSA/astroquery docs
        # Implementation would use pyvo or astroquery to query ObsTAP/SIA
        return []

    def wavelength_at(self, exposure: ExposureRef, ra: float, dec: float) -> float:
        if os.environ.get("SKYBLINK_ONLINE") != "1":
            raise NotImplementedError("Live IRSA queries require SKYBLINK_ONLINE=1")
        return 0.0

    def fetch_cutout(self, exposure: ExposureRef, ra: float, dec: float, size_deg: float) -> Tuple[Any, Any, Any, Any, Any, float]:
        if os.environ.get("SKYBLINK_ONLINE") != "1":
            raise NotImplementedError("Live IRSA queries require SKYBLINK_ONLINE=1")
        return None, None, None, None, None, 0.0
