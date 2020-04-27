import os, sys
import statistics, math
import json
from pathlib import Path
import subprocess
import shutil
from argparse import ArgumentParser

#return average and stdev of number of accepted reflections for a given dictionary
def avg_reflections(d):
    for entry, value in d.items():
        rlst = [y['accepted_reflections'] for (x,y) in value.items() if y['processing_successful'] and y['accepted_reflections'] is not None ]
    return statistics.mean(rlst), statistics.stdev(rlst)

#removes datasets with accepted reflections below some multiple of the stdev
def filter_datasets(d, threshold=2):
    l = {}
    avg, sd = avg_reflections(d)
    for entry, value in d.items():
        for entry2, value2 in value.items():
            if value2['accepted_reflections'] is not None and int(value2['accepted_reflections']) > avg - (threshold * sd) :
                l[entry2] = value2
    return l

def generate_xscale_directory(path):
    xs_path = Path(path / 'xscale')
    xs_path.mkdir(exist_ok=True)
    return xs_path

def get_xscale_directory(path):
    return Path(path / 'xscale')

def generate_xs_header(sg, unitcell, output_file="temp.ahkl"):
    return """OUTPUT_FILE={c}
SPACE_GROUP_NUMBER={a}
UNIT_CELL_CONSTANTS={b}
SAVE_CORRECTION_IMAGES=FALSE
WFAC1=1
PRINT_CORRELATIONS=FALSE\n""".format(a=sg, b=unitcell, c=output_file)

def generate_xscaleINP(d, args, xsdir):

    l = filter_datasets(d)

    if args.assert_P1 or args.spacegroup == 0:
        with open(Path(xsdir / 'XSCALE.INP'), 'w') as f:
            f.write(generate_xs_header(1, [y for x,y in l.items()][0]['unit_cell']))
            f.write(generate_xs_input(l))
    else:
        with open(Path(xsdir / 'XSCALE.INP'),'w') as f:
            f.write(generate_xs_header(args.spacegroup,args.unitcell))
            f.write(generate_xs_input(l))

def generate_xs_input(d):
    inputstr = """"""
    for entry, value in d.items():
        inputstr += "INPUT_FILE={}/XDS_ASCII.HKL\n".format(value['path'])
    return inputstr

def run_xscale(xsdir):
    # Run XDS in the datawell derectory:
    f = open(Path(xsdir / 'xscale.log'), "w")
    proc = subprocess.Popen(r"xscale_par", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, cwd=xsdir, text=True)
    for line in proc.stdout:
        sys.stdout.write(line)
        f.write(line)
    proc.wait()
    f.close()
    with open(Path(xsdir / 'XSCALE.LP'),'r') as f:
        line = f.readline()
        while not 'SUBSET OF INTENSITY DATA WITH SIGNAL/NOISE >= -3.0 AS FUNCTION OF RESOLUTION' in line:
            line = f.readline()
        while not 'total' in line:
            print(line, end='')
            line = f.readline()
        print(line)

def run_isocluster(xsdir,out='temp.ahkl'):
    f = open(Path(xsdir / 'xscale_isocluster.log'), "w")
    subprocess.call(r"xscale_isocluster {a}".format(a=out), stdout=f, shell=True, cwd=xsdir)
    f.close()

def sort_isocluster(xsdir):
    input_list = []
    try:
        with open(Path(xsdir / 'XSCALE.1.INP')) as f:
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

def filter_isocluster(input_list, threshold=0.6):
    result = []
    for line in input_list:
        if line[1] >= threshold:
            result.append(line)
    if len(result) == 0:
        sys.exit("Cluster strengths are too low for a reasonable solution.")
    return result

def copy_xscale_results(xsdir, suffix='old'):
    if Path(xsdir / 'XSCALE.INP').is_file():
        shutil.copy(Path(xsdir / 'XSCALE.INP'), Path(xsdir / 'XSCALE_{}.INP'.format(suffix)))
    if Path(xsdir / 'XSCALE.LP').is_file():
        shutil.copy(Path(xsdir / 'XSCALE.LP'), Path(xsdir / 'XSCALE_{}.LP'.format(suffix)))
    if Path(xsdir / 'XSCALE.log').is_file():
        shutil.copy(Path(xsdir / 'XSCALE.log'), Path(xsdir / 'XSCALE_{}.log'.format(suffix)))

def gen_sorted_xscaleINP(md_list, args, xsdir):
    with open(Path(xsdir / 'XSCALE_isocluster.INP'),'w') as f:
        f.write(generate_xs_header(args.spacegroup,args.unitcell))
        for line in md_list:
            f.write('{}\n'.format(line[0]))
            f.write('NBATCH=3 CORRECTIONS=ALL\n')

def rerun_xscale(xsdir):
    shutil.copy(Path(xsdir / 'XSCALE_isocluster.INP'), Path(xsdir / 'XSCALE.INP'))
    run_xscale(xsdir)

def dict_from_json(jsonfile):
    return json.load(open(jsonfile))

def main():
    parser = ArgumentParser(description=
    """
    Run xscale and xscale_isocluster.
    """)

    parser.add_argument('-i', '--input', type=lambda p: Path(p, exists=True).absolute(),
                        help='Path of restuls.json file')
    parser.add_argument('--assert_P1', action='store_true', help="Assert P1 Space Group")
    parser.add_argument('-s', '--spacegroup', type=int, help='Space Group Number')
    parser.add_argument('-u', '--unitcell', type=str, help='Unit Cell')
    parser.parse_args()
    args = parser.parse_args()

    xsdir = generate_xscale_directory(args.input.parent)
    d = dict_from_json(args.input)
    generate_xscaleINP(d, args, xsdir)
    run_xscale(xsdir)

if __name__=='__main__':
    main()
