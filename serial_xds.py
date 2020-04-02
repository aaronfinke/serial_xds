#!/usr/bin/env python3

from argparse import ArgumentParser
import fnmatch
import os, sys
import h5py
import time
import json
from datetime import datetime
from pathlib import Path
import logging
import platform

import master

def main(argv=None):

    # root = logging.getLogger()
    # root.setLevel(logging.DEBUG)
    #
    # streamhandler = logging.StreamHandler(sys.stdout)
    # filehandler = logging.FileHandler(filename='tmp.log')
    # handlers=[streamhandler, filehandler]
    # logging.basicConfig(
    #     level=logging.DEBUG,
    #     format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    #     handlers=handlers
    #     )
    # root.addHandler(streamhandler)
    # root.addHandler(filehandler)

    if argv is None:
        argv = sys.argv

    parser = ArgumentParser(description=
    """
    """)
    parser.add_argument('-i', '--input', type=str, nargs='+',
                        help='Path of Directory containing HDF5 master file(s)')
    parser.add_argument('-b', '--beamcenter', type=int, nargs=2,
                        help='Beam center in X and Y (pixels)')
    parser.add_argument('-o', '--oscillation', type=float,
                        help='Oscillation per well to process')
    parser.add_argument('-d', '--distance', type=float,
                        help='Detector distance in mm')
    parser.add_argument('-c', '--config_file', type=str,
                        help='json file containing configs')
    parser.add_argument('-r', '--oscillationperwell', type=float,
                        help='Oscillation angle per well')
    parser.add_argument('-w', '--wavelength', type=float, default=1.216,
                        help='Wavelength in Angstrom')
    parser.add_argument('-f', '--framesperdegree', type=int, default=5,
                        help='Number of frames per degree')
    parser.add_argument('--output', default=os.getcwd(),
                        help='Change output directory')
    parser.add_argument('-g', '--spacegroup', default=0,
                        help='Space group')
    parser.add_argument('-l', '--library', type=str,
                        default=str(neggia_path),
                        help='Location of Dectris Neggia library')
    parser.add_argument('-u', '--unitcell', type=str, default="100 100 100 90 90 90",
                        help='Unit cell')
    parser.parse_args()
    args = parser.parse_args()
    print(args)
    if args.config_file is not None:
        if '.json' in args.config_file:
            config = json.load(open(args.config_file))
            for key in config:
                if key == 'config_file':
                    continue
                if getattr(args, key) is None:
                    setattr(args, key, config[key])
    master.check_args(args)


    output_directory = master.create_output_directory(args.output, date)

    print("Output directory is {}".format(output_directory))

    try:
        with open(os.path.join(output_directory, 'arguments.json'), 'w') as file:
            file.write(json.dumps(vars(args), indent=1))
    except:
        print("File 'arguments.json' could not be written.")

    # Get all master files from the given path and create a list:
    for masterdir_input in args.input:
        masterdir = master.get_master_directory_path_from_input(masterdir_input)
        master_list = fnmatch.filter(os.listdir(masterdir), "*master.h5")
        for masterfile in master_list:
            # Return number of data files linked to a master file:
            masterpath = "{}/{}".format(masterdir, masterfile)
            totalframes = master.get_number_of_files(masterpath)

            # Each master file in the list now used to create an instance of a class called 'Master' (from master.py):
            master_class = master.Master(args, masterpath, totalframes, output_directory)

if __name__=='__main__':
    time1 = time.time()
    date = datetime.now()

    #OS Check
    source_path = Path(__file__).resolve().parent
    if sys.platform == 'darwin':
        neggia_path = source_path / 'etc' / 'dectris-neggia-mac.so'
    elif sys.platform == 'linux':
        neggia_path = source_path / 'etc' / 'dectris-neggia-centos7.so'
    else:
        sys.exit("Sorry, this program only works on Mac or Linux.")


    main()

    time2 = time.time()
    print("Total processing time: {:.1f} s".format(time2-time1))
