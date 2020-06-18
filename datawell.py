#!/usr/bin/env python3

import subprocess, os, re, sys
import json
from generate_xds import gen_xds_text
from pathlib import Path
from jsonenc import JSONEnc


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
        self.framepath = Path(self.master_dir / '{start:04d}_{end:04d}'.format(start=self.ff, end=self.lf))

    def setup_datawell_directory(self):
        # Generate datawell directory:
        try:
            self.framepath.mkdir()
        except:
            sys.exit('Datawell directory creation failed.')

    def get_dw_path(self):
        return self.framepath

    def gen_XDS(self):
        # Generating XDS file in datawell directory:
        try:
            d_b_s_range = "{a} {b}".format(a=int(self.ff)+4, b=self.lf)
            Path(self.framepath / 'XDS.INP').write_text(gen_xds_text(self.args.unitcell, self.masterpath,
                self.args.beamcenter[0], self.args.beamcenter[1], self.args.distance, self.oscillation_per_frame,
                self.args.wavelength, d_b_s_range, d_b_s_range, d_b_s_range, self.args.library, self.args.spacegroup))
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            sys.exit("File could not be written.")

    def run(self):
        # Run XDS in the datawell derectory:
        with open(Path(self.framepath / 'XDS.log'), 'w') as f:
            subprocess.call(r"xds_par", stdout=f, shell=True, cwd=self.framepath)
        self.set_dwdict()

    def check_and_rerun(self):
        '''IDXREF fails and XDS stops when less than 50% of reflections are indexed. This ensures those datasets
        get integrated too.
        '''
        if not self.dwdict['processing_successful']:
            if 'INSUFFICIENT PERCENTAGE' in self.dwdict['error_message']:
                self.update_XDS_INP_afterIDXREFfail()
                with open(Path(self.framepath / 'XDS.log'), 'a') as f:
                    subprocess.call(r"xds_par", stdout=f, shell=True, cwd=self.framepath)
                self.set_dwdict()
        else:
            return

    def update_XDS_INP_afterIDXREFfail(self):
        '''IDXREF fails and XDS stops when less than 50% of reflections are indexed. This ensures those datasets
        get integrated too.
        '''
        with open(Path(self.framepath / 'XDS.INP'), 'r') as source:
                data='\n'.join(line.rstrip() for line in source)
        data = re.sub('JOB=.*', 'JOB= DEFPIX INTEGRATE CORRECT', data,re.DOTALL)
        Path(self.framepath / 'XDS.INP').write_text(data)


    def set_dwdict(self):
        self.dwdict['first frame'] = self.ff
        self.dwdict['last frame'] = self.lf
        self.dwdict['path'] = str(self.framepath)
        if Path(self.framepath / 'XDS_ASCII.HKL').exists():
            self.dwdict['processing_successful'] = True
            self.dwdict['accepted_reflections'] = self.get_number_of_reflections(self.framepath)
            self.dwdict['space_group'] = self.get_spacegroup(self.framepath)
            self.dwdict['unit_cell'] = self.get_unitcell(self.framepath)

        else:
            self.dwdict['processing_successful'] = False
            self.dwdict['accepted_reflections'] = None
            self.dwdict['error_message'] = self.check_error()

    def get_number_of_reflections(self, framepath):
        with Path(framepath / 'CORRECT.LP').open() as file:
            for line in file:
                if 'NUMBER OF ACCEPTED OBSERVATIONS (INCLUDING SYSTEMATIC ABSENCES' in line:
                    value = re.search(r'\d+',line)
                    return int(value.group(0))
        return None

    def get_spacegroup(self,framepath):
        with Path(framepath / 'XDS_ASCII.HKL').open() as file:
            for line in file:
                if '!SPACE_GROUP_NUMBER=' in line:
                    return line.split()[-1]
        return None

    def get_unitcell(self,framepath):
        with Path(framepath / 'XDS_ASCII.HKL').open() as file:
            for line in file:
                if '!UNIT_CELL_CONSTANTS=' in line:
                    l = line.split()
                    return '{a} {b} {c} {al} {be} {ga}'.format(a=l[-6], b=l[-5], c=l[-4], al=l[-3], be=l[-2], ga=l[-1])
        return None


    def check_error(self):
        with Path(self.framepath / 'XDS.log').open() as f:
            for line in f:
                if "!!! ERROR" in line:
                    return " ".join((line.split("!!!")[-1]).split())

    def get_dw_dict(self):
        return self.dwdict

    def write_to_json(self):
        Path(self.framepath / 'results.json').write_text(json.dumps(self.dwdict, cls=JSONEnc))

    def getframes(self):
        return '{a:04d}_{b:04d}'.format(a=self.ff,b=self.lf)
