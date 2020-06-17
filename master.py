#!/usr/bin/env python3

import os, sys, h5py, json, re, errno
from multiprocessing import Pool, Manager
import datawell
from pathlib import Path
from jsonenc import JSONEnc

class Master(object):

    # Generating a constructor for the class:
    def __init__(self, args, masterfilepath, num_of_total_frames, output_directory):
        self.args = args
        self.masterfilepath = masterfilepath
        self.frames_per_degree = args.framesperdegree
        self.frames_per_well = int(args.oscillationperwell * args.framesperdegree)
        self.frames_to_process = int(args.oscillation * args.framesperdegree)
        self.total_frames = num_of_total_frames
        self.output = output_directory


        # Variables defined within class:
        self.master_dictionary = Manager().dict()
        self.new_list = []

        # Functions called within class:
        self.create_master_directory(self.masterfilepath) # creating masterfile directories
        self.master_directory_path = self.get_master_directory_path(self.masterfilepath)

        # creating datawell directory and run XDS in it (with parallelization)
        self.run()
        self.write_to_json()

    def run(self):
        p = Pool()
        for framenum in range(1,self.total_frames,self.frames_per_well):
            p.apply_async(self.create_and_run_data_wells, args=(framenum, self.master_dictionary))
        p.close()
        p.join()

    def create_master_directory(self, masterfilepath):
        # Generate a name for masterfile directory:
        suffix = masterfilepath.name.strip('_master.h5')
        new_dir_path = Path(self.output / suffix)
        # Create a masterfile directory:
        try:
            new_dir_path.mkdir()
        except:
            sys.exit("Creation of the directory {} failed.".format(dir_name))

    def create_and_run_data_wells(self, framenum, md):
        # Generate datawell directories by creating instances of class called 'Datawell' (from datawell.py):
        print("Processing frames {}-{}...".format(framenum,framenum+self.frames_to_process-1))
        dw = datawell.Datawell(framenum, framenum+self.frames_to_process-1, self.master_directory_path,
                                    self.masterfilepath, self.args)
        dw.setup_datawell_directory()
        dw.gen_XDS()
        dw.run()
        #dw.check_and_rerun()
        md[dw.getframes()] = dw.get_dw_dict()


    def get_master_directory_name(self,masterfilepath):
        return masterfilepath.name.strip('_master.h5')

    def get_master_directory_path(self, masterfilepath):
         # Return master directory path. Used in the above function.
        suffix = masterfilepath.name.strip('_master.h5')
        return Path(self.output / suffix)

    def get_master_dictionary(self):
        return self.master_dictionary.copy()

    def write_to_json(self):
        Path(self.master_directory_path / 'results_{b}.json'.format(b=self.get_master_directory_name(self.masterfilepath))).write_text(
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
    return file

def get_number_of_files(path, args):
    print(path)
    f = get_h5_file(path)
    lastdata = list(f['/entry/data/'].keys())[-1]
    try:
        numimages = f['/entry/data/'].get(lastdata).attrs.get('image_nr_high')
    except:
        numimages = len(list(f['/entry/data/'].keys())) * int(args.oscillation) * int(args.framesperdegree)
    return numimages

def check_args(args):
    def args_exit():
        sys.exit("Please check your input!")

    if args.oscillationperwell is None:
        args.oscillationperwell = args.oscillation
    if args.input is None:
        print("Input directory must be specified.")
        args_exit()
    if args.beamcenter is None or len(args.beamcenter) != 2:
        print("Please specify the beam center.")
        args_exit()
    if args.oscillation is None:
        print("Please provide the oscillation per well.")
        args_exit()
    if args.distance is None:
        print("Please provide the detector distance.")
        args_exit()
