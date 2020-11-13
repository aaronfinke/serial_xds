import json
from pathlib import Path
def gen_xds_text(UNIT_CELL_CONSTANTS, NAME_TEMPLATE_OF_DATA_FRAMES, ORGX, ORGY,
                DETECTOR_DISTANCE, OSCILLATION_RANGE, X_RAY_WAVELENGTH, DATA_RANGE,
                BACKGROUND_RANGE, SPOT_RANGE, LIB):
    dataframes = "??????".join((str(NAME_TEMPLATE_OF_DATA_FRAMES).rsplit("master", 1)))
    text = """
SPACE_GROUP_NUMBER=0
UNIT_CELL_CONSTANTS= {in_1}
NAME_TEMPLATE_OF_DATA_FRAMES= {in_2}
JOB= XYCORR INIT COLSPOT IDXREF DEFPIX INTEGRATE CORRECT
ORGX= {in_3}  ORGY= {in_4}
DETECTOR_DISTANCE= {in_5}
OSCILLATION_RANGE= {in_6}
X-RAY_WAVELENGTH= {in_7}
DATA_RANGE= {in_8}
BACKGROUND_RANGE= {in_9}
SPOT_RANGE= {in_10}
LIB={in_11}
DETECTOR= EIGER MINIMUM_VALID_PIXEL_VALUE=0 OVERLOAD= 68947
SENSOR_THICKNESS= 0.45
NX= 4148 NY= 4362  QX= 0.075  QY= 0.075

TRUSTED_REGION=0.0 1.2
DIRECTION_OF_DETECTOR_X-AXIS= 1.0 0.0 0.0
DIRECTION_OF_DETECTOR_Y-AXIS= 0.0 1.0 0.0
MAXIMUM_NUMBER_OF_JOBS=4
MAXIMUM_NUMBER_OF_PROCESSORS=8
ROTATION_AXIS= 0.0 -1.0 0.0
INCIDENT_BEAM_DIRECTION=0.0 0.0 1.0
FRACTION_OF_POLARIZATION=0.99
POLARIZATION_PLANE_NORMAL= 0.0 1.0 0.0
REFINE(IDXREF)=BEAM AXIS ORIENTATION CELL  ! POSITION
REFINE(INTEGRATE)= ORIENTATION POSITION BEAM ! CELL AXIS
REFINE(CORRECT)=POSITION BEAM ORIENTATION CELL AXIS
VALUE_RANGE_FOR_TRUSTED_DETECTOR_PIXELS= 6000 30000
! INCLUDE_RESOLUTION_RANGE=50 1.8
MINIMUM_I/SIGMA=50.0
CORRECTIONS= !
MINIMUM_FRACTION_OF_INDEXED_SPOTS=0.5
SEPMIN=4.0
INDEX_ERROR=0.1 INDEX_MAGNITUDE=8 INDEX_QUALITY=0.8
CLUSTER_RADIUS=2
MINIMUM_NUMBER_OF_PIXELS_IN_A_SPOT=3
UNTRUSTED_RECTANGLE= 1028 1041      0 4363
UNTRUSTED_RECTANGLE= 2068 2081      0 4363
UNTRUSTED_RECTANGLE= 3108 3121      0 4363
UNTRUSTED_RECTANGLE=    0 4149    512  551
UNTRUSTED_RECTANGLE=    0 4149   1062 1101
UNTRUSTED_RECTANGLE=    0 4149   1612 1651
UNTRUSTED_RECTANGLE=    0 4149   2162 2201
UNTRUSTED_RECTANGLE=    0 4149   2712 2751
UNTRUSTED_RECTANGLE=    0 4149   3262 3301
UNTRUSTED_RECTANGLE=    0 4149   3812 3851
NUMBER_OF_PROFILE_GRID_POINTS_ALONG_ALPHA/BETA=13
NUMBER_OF_PROFILE_GRID_POINTS_ALONG_GAMMA=13

    """.format(in_1=UNIT_CELL_CONSTANTS, in_2=dataframes, in_3=ORGX, in_4=ORGY,
    in_5=DETECTOR_DISTANCE, in_6=OSCILLATION_RANGE, in_7=X_RAY_WAVELENGTH, in_8=DATA_RANGE, in_9=BACKGROUND_RANGE,
    in_10=SPOT_RANGE, in_11=LIB)
    return text

def xds_from_json(json_file):
    return
