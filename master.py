#!/usr/bin/env python3

import os, sys, h5py, json, re, errno
from multiprocessing import Pool, Manager
import datawell
from pathlib import Path
from jsonenc import JSONEnc
from config import Config

class Master(object):

    # Generating a constructor for the class:
    def __init__(self, args, masterfilepath, output_directory):
        self.masterfilepath = masterfilepath
        self.args = args
        self.output = output_directory

        # Variables defined within class:
        self.master_dictionary = Manager().dict()
        self.new_list = []
        self.master_directory_path = self.get_master_directory_path()

    def set_config(self):
        self.config = Config(self.args, self.masterfilepath)
        self.config.set_detector_params(self.masterfilepath)
        self.config.set_args()
        self.config.update_configuration()
        return self.config

    def run(self):
        p = Pool(processes=self.config.nprocpool)
        for framenum in range(1,self.config.totalframes,self.config.framesperwell):
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
            sys.exit("Creation of the directory {} failed.".format(dirname))

    def create_and_run_data_wells(self, framenum, md):
        #breakpoint()
        # Generate datawell directories by creating instances of class called 'Datawell' (from datawell.py):
        f1 = framenum + self.config.frontoffset
        f2 = (framenum + self.config.framesperwell) - self.config.backoffset - 1
        dw = datawell.Datawell(self.config, f1, f2, self.master_directory_path, self.masterfilepath)
        print("Processing frames {}-{}...".format(f1, f2))

        dw.setup_datawell_directory()
        dw.gen_XDS()
        dw.run()
        dw.check_and_rerun()
        md[dw.getframes()] = dw.get_dw_dict()


    def get_master_directory_name(self):
        return self.masterfilepath.stem

    def get_master_directory_path(self):
        dirname = re.sub('_master','',self.masterfilepath.stem)
        return Path(self.output / dirname)

    def get_master_dictionary(self):
        return self.master_dictionary.copy()

    def write_to_json(self):
        Path(self.master_directory_path / 'results_{b}.json'.format(b=self.get_master_directory_name())).write_text(
            json.dumps(self.master_dictionary.copy(), indent=2, sort_keys=True, cls=JSONEnc)
        )


def get_h5_file(path):
    try:
        file = h5py.File(path, 'r')
    except Exception:
        raise IOError("Not a valid h5 file")
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

def is_masterH5file(masterpath):
    master_h5 = get_h5_file(masterpath)
    if '/entry/instrument/detector/description' in master_h5:
        master_h5.close()
        return True
    else:
        master_h5.close()
        return False
