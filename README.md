Serial_xds: Data Processing in Serial Oscillation Crystallography
================

Introduction
----------------
serial_xds is a python program that process data for serail osscilation crystallography

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

* X-Ray Detectore Software (XDS)
* Neggia plugin (available from Dectris website)
* xdsstat (available from [XDSwiki](https://strucbio.biologie.uni-konstanz.de/xdswiki/index.php/Xdsstat#Availability))

Installation
---------------
If files are on your locar machine, no work is needed.

Assumptions
---------------

* EIGER HDF5 data
* Data is collected serially, 5 frames per datawell (0.2<sup> o</sup> / frame)
