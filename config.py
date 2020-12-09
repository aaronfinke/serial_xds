#!/usr/bin/env python3

from argparse import ArgumentParser
import os,sys
from pathlib import Path
import h5py
from detector import Detector
import json
from jsonenc import JSONEnc

class Config(object):
    '''
    An instance of configurations for processing.
    '''

    def __init__(self, args, masterfilepath, configfile=None):
        self.args = args
        self.configfile = None
        self.input = masterfilepath
        self.oscillationperwell = None
        self.outputdir = None
        self.outputname = None
        self.spacegroup = None
        self.library = None
        self.unitcell = None
        self.njobs = None
        self.nproc = None
        self.nprocpool = None
        self.reversephi = None
        self.xscale = None

        self.nx = None
        self.ny = None
        self.dettype = None
        self.detname = None
        self.overload = None
        self.qx = None
        self.qy = None
        self.SN = None
        self.beamcenter = None
        self.oscillation = None
        self.distance = None
        self.wavelength = None
        self.sensorthickness = None
        self.totalframes  = None
        self.frontoffset = None
        self.backoffset = None
        self.framesperwell = None

        self.configuration = {}

    

    def set_args(self):
        self.input = self.args.input
        self.oscillationperwell = self.args.oscillationperwell
        self.outputdir = self.args.outputdir
        self.outputname = self.args.outputname
        self.spacegroup = self.args.spacegroup
        self.library = self.args.library
        self.totalframes = self.args.totalframes
        self.unitcell = self.args.unitcell
        self.njobs = self.args.njobs
        self.nproc = self.args.nproc
        self.nprocpool = int(os.cpu_count() / self.njobs)
        self.reversephi = self.args.reversephi
        self.xscale = self.args.xscale
        self.frontoffset = self.args.frontoffset
        self.backoffset = self.args.backoffset
        self.framesperwell = int(self.oscillationperwell * (1 / self.oscillation))

    
    def set_detector_params(self,masterpath):
        det = Detector(masterpath)
        self.nx = det.nx
        self.ny = det.ny
        self.dettype = det.dettype
        self.detname = det.detname
        self.overload = det.overload
        self.qx = det.qx
        self.qy = det.qy
        self.beamcenter = [det.orgx, det.orgy]
        self.oscillation = det.oscillation
        self.wavelength = det.wavelength
        self.distance = det.distance
        self.SN = det.SN
        self.sensorthickness = det.sensorthickness
        self.totalframes  = det.totalframes

    def update_config_file(self,args,configfile):
        with configfile.open() as f:
            configs = json.load(f)
            for key in configs:
                if key == 'config_file':
                    continue
                if getattr(args, key) is None:
                    setattr(args, key, configs[key])

    def write_config_to_file(self,output_dir):
        # try:
        Path(output_dir / 'config.json').write_text(json.dumps(self.configuration, indent=1, cls=JSONEnc))
        # except Exception as ex:
        #     template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        #     message = template.format(type(ex).__name__, ex.args)
        #     print(message)
        #     sys.exit("File 'arguments.json' could not be written.")

    def update_configuration(self):
        self.configuration = {
            'input' : self.input ,
            'configfile' : self.configfile ,
            'oscillationperwell' : self.oscillationperwell ,
            'framesperwell' : self.framesperwell ,
            'outputdir' : self.outputdir ,
            'outputname' : self.outputname ,
            'spacegroup' : self.spacegroup ,
            'library' : self.library ,
            'frontoffset' : self.frontoffset ,
            'backoffset' : self.backoffset ,
            'unitcell' : self.unitcell ,
            'njobs' : self.njobs ,
            'nproc' : self.nproc ,
            'reversephi' : self.reversephi ,
            'xscale' : self.xscale ,

            'nx' : self.nx ,
            'ny' : self.ny ,
            'dettype' : self.dettype ,
            'detname' : self.detname ,
            'overload' : self.overload ,
            'qx' : self.qx ,
            'qy' : self.qy ,
            'SN' : self.SN ,
            'beamcenter' : self.beamcenter ,
            'oscillation' : self.oscillation ,
            'distance' : self.distance ,
            'wavelength' : self.wavelength ,
            'sensorthickness' : self.sensorthickness ,
            'totalframes' : self.totalframes 
        }


def create_output_directory(path):
    try:
        Path(path).mkdir()
    except OSError:
        sys.exit("Creation of the directory {} failed. Such file may already exist.".format(path))


