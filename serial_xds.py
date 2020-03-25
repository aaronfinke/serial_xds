import argparse, fnmatch, os, h5py, time
import logging, sys
import master

def main():

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    streamhandler = logging.StreamHandler(sys.stdout)
    filehandler = logging.FileHandler(filename='tmp.log')
    handlers=[streamhandler, filehandler]
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
        handlers=handlers
        )
    root.addHandler(streamhandler)
    root.addHandler(filehandler)

    time1=time.time()
    parser = argparse.ArgumentParser(description='Arguments required to process the data: input, beamcenter, distance.')

    parser.add_argument('-i', '--input', type=str, nargs='+', required=True, help='Path of Directory containing HDF5 master file(s)')

    parser.add_argument('-b', '--beamcenter', type=int, nargs=2, required=True, help='Beam center in X and Y')

    parser.add_argument('-r', '--oscillations', type=float, default=1, help='Oscillation angle per well')

    parser.add_argument('-d', '--distance', type=float, required=True, help='Detector distance in mm')

    parser.add_argument('-w', '--wavelength', type=float, default=1.216, help='Wavelength in Angstrom')

    parser.add_argument('-f', '--framesperdegree', type=int, default=5, help='Number of frames per degree')

    parser.add_argument('--output', default=os.getcwd(), help='Use this option to change output directly')

    parser.add_argument('-sg', '--spacegroup', help='Space group')

    parser.add_argument('-u', '--unitcell', type=str, default="100 100 100 90 90 90", help='Unit cell')

    parser.parse_args()

    args = parser.parse_args()

    # Get all master files from the given path and create a list:
    for masterdir in args.input:
        master_list = fnmatch.filter(os.listdir(masterdir), "*master.h5")
        print(master_list)
        for masterfile in master_list:
            # Return number of data files linked to a master file:
            masterpath = "{}/{}".format(masterdir, masterfile)
            totalframes = master.get_number_of_files(masterpath)

            # Each master file in the list now used to create an instance of a class called 'Master' (from master.py):
            master_class = master.Master(args, masterpath, totalframes)

    time2 = time.time()
    print("Total time: {:.1f} s".format(time2-time1))
if __name__=='__main__':
    main()
