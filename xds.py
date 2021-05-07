import json
from pathlib import Path
def gen_xds_text(UNIT_CELL_CONSTANTS, NAME_TEMPLATE_OF_DATA_FRAMES, ORGX, ORGY,
                DETECTOR_DISTANCE, OSCILLATION_RANGE, X_RAY_WAVELENGTH, DATA_RANGE,
                BACKGROUND_RANGE, SPOT_RANGE, LIB, SPACE_GROUP_NUMBER, ):
    dataframes = "??????".join((str(NAME_TEMPLATE_OF_DATA_FRAMES).rsplit("master", 1)))
    text = f"""
SPACE_GROUP_NUMBER={SPACE_GROUP_NUMBER}
UNIT_CELL_CONSTANTS= {UNIT_CELL_CONSTANTS}
NAME_TEMPLATE_OF_DATA_FRAMES= {NAME_TEMPLATE_OF_DATA_FRAMES}
JOB= XYCORR INIT COLSPOT IDXREF DEFPIX INTEGRATE CORRECT
ORGX= {ORGX}  ORGY= {ORGY}
DETECTOR_DISTANCE= {DETECTOR_DISTANCE}
OSCILLATION_RANGE= {OSCILLATION_RANGE}
X-RAY_WAVELENGTH= {X_RAY_WAVELENGTH}
DATA_RANGE= {DATA_RANGE}
BACKGROUND_RANGE= {BACKGROUND_RANGE}
SPOT_RANGE= {SPOT_RANGE}
{LIB}
DETECTOR= EIGER MINIMUM_VALID_PIXEL_VALUE=0 OVERLOAD= 35187210
SENSOR_THICKNESS= 0.45
NX= 4148 NY= 4362  QX= 0.075  QY= 0.075

TRUSTED_REGION=0.0 1.2
DIRECTION_OF_DETECTOR_X-AXIS= 1.0 0.0 0.0
DIRECTION_OF_DETECTOR_Y-AXIS= 0.0 1.0 0.0
MAXIMUM_NUMBER_OF_JOBS= 
MAXIMUM_NUMBER_OF_PROCESSORS= 
ROTATION_AXIS= -1.0 0.0 0.0
INCIDENT_BEAM_DIRECTION=0.0 0.0 1.0
FRACTION_OF_POLARIZATION=0.99
POLARIZATION_PLANE_NORMAL= 0.0 1.0 0.0
REFINE(IDXREF)=BEAM AXIS ORIENTATION CELL  ! POSITION
REFINE(INTEGRATE)= ORIENTATION POSITION BEAM ! CELL AXIS
REFINE(CORRECT)=POSITION BEAM ORIENTATION CELL AXIS
VALUE_RANGE_FOR_TRUSTED_DETECTOR_PIXELS= 6000 30000
!INCLUDE_RESOLUTION_RANGE=50 1.8
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

    """
    return text

def xds_from_json():
    with open(Path(Path(__file__).parent/ "xds_def.json")) as f:
        xds_json = json.load(f)
    return xds_json

def get_detector_params(det):
    with open(Path(Path(__file__).parent/"detectors.json")) as f:
        det_json = json.load(f)
    for item in det_json:
        if item == det:
            det_dict = det_json[item]
    return det_dict


def get_xds_params(args):
    xds_params = xds_from_json()
    xds_params['ORGX']['value'] = args.beamcenter[0]
    xds_params['ORGY']['value'] = args.beamcenter[1]
    xds_params['DETECTOR_DISTANCE']['value'] = args.distance
    xds_params['X-RAY_WAVELENGTH']['value'] = args.wavelength
    xds_params['OSCILLATION_RANGE']['value'] = "{:.2f}".format(1/args.framesperdegree)
    xds_params['MAXIMUM_NUMBER_OF_JOBS']['value'] = args.jobs
    xds_params['MAXIMUM_NUMBER_OF_PROCESSORS']['value'] = args.processors
    xds_params['SPACE_GROUP_NUMBER']['value'] = args.spacegroup
    xds_params['UNIT_CELL_CONSTANTS']['value'] = args.unitcell
    if args.library:
        xds_params['LIB']['value'] = args.library
        xds_params['LIB']['required'] = True
    return xds_params

def get_library_path(self):
    if not self.args.library:
        return "!LIB="
    else:
        return f"LIB= {self.args.library}"

def gen_XDS_INP(framepath, masterpath, d_b_s_range, xds_params, det_params):
    template_path = "??????".join((str(masterpath).rsplit("master", 1)))
    with open(Path(framepath / 'XDS.INP'), 'w') as f:
        f.write(f"NAME_TEMPLATE_OF_DATA_FRAMES= {template_path}\n")
        f.write(f"BACKGROUND_RANGE= {d_b_s_range}\n")
        f.write(f"SPOT_RANGE= {d_b_s_range}\n")
        f.write(f"DATA_RANGE= {d_b_s_range}\n")
        for item in xds_params:
            if xds_params[item]['required']:
                f.write(f"{item}= {xds_params[item]['value']}\n")
        for item in det_params:
            if item == "UNTRUSTED_RECTANGLE":
                continue
            f.write(f"{item}= {det_params[item]}\n")
            for rect in det_params["UNTRUSTED_RECTANGLE"]:
                f.write(f"UNTRUSTED_RECTANGLE= {rect}\n")
