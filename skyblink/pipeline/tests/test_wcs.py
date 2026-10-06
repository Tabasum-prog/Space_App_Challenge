from pipeline.skyblink_pipeline.core.wcs_adapter import NumpyWCS, create_wcs
import numpy as np

def test_numpy_wcs():
    wcs = NumpyWCS(crval=(10, 20), crpix=(128, 128), cdelt=(-6.2/3600, 6.2/3600))
    ra, dec = wcs.pixel_to_world(128, 128)
    assert abs(ra - 10) < 1e-9
    assert abs(dec - 20) < 1e-9
    
    x, y = wcs.world_to_pixel(ra, dec)
    assert abs(x - 128) < 1e-9
    assert abs(y - 128) < 1e-9
