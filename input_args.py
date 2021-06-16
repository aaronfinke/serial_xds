from argparse import ArgumentParser
import h5py
import os, sys
from pathlib import Path
from jsonenc import JSONEnc
import master
import json

def parse_args(args):
    '''
    Parses command line arguments, then reads a config file, then fills in the blanks with
    metadata from h5 file 
    '''
    parser = ArgumentParser(description=
    """
    """)
    parser.add_argument('-i', '--input', type=lambda p: Path(p, exists=True).absolute(), nargs='+',
                        help='Path of Directory containing HDF5 master file(s)')
    parser.add_argument('-b', '--beamcenter', type=int, nargs=2,
                        help='Beam center in X and Y (pixels)')
    parser.add_argument('-o', '--oscillation', type=float,
                        help='Oscillation per well to process')
    parser.add_argument('-d', '--distance', type=float,
                        help='Detector distance in mm')
    parser.add_argument('-c', '--config_file', type=lambda p: Path(p, exists=True).absolute(),
                        help='json file containing configs')
    parser.add_argument('-r', '--oscillationperwell', type=float,
                        help='Total oscillation per well')
    parser.add_argument('-w', '--wavelength', type=float, default=1.216,
                        help='Wavelength in Angstrom')
    parser.add_argument('-f', '--framesperdegree', type=int, default=5,
                        help='Number of frames per degree')
    parser.add_argument('-m', '--maxframes', type=int,
                        help='Number of max frames to process (default all frames)')
    parser.add_argument('-j', '--jobs', type=int, default=8,
                        help='Number of parallel XDS jobs (default 8)')
    parser.add_argument('--detector', type=str, default="EIGER2_16M",
                        help="Detector used (default EIGER2 16M")
    parser.add_argument('-k','--processors', type=int, default=os.cpu_count() // 8,
                        help='Number of processors for XDS job (default num CPUs // 8')
    parser.add_argument('--assert_P1', action='store_true', help="Assert P1 Space Group")
    parser.add_argument('--output', type=lambda p: Path(p, exists=True).absolute(), default=Path.cwd().absolute(),
                        help='Change output directory')
    parser.add_argument('--outputname', type=str, default="ssxoutput",
                        help='Change output directory')
    parser.add_argument('-g', '--spacegroup', default=0,
                        help='Space group')
    parser.add_argument('-u', '--unitcell', type=str, default="100 100 100 90 90 90",
                        help='Unit cell')
    parser.add_argument('-l', '--library', type=str,
                        help='Location of library for XDS')
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
    return args