#!/usr/bin/env python3

import subprocess, os, re, sys
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

        # Variables defined within class:
        self.framepath = "{d}/{start}_{end}".format(d=self.master_dir, start=self.ff, end=self.lf)

    def setup_datawell_directory(self):
        # Generate datawell directory:
        try:
            os.makedirs(self.framepath)
        except OSError:
            print("Failed to create datawell directory")
            sys.exit()


    def gen_XDS(self):
        # Generating XDS file in datawell directory:
        try:
            d_b_s_range = "{a} {b}".format(a=self.ff, b=self.lf)
            with open(os.path.join(self.framepath, 'XDS.INP'), 'x') as input:
                input.write(gen_xds_text(self.args.unitcell, self.masterpath,
                self.args.beamcenter[0], self.args.beamcenter[1], self.args.distance, self.args.oscillation,
                self.args.wavelength, d_b_s_range, d_b_s_range, d_b_s_range, self.args.library))
        except:
            print("IO ERROR")

    def run(self):
        # Run XDS in the datawell derectory:
        os.chdir(self.framepath)
        f = open("XDS.log", "w")
        subprocess.call(r"xds_par", stdout=f)
        f.close()

    def gen_datawell_dict(self):
        dw_dict = {}
        dw_dict['first frame'] = self.ff
        dw_dict['last frame'] = self.lf
        if os.path.exists('XDS_ASCII.HKL'):
            dw_dict['processing_successful'] = True
            with open('CORRECT.LP') as file:
                for line in file:
                    if 'NUMBER OF ACCEPTED OBSERVATIONS (INCLUDING SYSTEMATIC ABSENCES' in line:
                        value = re.search(r'\d+',line)
                        dw_dict['accepted_reflections']=value.group(0)
        else:
            dw_dict['processing_successful'] = False
            dw_dict['accepted_reflections'] = None
        return dw_dict

    def getframes(self):
        return '{a}_{b}'.format(a=self.ff,b=self.lf)

    def close(self):
        if os.path.exists('XDS_ASCII.HKL'):
            print("{}: FRAMES {}-{} ... done".format(self.master_dir, self.ff, self.lf))
        else:
            print("{}: FRAMES {}-{} ... failed".format(self.master_dir, self.ff, self.lf))
        os.chdir(self.master_dir)
