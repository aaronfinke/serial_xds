Serial_xds: Data Processing in Serial Oscillation Crystallography
================

Introduction
----------------
serial_xds is a simple Python3.6 routine that process data for serial oscillation crystallography.

Usage
----------------
    usage: serial_xds.py [-h] [-i INPUT [INPUT ...]] [-b BEAMCENTER BEAMCENTER] [-o OSCILLATION] [-d DISTANCE] [-c CONFIG_FILE] [-r OSCILLATIONPERWELL] [-w WAVELENGTH] [-f FRAMESPERDEGREE] [-m MAXFRAMES] [-j JOBS] [--detector DETECTOR] [-k PROCESSORS] [--assert_P1] [--output OUTPUT]
    [--outputname OUTPUTNAME] [-g SPACEGROUP] [-u UNITCELL] [-l LIBRARY] [--scale]

    optional arguments:
      -h, --help            show this help message and exit
      -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                            Path of Directory containing HDF5 master file(s)
      -b BEAMCENTER BEAMCENTER, --beamcenter BEAMCENTER BEAMCENTER
                            Beam center in X and Y (pixels)
      -o OSCILLATION, --oscillation OSCILLATION
                            Oscillation per well to process
      -d DISTANCE, --distance DISTANCE
                            Detector distance in mm
      -c CONFIG_FILE, --config_file CONFIG_FILE
                            json file containing configs
      -r OSCILLATIONPERWELL, --oscillationperwell OSCILLATIONPERWELL
                            Oscillation angle per well
      -w WAVELENGTH, --wavelength WAVELENGTH
                            Wavelength in Angstrom
      -f FRAMESPERDEGREE, --framesperdegree FRAMESPERDEGREE
                            Number of frames per degree
      -m MAXFRAMES, --maxframes MAXFRAMES
                            Number of max frames to process (default all frames)
      -j JOBS, --jobs JOBS  Number of parallel XDS jobs (default 8)
      --detector DETECTOR   Detector used (default EIGER2 16M
      -k PROCESSORS, --processors PROCESSORS
                            Number of processors for XDS job (default num CPUs // 8
      --assert_P1           Assert P1 Space Group
      --output OUTPUT       Change output directory
      --outputname OUTPUTNAME
                            Change output directory
      -g SPACEGROUP, --spacegroup SPACEGROUP
                            Space group
      -u UNITCELL, --unitcell UNITCELL
                            Unit cell
      -l LIBRARY, --library LIBRARY
                            Location of Dectris Neggia library
      --scale               Do XSCALE after processing


Dependencies
--------------
serial_xds depends on:

* X-Ray Detector Software (XDS): [download from XDS website](http://xds.mpimf-heidelberg.mpg.de/)
* h5py, an HDF5 plugin for python: [download instructions here] (https://www.h5py.org/)
* xdsstat (available from [XDSwiki](https://strucbio.biologie.uni-konstanz.de/xdswiki/index.php/Xdsstat#Availability))
* Neggia plugin: [download from Dectris website](https://www.dectris.com/accounts/login/?next=/support/downloads/software/neggia/) this is not strictly necessary if you also have the H5toXds program in your PATH, but Neggia improves performance.
* For scaling and filtering of data, [XSCALE_ISOCLUSTER](https://strucbio.biologie.uni-konstanz.de/xdswiki/index.php/XSCALE_ISOCLUSTER) is also a useful tool to have.

Installation
---------------
Simply ensure that the XDS binaries are in your path.

Assumptions
---------------

* Data is in EIGER HDF5 format. This may work with other HDF5 files but they are not yet tested.
* Data is collected serially, <i>with oscillation</i>. This routine will not work with still images. Use [nXDS](http://nxds.mpimf-heidelberg.mpg.de/) for still processing.

Acknowledgements
-----------------
serial_xds was developed at Cornell High Energy Synchrotron Source (CHESS) for serial ossilation crystallography data processing. Tested at the MacCHESS ID7B2 beamline.
