import os, sys
import statistics, math
import json
from pathlib import Path
import subprocess
import shutil

#return average and stdev of number of accepted reflections for a given dictionary
def avg_reflections(d):
    rlst = [y['accepted_reflections'] for (x,y) in d.items() if y['processing_successful'] ]
    return statistics.mean(rlst), statistics.stdev(rlst)

#removes datasets with accepted reflections below some multiple of the stdev
def filter_datasets(d, threshold=1):
    l = {}
    avg, sd = avg_reflections(d)
    for entry, value in d.items():
        if value['accepted_reflections'] is not None and int(value['accepted_reflections']) > avg - (threshold * sd) :
            l[entry] = value
    return l

def generate_xscale_directory(path):
    xs_path = os.path.join(path, 'xscale')
    os.mkdir(xs_path)
    return xs_path

def get_xscale_directory(path):
    return os.path.join(path, 'xscale')

def generate_xs_header(sg, unitcell, output_file="temp.ahkl"):
    return """OUTPUT_FILE={c}
!SPACE_GROUP_NUMBER={a}
!UNIT_CELL_CONSTANTS={b}
SAVE_CORRECTION_IMAGES=FALSE
WFAC1=1
PRINT_CORRELATIONS=FALSE\n""".format(a=sg, b=unitcell, c=output_file)

def generate_xs_input(d):
    inputstr = """"""
    for entry, value in d.items():
        inputstr += "INPUT_FILE={}/XDS_ASCII.HKL\n".format(value['path'])
    return inputstr

def generate_xscaleINP(md_list, args, xsdir):
    with open(os.path.join(xsdir,'XSCALE.INP'),'w') as f:
        f.write(generate_xs_header(args.spacegroup,args.unitcell))
        for d in md_list:
            l = filter_datasets(d)
            f.write(generate_xs_input(l))

def run_xscale(xsdir):
    # Run XDS in the datawell derectory:
    f = open(os.path.join(xsdir,'xscale.log'), "w")
    subprocess.call(r"xscale_par", stdout=f, shell=True, cwd=xsdir)
    f.close()

def run_isocluster(xsdir,out):
    f = open(os.path.join(xsdir,'xscale_isocluster.log'), "w")
    subprocess.call(r"xscale_isocluster {a}".format(a=out), stdout=f, shell=True, cwd=xsdir)
    f.close()

def sort_isocluster(xsdir):
    input_list = []
    try:
        with open('XSCALE.1.INP') as f:
            line = f.readline()
            while line:
                if line.startswith('INPUT_FILE'):
                    inp = line.rstrip()
                    line = f.readline()
                    x = line.split()
                    y = float(x[6]) * math.cos(float(x[7])*(3.14159/180))
                    input_list.append([inp, y, x[8]])
                else:
                    line = f.readline()
        result = sorted(input_list, key=lambda x:(x[1] ), reverse=True)
    except:
        sys.exit("XSCALE_isocluster failed.")
    return result

def filter_isocluster(list, threshold=0.6):


def copy_xscale_results(xsdir, suffix='old'):
    if Path(xsdir / 'XSCALE.INP').is_file():
        shutil.copy(Path(xsdir / 'XSCALE.INP'), Path(xsdir / 'XSCALE_{}.INP'.format(suffix)))
    if Path(xsdir / 'XSCALE.LP').is_file():
        shutil.copy(Path(xsdir / 'XSCALE.INP'), Path(xsdir / 'XSCALE_{}.INP'.format(suffix)))


def gen_sorted_xscaleINP(md_list, args, xsdir)
    with open(os.path.join(xsdir,'XSCALE.INP'),'w') as f:
        f.write(generate_xs_header(args.spacegroup,args.unitcell))
        for line in md_list:
            f.write(md_list[0])
            
