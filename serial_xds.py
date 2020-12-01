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
from jsonenc import JSONEnc
import master
import scale


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
    parser.add_argument('-i', '--input', type=lambda p: Path(p, exists=True).absolute(), nargs='+',
                        help='Path(s) of HDF5 master file(s)')
    parser.add_argument('-b', '--beamcenter', type=int, nargs=2,
                        help='Beam center in X and Y (pixels)')
    parser.add_argument('-o', '--oscillation', type=float,
                        help='Oscillation per well to process')
    parser.add_argument('-d', '--distance', type=float,
                        help='Detector distance in mm')
    parser.add_argument('-c', '--config_file', type=lambda p: Path(p, exists=True).absolute(),
                        help='json file containing configs')
    parser.add_argument('-r', '--oscillationperwell', type=float,
                        help='Oscillation angle per well')
    parser.add_argument('-w', '--wavelength', type=float, default=1,
                        help='Wavelength in Angstrom')
    parser.add_argument('-f','--framesperdegree', type=int, default=5,
                        help='Number of frames per degree')
    parser.add_argument('--assert_P1', action='store_true', help="Assert P1 Space Group")
    parser.add_argument('--output', type=lambda p: Path(p, exists=True).absolute(), default=Path.cwd().absolute(),
                        help='Change output directory')
    parser.add_argument('--outputname', type=str, default="ssxoutput",
                        help='Change output directory')
    parser.add_argument('-s','--spacegroup', type=int, default=0,
                        help='Space group number to be used in indexing, default is to determina automatically')
    parser.add_argument('-l', '--library', type=str,
                        default=neggia_path,
                        help='Location of Dectris Neggia library')
    parser.add_argument('-m', '--maxframes', type=int,
                        help='Number of max frames to process (default all frames)')
    parser.add_argument('-u', '--unitcell', type=str, default="100 100 100 90 90 90",
                        help='Unit cell to be used in indexing')
    parser.add_argument('--scale', action='store_true', help="Do XSCALE after processing")

    parser.parse_args()
    args = parser.parse_args()
    if args.config_file is not None:
        with args.config_file.open() as f:
            configs = json.load(f)
            for key in configs:
                if key == 'config_file':
                    continue
                if getattr(args, key) is None:
                    setattr(args, key, configs[key])
    master.check_args(args)

    outpath_path = args.output
    formatted_date = '{a:04d}{b:02d}{c:02d}_{d:02d}{e:02d}{f:02d}'.format(
                    a=date.year,b=date.month,c=date.day,d=date.hour,e=date.minute,f=date.second)
    output_directory = Path(outpath_path / '{a}_{b}'.format(a=args.outputname, b=formatted_date))
    master.create_output_directory(output_directory)

    print("Output directory is {}".format(output_directory))
    sys.stdout.flush()

    output_dictionary = {}

    try:
        Path(output_directory / 'arguments.json').write_text(json.dumps(vars(args), cls=JSONEnc))
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        sys.exit("File 'arguments.json' could not be written.")

    for masterfile in args.input:
        master_h5 = master.get_h5_file(masterfile)
        if not master.is_masterH5file(master_h5):
            sys.exit('not a valid master file')
        master_h5.close()
        # Return number of data files linked to a master file:
        print('master file is: {}'.format(masterfile))
        master_class = master.Master(args, masterfile, output_directory)
        output_dictionary[master_class.get_master_directory_name()] = master_class.get_master_dictionary()
        Path( output_directory / 'results.json').write_text(json.dumps(output_dictionary, indent=2, cls=JSONEnc, sort_keys=True))

        #run scale.py if asked for
        if args.scale:
            xsdir = scale.generate_xscale_directory(output_directory)
            scale.generate_xscaleINP(output_dictionary, args, xsdir)
            scale.run_xscale(xsdir)

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
