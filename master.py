#!/usr/bin/env python3

import os, sys, h5py, json, re, errno
from multiprocessing import Pool, Manager
import datawell
from pathlib import Path
from jsonenc import JSONEnc

class Master(object):

    # Generating a constructor for the class:
    def __init__(self, args, masterfilepath, output_directory):
        self.args = args
        self.masterfilepath = masterfilepath
        self.framesperdegree = args.framesperdegree
        self.frames_per_well = int(args.oscillationperwell * args.framesperdegree)
        self.frames_to_process = int(args.oscillation * args.framesperdegree) - 1
        self.output = output_directory
        self.beamcenter, self.distance, self.wavelength, self.total_frames = self.get_attributes_from_H5(self.args, self.masterfilepath)
        self.unitcell = args.unitcell
        self.spacegroup = args.spacegroup
        self.library = args.library
        # Variables defined within class:
        self.master_dictionary = Manager().dict()
        self.new_list = []

        # Functions called within class:
        self.create_master_directory() # creating masterfile directories
        self.master_directory_path = self.get_master_directory_path()

        # creating datawell directory and run XDS in it (with parallelization)
        self.run()
        self.write_to_json()

    def get_attributes_from_H5(self, args, masterfilepath):
        f = get_h5_file(masterfilepath)
        beamcenter = self.get_beamcenter(args, f)
        distance = self.get_distance(args, f)
        wavelength = self.get_wavelength(args, f)
        total_frames = self.get_total_frames(args, f)
        f.close()
        return beamcenter, distance, wavelength, total_frames

    def get_total_frames(self, args, h5file):
        if args.maxframes is None:
            return int(len(list(h5file['/entry/data/'])) * args.oscillation * args.framesperdegree)
        else:
            return args.maxframes

    def get_beamcenter(self, args, h5file):
        if args.beamcenter is None:
            bs_x = h5file['/entry/instrument/detector/beam_center_x'][()]
            bs_y = h5file['/entry/instrument/detector/beam_center_y'][()]
            beamcenter = [bs_x, bs_y]
        else:
            beamcenter = args.beamcenter
        return beamcenter

    def get_distance(self, args, h5file):
        if args.distance is None:
            # need to convert into mm for XDS
            distance = h5file['/entry/instrument/detector/distance'][()] * 1000
        else:
            distance = args.distance
        return distance

    def get_wavelength(self, args, h5file):
        if args.wavelength is None:
            wavelength = h5file['/entry/instrument/beam/incident_wavelength'][()]
        else:
            wavelength = args.wavelength
        return wavelength

    def run(self):
        p = Pool()
        for framenum in range(1,self.total_frames,self.frames_per_well):
            p.apply_async(self.create_and_run_data_wells, args=(framenum, self.master_dictionary))
        p.close()
        p.join()
        #single-thread version
        # for framenum in range(1,self.total_frames,self.frames_per_well):
        #     self.create_and_run_data_wells(framenum, self.master_dictionary)

    def create_master_directory(self):
        # Create a masterfile directory
        dirname = re.sub('_master','',self.masterfilepath.stem)
        try:
            Path(self.output / dirname).mkdir()
        except:
            sys.exit("Creation of the directory {} failed.".format(dir_name))

    def create_and_run_data_wells(self, framenum, md):
        #breakpoint()
        # Generate datawell directories by creating instances of class called 'Datawell' (from datawell.py):
        dw = datawell.Datawell(framenum, framenum+self.frames_to_process, self.master_directory_path,
                                    self.masterfilepath, self.beamcenter, self.distance, self.wavelength, 
                                    self.unitcell, self.spacegroup, self.library, self.framesperdegree)
        print("Processing frames {}-{}...".format(framenum,framenum+self.frames_to_process))

        dw.setup_datawell_directory()
        dw.gen_XDS()
        dw.run()
        dw.check_and_rerun()
        md[dw.getframes()] = dw.get_dw_dict()


    def get_master_directory_name(self):
        return self.masterfilepath.stem

    def get_master_directory_path(self):
         # Return master directory path. Used in the above function.
        dirname = re.sub('_master','',self.masterfilepath.stem)
        return Path(self.output / dirname)

    def get_master_dictionary(self):
        return self.master_dictionary.copy()

    def write_to_json(self):
        Path(self.master_directory_path / 'results_{b}.json'.format(b=self.get_master_directory_name())).write_text(
            json.dumps(self.master_dictionary.copy(), indent=2, sort_keys=True, cls=JSONEnc)
        )

def create_output_directory(path):
    try:
        Path(path).mkdir()
    except OSError:
        sys.exit("Creation of the directory {} failed. Such file may already exist.".format(dir_name))


def get_h5_file(path):
    try:
        file = h5py.File(path, 'r')
    except Exception:
        raise IOError("Not a valid h5 file")
        sys.exit()
    return file


def check_args(args):
    def args_exit():
        sys.exit("Please check your input!")

    if args.oscillationperwell is None:
        args.oscillationperwell = args.oscillation
    if args.input is None:
        print("Input directory must be specified.")
        args_exit()
    if args.oscillation is None:
        print("Please provide the oscillation per well.")
        args_exit()

def is_masterH5file(h5file):
    try:
        detname = h5file['/entry/instrument/detector/description'][()]
    except:
        result = False
    return True
