#!/usr/bin/env python3

import h5py
from pathlib import Path

class Detector(object):
    # An instance of a detector with experimental parameters.

    def __init__(self, masterpath):
        self.masterpath = masterpath
        self.nx = None
        self.ny = None
        self.dettype = None
        self.detname = None
        self.overload = None
        self.qx = None
        self.qy = None
        self.orgx = None
        self.orgy = None
        self.oscillation = None
        self.wavelength = None
        self.distance = None
        self.SN = None
        self.sensorthickness = None
        self.totalframes  = None

        self.h5file = self.__get_h5file(masterpath)
        self.set_parameters_from_file()
        self.close()

    
    def __get_h5file(self,masterpath):
        try: 
            f = h5py.File(masterpath, 'r')
        except Exception:
            raise IOError("Not a valid h5 file")
        return f
    
    def close(self):
        self.h5file.close()
    
    def set_parameters_from_file(self):
        self.ny = self.__set_ny()
        self.nx = self.__set_nx()
        self.detname = self.__set_detname()
        self.dettype = self.__set_dettype(self.detname)
        self.overload = self.__set_overload()
        self.qx = self.__set_qx()
        self.qy = self.__set_qy()
        self.orgx = self.__set_orgx()
        self.orgy = self.__set_orgy()
        self.oscillation = self.__set_oscillation()
        self.wavelength = self.__set_wavelength()
        self.distance = self.__set_distance()
        self.SN = self.__set_SN()
        self.sensorthickness = self.__set_sensorthickness()
        self.totalframes  = self.__set_totalframes()

    def __set_nx(self):
        if '/entry/instrument/detector/detectorSpecific/x_pixels_in_detector' in self.h5file:
            return int(self.h5file['/entry/instrument/detector/detectorSpecific/x_pixels_in_detector'][()])
        else:
            return None
    def __set_ny(self):
        if '/entry/instrument/detector/detectorSpecific/y_pixels_in_detector' in self.h5file:
            return int(self.h5file['/entry/instrument/detector/detectorSpecific/y_pixels_in_detector'][()])
        else:
            return None
    def __set_overload(self):
        if '/entry/instrument/detector/detectorSpecific/countrate_correction_count_cutoff' in self.h5file:
            return int(self.h5file['/entry/instrument/detector/detectorSpecific/countrate_correction_count_cutoff'][()])
        else:
            return 65535
    def __set_detname(self):
        if '/entry/instrument/detector/description' in self.h5file:
            return str(self.h5file['/entry/instrument/detector/description'][()], 'utf-8')
    def __set_dettype(self, detname):
        if 'EIGER' in detname:
            return 'EIGER'
        elif 'PILATUS' in detname:
            return 'PILATUS'
        else:
            return 'GENERIC'
    def __set_qx(self):
        if '/entry/instrument/detector/x_pixel_size' in self.h5file:
            return float(self.h5file['/entry/instrument/detector/x_pixel_size'][()] * 1000)       # convert into mm for XDS
        else:
            return None
    def __set_qy(self):
        if '/entry/instrument/detector/y_pixel_size' in self.h5file:
            return float(self.h5file['/entry/instrument/detector/y_pixel_size'][()] * 1000 )       # convert into mm for XDS
        else:
            return None
    def __set_orgx(self):
        if '/entry/instrument/detector/beam_center_x' in self.h5file:
            return float(self.h5file['/entry/instrument/detector/beam_center_x'][()])
        else:
            return None
    def __set_orgy(self):
        if '/entry/instrument/detector/beam_center_y' in self.h5file:
            return float(self.h5file['/entry/instrument/detector/beam_center_y'][()])
        else:
            return None
    def __set_oscillation(self):
        if '/entry/sample/goniometer/omega_range_average' in self.h5file:
            return float(self.h5file['/entry/sample/goniometer/omega_range_average'][()])
        else:
            return None
    def __set_wavelength(self):
        if '/entry/instrument/beam/incident_wavelength' in self.h5file:
            return float('{:.6f}'.format(self.h5file['/entry/instrument/beam/incident_wavelength'][()]))
        else:
            return None
    def __set_distance(self):
        if '/entry/instrument/detector/detector_distance' in self.h5file:
            return float(self.h5file['/entry/instrument/detector/detector_distance'][()] * 1000)     # convert into mm for XDS
        else:
            return None
    def __set_totalframes(self):
        x = 0
        datalen = len(self.h5file['/entry/data/'])
        lastdata = None
        while not lastdata and (datalen >= x * -1):
            x = x - 1
            ll = list(self.h5file['/entry/data/'].keys())[x]
            lastdata = self.h5file['/entry/data/'].get(ll)
        if lastdata:
            return int(lastdata.attrs.get('image_nr_high'))
        else:
            return None
    def __set_SN(self):
        if '/entry/instrument/detector/detector_number' in self.h5file:
            return str(self.h5file['/entry/instrument/detector/detector_number'][()], 'utf-8')
    def __set_sensorthickness(self):
        if '/entry/instrument/detector/sensor_thickness' in self.h5file:
            return float(self.h5file['/entry/instrument/detector/sensor_thickness'][()] * 1000 )       # convert into mm for XDS
    def get_parameters(self):
        return self.__dict__

def main():
    f = h5py.File(Path('/Users/aaronfinke/test_ssx_eig16m/trypsin_1_1_master.h5'),'r')

    det = Detector(f)
    print("Total frames is: {}".format(det.totalframes))
    print("Distance is: {}".format(det.distance))
    print("wavelength is: {}".format(det.wavelength))
    print("Oscillation is: {}".format(det.oscillation))
    print("ORGX is: {}".format(det.orgx))
    print("ORGY is: {}".format(det.orgy))
    print("NX is: {}".format(det.nx))
    print("NY is: {}".format(det.ny))
    print("QX is: {}".format(det.qx))
    print("QY is: {}".format(det.qy))
    print("Det name is: {}".format(det.detname))
    print("Det type is: {}".format(det.dettype))
    print("Det SN is: {}".format(det.SN))
    print("Overload is: {}".format(det.overload))
    print("Sensor thickness is: {}".format(det.sensorthickness))

if __name__ == '__main__':
    main()