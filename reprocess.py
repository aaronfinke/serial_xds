#!/usr/bin/env python3

from pathlib import Path
import subprocess, os, re, sys
import json
from multiprocessing import Pool, Manager
import shutil
from argparse import ArgumentParser
from jsonenc import JSONEnc

def json_to_dict(jsonfile):
    assert jsonfile.is_file(), "JSON File does not exist or cannot be loaded"
    d = json.load(open(jsonfile))
    return d

def gen_reproc_list(jsonfile):
    '''makes a list of directories to reprocess'''
    d = []
    for k,v in json_to_dict(jsonfile).items():
        for x,y in v.items():
            if (y['processing_successful']):
                d.append(y['path'])
    return d

def update_xds_INP(p,args):
    with open(Path( p / 'XDS.INP'), 'r') as source:
            data='\n'.join(line.rstrip() for line in source)
    data = re.sub('JOB=.*', 'JOB= CORRECT', data,re.DOTALL)
    data = re.sub('SPACE_GROUP_NUMBER=.*', 'SPACE_GROUP_NUMBER={}'.format(args.spacegroup),data,re.DOTALL)
    data = re.sub('UNIT_CELL_CONSTANTS=.*', 'UNIT_CELL_CONSTANTS={}'.format(args.unitcell), data, re.DOTALL)
    Path(p / 'XDS.INP').write_text(data)


def rerun_xds(args, xdsdir, mdict):
    p = Path(xdsdir)
#    print('rerunning XDS in {a} with SG {b} and unit cell {c}'.format(a=xdsdir, b= args.spacegroup, c=args.unitcell))
    copy_xds_results(p,'P1')
    update_xds_INP(p, args)
    with open(Path(p / 'XDS.log'), 'w') as f:
        subprocess.call(r"xds_par", stdout=f, shell=True, cwd=p)

def get_accepted_reflections(xdsdir):
    with Path(xdsdir / 'CORRECT.LP').open() as file:
        for line in file:
            if 'NUMBER OF ACCEPTED OBSERVATIONS (INCLUDING SYSTEMATIC ABSENCES' in line:
                value = re.search(r'\d+',line)
                return int(value.group(0))

def get_spacegroup(xdsdir):
    with Path(xdsdir / 'XDS_ASCII.HKL').open() as file:
        for line in file:
            if '!SPACE_GROUP_NUMBER=' in line:
                return line.split()[-1]
    return None

def get_unitcell(xdsdir):
    with Path(xdsdir / 'XDS_ASCII.HKL').open() as file:
        for line in file:
            if '!UNIT_CELL_CONSTANTS=' in line:
                l = line.split()
                return '{a} {b} {c} {al} {be} {ga}'.format(a=l[-6], b=l[-5], c=l[-4], al=l[-3], be=l[-2], ga=l[-1])
    return None

def reprocess(args):
    d = gen_reproc_list(args.input)
    pool = Pool()
    for xdsdir in d:
        xdsdir = Path(xdsdir)
        pool.apply_async(rerun_xds, args=(args,xdsdir))
        #convoluted method for managed dict updating, this is a Python bug
        mdict_xdsdir_parent_name = mdict[xdsdir.parent.name]
        mdict_xdsdir_parent_name_xdsdir_name = mdict_xdsdir_parent_name[xdsdir.name]
        mdict_xdsdir_parent_name_xdsdir_name['accepted_reflections'] = get_accepted_reflections(xdsdir)
        mdict_xdsdir_parent_name_xdsdir_name['space_group'] = get_spacegroup(xdsdir)
        mdict_xdsdir_parent_name_xdsdir_name['unit_cell'] = get_unitcell(xdsdir)
        mdict_xdsdir_parent_name[xdsdir.name] = mdict_xdsdir_parent_name_xdsdir_name
        mdict[xdsdir.parent.name] = mdict_xdsdir_parent_name

    pool.close()
    pool.join()


def copy_xds_results(xdsdir, suffix='old'):
    if Path(xdsdir / 'XDS.INP').is_file():
        shutil.copy(Path(xdsdir / 'XDS.INP'), Path(xdsdir / 'XDS_{}.INP'.format(suffix)))
    if Path(xdsdir / 'XDS_ASCII.HKL').is_file():
        shutil.copy(Path(xdsdir / 'XDS_ASCII.HKL'), Path(xdsdir / 'XDS_ASCII_{}.HKL'.format(suffix)))
    if Path(xdsdir / 'XDS.log').is_file():
        shutil.copy(Path(xdsdir / 'XDS.log'), Path(xdsdir / 'XDS_{}.log'.format(suffix)))

def write_to_json(args, mdict):
    Path(args.input.parent / 'results_{b}.json'.format(b='reprocessed')).write_text(
        json.dumps(mdict.copy(), indent=2, sort_keys=True, cls=JSONEnc))


def main():
    parser = ArgumentParser(description=
    """
    Reprocess XDS data in chosen space group and unit cell.
    results.json file required
    """)

    parser.add_argument('-i', '--input', type=lambda p: Path(p, exists=True).absolute(),
                        help='Path of restuls.json file')
    parser.add_argument('-s', '--spacegroup', type=int, help='Space Group Number')
    parser.add_argument('-u', '--unitcell', type=str, help='Unit Cell')
    parser.parse_args()
    args = parser.parse_args()
    global mdict
    mdict = Manager().dict()
    mdict.update(json.load(open(args.input)))

    reprocess(args)
    write_to_json(args, mdict)

if __name__ == '__main__':
    main()
