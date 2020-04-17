#!/usr/bin/env python3

from pathlib import Path
import subprocess, os, re, sys
import json
from multiprocessing import Pool
import shutil
from argparse import ArgumentParser



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
    data = re.sub('JOB= XYCORR INIT COLSPOT IDXREF DEFPIX INTEGRATE CORRECT', '!JOB= XYCORR INIT COLSPOT IDXREF DEFPIX INTEGRATE CORRECT\nJOB= CORRECT', data)
    data = re.sub('SPACE_GROUP_NUMBER=.*', 'SPACE_GROUP_NUMBER={}'.format(args.spacegroup),data,re.DOTALL)
    data = re.sub('UNIT_CELL_CONSTANTS=.*', 'UNIT_CELL_CONSTANTS={}'.format(args.unitcell), data, re.DOTALL)
    Path(p / 'XDS.INP').write_text(data)


def rerun_xds(args, xdsdir):
    p = Path(xdsdir)
    print('rerunning XDS in {a} with SG {b} and unit cell {c}'.format(a=xdsdir, b= args.spacegroup, c=args.unitcell))
    copy_xds_results(p,'P1')
    update_xds_INP(p, args)
    with open(Path(p / 'XDS.log'), 'w') as f:
        subprocess.call(r"xds_par", stdout=f, shell=True, cwd=p)


def reprocess(args):
    d = gen_reproc_list(args.input)
    p = Pool()
    p.starmap(rerun_xds, [(args, xdsdir) for xdsdir in d])

def copy_xds_results(xdsdir, suffix='old'):
    if Path(xdsdir / 'XDS.INP').is_file():
        shutil.copy(Path(xdsdir / 'XDS.INP'), Path(xdsdir / 'XDS_{}.INP'.format(suffix)))
    if Path(xdsdir / 'XDS_ASCII.HKL').is_file():
        shutil.copy(Path(xdsdir / 'XDS_ASCII.HKL'), Path(xdsdir / 'XDS_ASCII_{}.HKL'.format(suffix)))
    if Path(xdsdir / 'XDS.log').is_file():
        shutil.copy(Path(xdsdir / 'XDS_ASCII.HKL'), Path(xdsdir / 'XDS_ASCII_{}.HKL'.format(suffix)))



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

    reprocess(args)



if __name__ == '__main__':
    main()
