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
import config


def main(argv=None):

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


    if argv is None:
        argv = sys.argv

    parser = ArgumentParser(description=
    """
    """)
    parser.add_argument('-i', '--input', type=lambda p: Path(p, exists=True).absolute(), nargs='+', required=True,
                        help='Path(s) of HDF5 master file(s)')
    parser.add_argument('-b', '--beamcenter', type=int, nargs=2,
                        help='Beam center in X and Y (pixels)')
    parser.add_argument('-o', '--oscillation', type=float,
                        help='Oscillation per frame')
    parser.add_argument('-d', '--distance', type=float,
                        help='Detector distance in mm')
    parser.add_argument('-c', '--config_file', type=lambda p: Path(p, exists=True).absolute(),
                        help='json file containing configs; command line args override')
    parser.add_argument('-r', '--oscillationperwell', type=float,
                        help='Oscillation angle per well')
    parser.add_argument('-w', '--wavelength', type=float,
                        help='Wavelength in Angstrom')
    parser.add_argument('-s','--spacegroup', type=int, default=0,
                        help='Space group number to be used in indexing, default is to determine SG automatically')
    parser.add_argument('-u', '--unitcell', type=str, default="100 100 100 90 90 90",
                        help='Unit cell to be used in indexing')                  
    parser.add_argument('-l', '--library', type=str, default=neggia_path,
                        help='Location of Dectris Neggia library')
    parser.add_argument('-m', '--totalframes', type=int,
                        help='Number of max frames to process (default all frames)')
    parser.add_argument('--frontoffset', type=int, default=0,
                        help='skip first n frames per well if e.g. shutter shadowed')
    parser.add_argument('--backoffset', type=int, default=0,
                        help='skip last n frames per well if e.g. radiation damage')
    parser.add_argument('-j', '--njobs', type=int, default=1,
                        help='number of XDS jobs')
    parser.add_argument('-k', '--nproc', type=int, default=4,
                        help='number of XDS jobs')
    parser.add_argument('--outputdir', type=lambda p: Path(p, exists=True).absolute(), default=Path.cwd().absolute(),
                        help='Change output directory')
    parser.add_argument('--outputname', type=str, default="ssxoutput",
                        help='Change output directory')                        
    parser.add_argument('--reversephi', action='store_true',
                        help='Reverse phi oscillation')
    parser.add_argument('--xscale', action='store_true', help="Do XSCALE after processing")
    parser.parse_args()
    args = parser.parse_args()

    formatted_date = '{a:04d}{b:02d}{c:02d}_{d:02d}{e:02d}{f:02d}'.format(
                    a=date.year,b=date.month,c=date.day,d=date.hour,e=date.minute,f=date.second)
    output_directory = Path(args.outputdir / '{a}_{b}'.format(a=args.outputname, b=formatted_date))
    config.create_output_directory(output_directory)

    print("Output directory is {}".format(output_directory))
    sys.stdout.flush()

    output_dictionary = {}

    for masterfile in args.input:
        if not master.is_masterH5file(masterfile):
            sys.exit('not a valid master file')
        # Return number of data files linked to a master file:
        print('master file is: {}'.format(masterfile))
        master_class = master.Master(args, masterfile, output_directory)
        master_class.create_master_directory()
        cg = master_class.set_config()
        cg.write_config_to_file(master_class.get_master_directory_path())
        master_class.run()
        master_class.write_to_json()

        output_dictionary[master_class.get_master_directory_name()] = master_class.get_master_dictionary()
        Path( output_directory / 'results.json').write_text(json.dumps(output_dictionary, indent=2, cls=JSONEnc, sort_keys=True))

        #run scale.py if asked for
        if args.xscale:
            xsdir = scale.generate_xscale_directory(output_directory)
            scale.generate_xscaleINP(output_dictionary, args, xsdir)
            scale.run_xscale(xsdir)

    time2 = time.time()
    print("Total processing time: {:.1f} s".format(time2-time1))


if __name__=='__main__':
    main()

