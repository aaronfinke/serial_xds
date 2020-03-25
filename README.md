Serial_xds: Data Processing in Serial Oscillation Crystallography
================

Introduction
----------------
serial_xds is a simple Python3.6 routine that process data for serial oscillation crystallography.

Usage
----------------
    serial_xds.py -h
    usage: serial_xds.py [-h] -i INPUT [INPUT ...] -b BEAMCENTER BEAMCENTER
                         [-r OSCILLATIONS] -d DISTANCE [-w WAVELENGTH]
                         [-f FRAMESPERDEGREE] [--output OUTPUT] [-sg SPACEGROUP]
                         [-u UNITCELL]

    Arguments required to process the data: input, beamcenter, distance.

    optional arguments:
      -h, --help            show this help message and exit
      -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                            Path of Directory containing HDF5 master file(s)
      -b BEAMCENTER BEAMCENTER, --beamcenter BEAMCENTER BEAMCENTER
                            Beam center in X and Y
      -r OSCILLATIONS, --oscillations OSCILLATIONS
                            Oscillation angle per well
      -d DISTANCE, --distance DISTANCE
                            Detector distance in mm
      -w WAVELENGTH, --wavelength WAVELENGTH
                            Wavelength in Angstrom
      -f FRAMESPERDEGREE, --framesperdegree FRAMESPERDEGREE
                            Number of frames per degree
      --output OUTPUT       Use this option to change output directly
      -sg SPACEGROUP, --spacegroup SPACEGROUP
                            Space group
      -u UNITCELL, --unitcell UNITCELL
                            Unit cell

Computer system with two or more processing units is required to leverage parallel operation in master.py script.

Dependencies
--------------
serial_xds depends on:

* X-Ray Detector Software (XDS): [download from XDS website](http://xds.mpimf-heidelberg.mpg.de/)
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
