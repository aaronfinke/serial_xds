#!/usr/bin/env python3

import os, sys, h5py, json, re, errno
from multiprocessing import Pool, Manager
import datawell

class Master(object):

    # Generating a constructor for the class:
    def __init__(self, args, masterpath, num_of_total_frames, output_directory):
        self.args = args
        self.masterpath = masterpath
        self.frames_per_degree = args.framesperdegree
        self.frames_per_well = int(args.oscillationperwell * args.framesperdegree)
        self.frames_to_process = int(args.oscillation * args.framesperdegree)
        self.total_frames = num_of_total_frames
        self.output = output_directory


        # Variables defined within class:
        manager = Manager()
        self.master_dictionary = manager.dict()
        self.new_list = []

        # Functions called within class:
        self.create_master_directory() # creating masterfile directories
        self.master_directory_path = self.get_master_directory_path()

        # creating datawell directory and run XDS in it (with parallelization)
        self.run()
        self.write_to_json()

    def run(self):
        p = Pool()
        for framenum in range(1,self.total_frames,self.frames_per_well):
            p.apply_async(self.create_and_run_data_wells, args=(framenum, self.master_dictionary))
        p.close()
        p.join()
        print(self.master_dictionary)

    def create_master_directory(self):
        # Generate a name for masterfile directory:
        end_index = self.masterpath.find('_master.h5')
        start_index = self.masterpath.rfind('/')
        dir_name= self.masterpath[start_index+1:end_index]
        new_dir_path = '{new_dir}/{name}'.format(new_dir = self.output, name = dir_name)

        # Create a masterfile directory:
        try:
            os.makedirs(new_dir_path)
        except FileExistsError:
            print("Creation of the directory {} failed.".format(dir_name))
            sys.exit(1)

    def create_and_run_data_wells(self, framenum, md):
        # Generate datawell directories by creating instances of class called 'Datawell' (from datawell.py):
        dw = datawell.Datawell(framenum, framenum+self.frames_to_process-1, self.master_directory_path,
                                    self.masterpath, self.args)
        dw.setup_datawell_directory()
        dw.gen_XDS()
        dw.run()
        dw_dict = dw.gen_datawell_dict()
        print(dw_dict)
        md[dw.getframes()] = dw_dict
        dw.close()


    def get_master_directory_path(self):
         # Return master directory path. Used in the above function.
            end_index = self.masterpath.find('_master.h5')
            start_index = self.masterpath.rfind('/')
            dir_name= self.masterpath[start_index+1:end_index]
            return '{new_dir}/{name}'.format(new_dir = self.output, name = dir_name)

    def write_to_json(self):
        go_json = json.dumps(self.master_dictionary.copy(), indent=2, sort_keys=True)
        with open(os.path.join('{}'.format(self.master_directory_path), 'results.json'), 'w') as file:
            file.write(go_json)

def get_master_directory_path_from_input(path):
    #get the full path from the master directory from the input.
    if os.path.exists(os.path.abspath(path)):
        print("master file path is {}".format(os.path.abspath(path)))
        return os.path.abspath(path)
    else:
        sys.exit('File "{}" not found. Check the path.'.format(path))

def create_output_directory(path, date):
    output_date = 'ssxoutput_{a:04d}{b:02d}{c:02d}_{d:02d}{e:02d}{f:02d}'.format(
                    a=date.year,b=date.month,c=date.day,d=date.hour,e=date.minute,f=date.second)
    output_dir_path = '{a}/{b}'.format(a = path, b = output_date)
    try:
        os.makedirs(output_dir_path)
    except OSError:
        print("Creation of the directory {} failed. Such file may already exist.".format(dir_name))
        sys.exit(1)
    return output_dir_path

def get_h5_file(path):
    try:
        file = h5py.File(path, 'r')
    except Exception:
        raise IOError("Not a valid h5 file")
    return file

def get_number_of_files(path):
    print(path)
    f = get_h5_file(path)
    return len(f['/entry/data'])

def check_args(args):
    def args_exit():
        sys.exit("Please check your input!")

    if args.oscillationperwell is None:
        args.oscillationperwell = args.oscillation

    if args.input is None:
        print("Input directory must be specified.")
        args_exit()
    else:
        for ip in args.input:
            if not os.path.exists(ip):
                print("Input path does not exist!")
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
