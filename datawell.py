#!/usr/bin/env python3

import subprocess, os, re, sys
import json
from generate_xds import gen_xds_text


class Datawell(object):

    # Generating a constructor for the class:
    def __init__(self, first_frame, last_frame, master_directory, masterpath, args):
        self.ff = first_frame
        self.lf = last_frame
        self.master_dir = master_directory
        self.masterpath = masterpath
        self.args = args
        self.frames = '{a}_{b}'.format(a=self.ff,b=self.lf)
        self.oscillation_per_frame = "{:.2f}".format(1/args.framesperdegree)
        self.dwdict = {}

        # Variables defined within class:
        self.framepath = "{d}/{start:04d}_{end:04d}".format(d=self.master_dir, start=self.ff, end=self.lf)

    def setup_datawell_directory(self):
        # Generate datawell directory:
        try:
            os.makedirs(self.framepath)
        except:
            sys.exit(1)

    def gen_XDS(self):
        # Generating XDS file in datawell directory:
        try:
            d_b_s_range = "{a} {b}".format(a=self.ff, b=self.lf)
            with open(os.path.join(self.framepath, 'XDS.INP'), 'w') as input:
                input.write(gen_xds_text(self.args.unitcell, self.masterpath,
                self.args.beamcenter[0], self.args.beamcenter[1], self.args.distance, self.oscillation_per_frame,
                self.args.wavelength, d_b_s_range, d_b_s_range, d_b_s_range, self.args.library))
        except:
            print("IO ERROR")

    def run(self):
        # Run XDS in the datawell derectory:
        f = open(os.path.join(self.framepath,'XDS.log'), "w")
        subprocess.call(r"xds_par", stdout=f, shell=True, cwd=self.framepath)
        f.close()
        self.set_dwdict()

    def set_dwdict(self):
        self.dwdict['first frame'] = self.ff
        self.dwdict['last frame'] = self.lf
        if os.path.exists(os.path.join(self.framepath,'XDS_ASCII.HKL')):
            self.dwdict['processing_successful'] = True
            with open(os.path.join(self.framepath,'CORRECT.LP')) as file:
                for line in file:
                    if 'NUMBER OF ACCEPTED OBSERVATIONS (INCLUDING SYSTEMATIC ABSENCES' in line:
                        value = re.search(r'\d+',line)
                        self.dwdict['accepted_reflections']=value.group(0)
        else:
            self.dwdict['processing_successful'] = False
            self.dwdict['accepted_reflections'] = None
            self.dwdict['error_message'] = self.check_error()

    def check_error(self):
        with open(os.path.join(self.framepath,'XDS.log')) as f:
            for line in f:
                if "!!! ERROR" in line:
                    return " ".join((line.split("!!!")[-1]).split())

    def get_dw_dict(self):
        return self.dwdict

    def write_to_json(self):
        go_json = json.dumps(self.dwdict)
        with open(os.path.join('{}'.format(self.framepath), 'results.json'), 'w') as file:
            file.write(go_json)

    def getframes(self):
        return '{a:04d}_{b:04d}'.format(a=self.ff,b=self.lf)
