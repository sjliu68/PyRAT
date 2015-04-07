import pyrat, os
import logging
from osgeo import gdal
import glob
import numpy as np


class ENVISAT(pyrat.ImportWorker):
    """
    Import of ENVISAT satellite data.

    **author:** Andreas Reigber\n
    **status:** --beta-- No metadata are extracted. Mostly untested!
    """

    gui = {'menu': 'File|Import spaceborne', 'entry': 'ENVISAT'}
    para = [{'var': 'file', 'value': '', 'type': 'openfile', 'text': 'Product file (*.N1)'}]

    def __init__(self, *args, **kwargs):
        super(ENVISAT, self).__init__(*args, **kwargs)
        self.name = "ENVISAT IMPORT"

    def getsize(self, *args, **kwargs):
        self.ds = gdal.Open(self.file)
        if self.ds is not None:
            self.band = []
            for band in range(self.ds.RasterCount):
                self.band.append(self.ds.GetRasterBand(band+1))
            return self.ds.RasterYSize, self.ds.RasterXSize
        else:
            logging.error("ERROR: product directory not recognised!")
            return False, False

    def block_reader(self, *args, **kwargs):
        array = []
        for band in self.band:
            array.append(band.ReadAsArray(xoff=0, yoff=kwargs['block'][0], win_ysize=self.blocksize))
        if len(array) == 1:
            return array[0]
        else:
            return array

    def close(self, *args, **kwargs):
        self.ds = None          # correct according to GDAL manual!!??

    def getmeta(self, *args, **kwargs):
        meta = {}
        meta['sensor'] = "ENVISAT"
        metain = self.ds.GetMetadata()
        meta.update(metain)
        for band in self.band:
            metain = band.GetMetadata()
            meta.update(metain)
        return meta

class PALSAR(pyrat.ImportWorker):
    """
    Import of PALSAR satellite data. Only level 1.1. and 1.5 are supported.

    **author:** Andreas Reigber\n
    **status:** --beta-- No metadata are extracted. Mostly untested!
    """

    gui = {'menu': 'File|Import spaceborne', 'entry': 'PALSAR'}
    para = [{'var': 'dir', 'value': '', 'type': 'opendir', 'text': 'Product directory'}]

    def __init__(self, *args, **kwargs):
        super(PALSAR, self).__init__(*args, **kwargs)
        self.name = "PALSAR IMPORT"

    def getsize(self, *args, **kwargs):
        volfile = glob.glob(self.dir+"/VOL*")
        if len(volfile) > 0:
            self.ds = gdal.Open(volfile[0])
            if self.ds is not None:
                self.band = []
                for band in range(self.ds.RasterCount):
                    self.band.append(self.ds.GetRasterBand(band+1))
                return len(self.band), self.ds.RasterYSize, self.ds.RasterXSize
            else:
                logging.error("ERROR: product directory not recognised!")
                return False, False
        else:
            logging.error("ERROR: volume file not found!")
            return False, False

    def block_reader(self, *args, **kwargs):
        array = []
        for band in self.band:
            array.append(band.ReadAsArray(xoff=0, yoff=kwargs['block'][0], win_ysize=self.blocksize))
        out = np.empty((len(array), )+array[0].shape, dtype=array[0].dtype)
        for k in range(len(array)):
            out[k, ...] = array[k]
        out[~np.isfinite(out)] = 0
        return out.squeeze()

    def close(self, *args, **kwargs):
        self.ds = None          # correct according to GDAL manual!!??

    def getmeta(self, *args, **kwargs):
        meta = {}
        meta['sensor'] = "PALSAR"
        metain = self.ds.GetMetadata()
        meta.update(metain)
        for band in self.band:
            metain = band.GetMetadata()
            meta.update(metain)
        return meta


class Radarsat2(pyrat.ImportWorker):
    """
    Import of Radarsat=2 satellite data.

    **author:** Andreas Reigber\n
    **status:** --beta-- No metadata are extracted. Mostly untested!
    """

    gui = {'menu': 'File|Import spaceborne', 'entry': 'Radarsat-2'}
    para = [{'var': 'dir', 'value': '', 'type': 'opendir', 'text': 'Product directory'}]

    def __init__(self, *args, **kwargs):
        super(Radarsat2, self).__init__(*args, **kwargs)
        self.name = "RADARSAT-2 IMPORT"

    def getsize(self, *args, **kwargs):
        volfile = glob.glob(self.dir+"/product.xml")
        if len(volfile) > 0:
            self.ds = gdal.Open(volfile[0])
            if self.ds is not None:
                self.band = []
                for band in range(self.ds.RasterCount):
                    self.band.append(self.ds.GetRasterBand(band+1))
                return len(self.band), self.ds.RasterYSize, self.ds.RasterXSize
            else:
                logging.error("ERROR: product directory not recognised!")
                return False, False
        else:
            logging.error("ERROR: product.xml file not found!")
            return False, False

    def block_reader(self, *args, **kwargs):
        array = []
        for band in self.band:
            array.append(band.ReadAsArray(xoff=0, yoff=kwargs['block'][0], win_ysize=self.blocksize))
        out = np.empty((len(array), )+array[0].shape, dtype=array[0].dtype)
        for k in range(len(array)):
            out[k, ...] = array[k]
        out[~np.isfinite(out)] = 0
        return out.squeeze()

    def close(self, *args, **kwargs):
        self.ds = None          # correct according to GDAL manual!!??

    def getmeta(self, *args, **kwargs):
        meta = {}
        meta['sensor'] = "Radarsat-2"
        metain = self.ds.GetMetadata()
        meta.update(metain)
        meta['CH_pol'] = []
        for band in self.band:
            metain = band.GetMetadata()
            meta['CH_pol'].append(metain['POLARIMETRIC_INTERP'])
            meta.update(metain)
        return meta

