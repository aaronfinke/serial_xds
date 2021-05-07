import json
from pathlib import Path

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
                for rect in det_params["UNTRUSTED_RECTANGLE"]:
                    f.write(f"UNTRUSTED_RECTANGLE= {rect}\n")
            else:
                f.write(f"{item}= {det_params[item]}\n")
