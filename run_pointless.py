from __future__ import absolute_import
import xml.dom.minidom

from cctbx import sgtbx


def read_pointless_xml(pointless_xml_file):
    '''Read through the pointless xml output, return as a list of spacegroup
    numbers in order of likelihood, corresponding to the pointgroup of the
    data.'''

    dom = xml.dom.minidom.parse(pointless_xml_file)

    best = dom.getElementsByTagName('BestSolution')[0]
    pointgroup = best.getElementsByTagName(
        'GroupName')[0].childNodes[0].data
    confidence = float(best.getElementsByTagName(
        'Confidence')[0].childNodes[0].data)
    totalprob = float(best.getElementsByTagName(
        'TotalProb')[0].childNodes[0].data)
    reindex_matrix = list(map(float, best.getElementsByTagName(
        'ReindexMatrix')[0].childNodes[0].data.split()))
    reindex_operator = best.getElementsByTagName(
        'ReindexOperator')[0].childNodes[0].data.strip()

    scorelist = dom.getElementsByTagName('LaueGroupScoreList')[0]
    scores = scorelist.getElementsByTagName('LaueGroupScore')

    results = []

    for s in scores:
        number = int(s.getElementsByTagName(
            'number')[0].childNodes[0].data)
        lauegroup = str(s.getElementsByTagName(
            'LaueGroupName')[0].childNodes[0].data).strip()
        if lauegroup[0] == 'H':
            lauegroup = 'R{}'.format(lauegroup[1:])
        pointgroup = sgtbx.space_group_type(lauegroup).group(
            ).build_derived_acentric_group().type().number()
        reindex = s.getElementsByTagName(
            'ReindexOperator')[0].childNodes[0].data
        netzc = float(s.getElementsByTagName(
            'NetZCC')[0].childNodes[0].data)
        likelihood = float(s.getElementsByTagName(
            'Likelihood')[0].childNodes[0].data)
        r_merge = float(s.getElementsByTagName(
            'R')[0].childNodes[0].data)
        delta = float(s.getElementsByTagName(
            'CellDelta')[0].childNodes[0].data)

        # record this as a possible lattice... if it's Z score
        # is positive, anyway - except this does kinda bias towards
        # those lattices which have all symops => no Z-.

        lattice = lauegroup_to_lattice(lauegroup)
        if netzc >= 0.0:
            results.append((lattice, pointgroup))

    return results

def lauegroup_to_lattice(lauegroup):
    '''Convert a Laue group representation (from pointless, e.g. I m m m)
    to something useful, like the implied crystal lattice (in this
    case, oI.)'''

    # this has been calculated from the results of Ralf GK's sginfo and a
    # little fiddling...
    #
    # 19/feb/08 added mI record as pointless has started producing this -
    # why??? this is not a "real" spacegroup... may be able to switch this
    # off...
    #                             'I2/m': 'mI',

    lauegroup_to_lattice = {'Ammm': 'oA',
                            'C2/m': 'mC',
                            'I2/m': 'mI',
                            'Cmmm': 'oC',
                            'Fm-3': 'cF',
                            'Fm-3m': 'cF',
                            'Fmmm': 'oF',
                            'H-3': 'hR',
                            'H-3m': 'hR',
                            'R-3:H': 'hR',
                            'R-3m:H': 'hR',
                            'R-3': 'hR',
                            'R-3m': 'hR',
                            'I4/m': 'tI',
                            'I4/mmm': 'tI',
                            'Im-3': 'cI',
                            'Im-3m': 'cI',
                            'Immm': 'oI',
                            'P-1': 'aP',
                            'P-3': 'hP',
                            'P-3m': 'hP',
                            'P2/m': 'mP',
                            'P4/m': 'tP',
                            'P4/mmm': 'tP',
                            'P6/m': 'hP',
                            'P6/mmm': 'hP',
                            'Pm-3': 'cP',
                            'Pm-3m': 'cP',
                            'Pmmm': 'oP'}

    updated_laue = ''

    for l in lauegroup.split():
        if not l == '1':
            updated_laue += l

    return lauegroup_to_lattice[updated_laue]

def decide_pointgroup(p1_unit_cell, metadata,
                      input_spacegroup=None):
    '''
    Run POINTLESS to get the list of allowed pointgroups (N.B. will
    insist on triclinic symmetry for this scaling step) then run
    pointless on the resulting reflection file to get the idea of the
    best pointgroup to use. Then return the correct pointgroup and
    cell.

    Parameters
    ----------
    p1_unit_cell : tuple
    metadata : dict
    input_spacegroup : tuple, optional
    Returns
    -------
    returns several values of different types
        unit_cell <tuple>, space_group_number <int>
        resolution_high <float>
    '''

    pointless_log = run_job(
        'pointless_wrapper',
        arguments=['xdsin', xdsin, 'xmlout', xmlout],
        stdin=['systematicabsences off'])

    fout = open('pointless.log', 'w')

    for record in pointless_log:
        fout.write(record)

    fout.close()

    # now read the XML file

    pointless_results = read_pointless_xml(xmlout)

    # select the top solution which is allowed, return this

    if input_spacegroup:
        sg_accepted = False
        input_spacegroup="".join(input_spacegroup.split())
        pointgroup = ersatz_pointgroup(input_spacegroup)
        if pointgroup.startswith('H'):
            pointgroup = pointgroup.replace('H', 'R')
        lattice = spacegroup_to_lattice(input_spacegroup)
        for r in pointless_results:
            result_sg = "".join(check_spacegroup_name(r[1]).split(' '))
            if lattice_to_spacegroup(lattice) in results and \
                    ersatz_pointgroup(result_sg) == pointgroup:
                space_group_number = r[1]
                unit_cell = results[lattice_to_spacegroup(r[0])][1]
                write('Happy with sg# {}'.format(space_group_number))
                write('{0[0]:6.2f} {0[1]:6.2f} {0[2]:6.2f} {0[3]:6.2f} {0[4]:6.2f} {0[5]:6.2f}'.format(
                      unit_cell))
                sg_accepted = True
                break

        if not sg_accepted:
            write('No indexing solution for spacegroup {} so ignoring'.format(
                  input_spacegroup))
            input_spacegroup = None

    # if input space group obviously nonsense, allow to ignore just warn
    if not input_spacegroup:
        for r in pointless_results:
            if lattice_to_spacegroup(r[0]) in results:
                space_group_number = r[1]
                unit_cell = results[lattice_to_spacegroup(r[0])][1]
                write('Happy with sg# {}'.format(space_group_number))
                write('{0[0]:6.2f} {0[1]:6.2f} {0[2]:6.2f} {0[3]:6.2f} {0[4]:6.2f} {0[5]:6.2f}'.format(
                      unit_cell))
                break
            else:
                write('Rejected solution {0[0]} {0[1]:3d}'.format(r))

    # this should probably be a proper check...
    assert(space_group_number)

    # also save the P1 XDS_ASCII.HKL file see
    # http://trac.diamond.ac.uk/scientific_software/ticket/1106

    shutil.copyfile('XDS_ASCII.HKL', 'XDS_P1.HKL')

    return unit_cell, space_group_number, resolution_high

def main():
    print(read_pointless_xml('/Users/aaronfinke/ssx_test/ssxoutput_20200423_111035/xscale/moo.xml'))

if __name__ == '__main__':
    main()
