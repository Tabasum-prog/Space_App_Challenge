import numpy as np

try:
    from astropy.wcs import WCS
    HAS_ASTROPY = True
except ImportError:
    HAS_ASTROPY = False

class BaseWCS:
    def pixel_to_world(self, x, y):
        raise NotImplementedError
    def world_to_pixel(self, ra, dec):
        raise NotImplementedError

class NumpyWCS(BaseWCS):
    def __init__(self, crval, crpix, cdelt):
        self.crval = np.array(crval)
        self.crpix = np.array(crpix)
        self.cdelt = np.array(cdelt)
        
    def pixel_to_world(self, x, y):
        ra = self.crval[0] + (x - self.crpix[0]) * self.cdelt[0] / np.cos(np.radians(self.crval[1]))
        dec = self.crval[1] + (y - self.crpix[1]) * self.cdelt[1]
        return ra, dec
        
    def world_to_pixel(self, ra, dec):
        x = self.crpix[0] + (ra - self.crval[0]) * np.cos(np.radians(self.crval[1])) / self.cdelt[0]
        y = self.crpix[1] + (dec - self.crval[1]) / self.cdelt[1]
        return x, y

class AstropyWCS(BaseWCS):
    def __init__(self, header):
        self.wcs = WCS(header)
        
    def pixel_to_world(self, x, y):
        return self.wcs.pixel_to_world_values(x, y)
        
    def world_to_pixel(self, ra, dec):
        return self.wcs.world_to_pixel_values(ra, dec)

def create_wcs(header=None, crval=None, crpix=None, cdelt=None, force_numpy=False):
    if HAS_ASTROPY and header is not None and not force_numpy:
        return AstropyWCS(header)
    if crval is not None and crpix is not None and cdelt is not None:
        return NumpyWCS(crval, crpix, cdelt)
    raise ValueError("Not enough WCS info provided")

import scipy.ndimage
def reproject_image(data, header_in, header_out):
    # Fallback using scipy map_coordinates
    wcs_in = create_wcs(header_in, crval=(header_in['CRVAL1'], header_in['CRVAL2']), crpix=(header_in['CRPIX1'], header_in['CRPIX2']), cdelt=(header_in['CDELT1'], header_in['CDELT2']), force_numpy=True)
    wcs_out = create_wcs(header_out, crval=(header_out['CRVAL1'], header_out['CRVAL2']), crpix=(header_out['CRPIX1'], header_out['CRPIX2']), cdelt=(header_out['CDELT1'], header_out['CDELT2']), force_numpy=True)
    y_idx, x_idx = np.indices(data.shape)
    ra, dec = wcs_out.pixel_to_world(x_idx, y_idx)
    x_in, y_in = wcs_in.world_to_pixel(ra, dec)
    return scipy.ndimage.map_coordinates(data, [y_in, x_in], order=1, mode='constant', cval=np.nan)

