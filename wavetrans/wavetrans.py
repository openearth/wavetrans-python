import re
import os
import json
import logging
import numpy as np
import oceanwaves


GEOM_FILE = os.path.join(os.path.split(__file__)[0], 'dimensionsOSK.json')
REGEX_RUN = 'U\d{2}D\d{3}L(m|p)\d{3}(OO|NZ)\w'


def get_transmitted_spectrum(spcfile, outpath, closed=False, door=None):
    '''Reads SWAN spectrum and table file and writes transmitted SWAN spectrum files

    Parameters
    ----------
    spcfile : str
        Path to input SWAN spectrum file
    outpath : str
        Path to output directory for SWAN spectrum files
    closed : bool, optional
        Flag indicating whether barrier doors are closed
    door : int, optional
        Index of barrier door in dimensionsOSK.json
    
    '''

    # determine and check paths
    if not os.path.exists(spcfile):
        raise IOError('Spectrum file not found: %s' % spcfile)

    tabfile = '%s.TAB' % os.path.splitext(spcfile)[0]

    if not os.path.exists(tabfile):
        raise IOError('Tabular file corresponding to spectrum fil not found: %s' % tabfile)

    m = re.match(REGEX_RUN, os.path.split(spcfile)[1])
    if not m:
        raise ValueError('Invalid run identifier in file name: %s' % spcfile)

    run = m.group().replace('NZ','OO')
    outpath = os.path.join(outpath, run)
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    
    # read conditions and geometry
    hbc = get_conditions(spcfile, tabfile)
    geom = get_geometry()

    # compute transmission
    Kt = transmission_through_barrier(hbc, geom, closed=closed, door=door)

    # read spectrum
    spc = oceanwaves.from_swan(spcfile)
    if door is not None:
        doors = [door]
    else:
        doors = range(spc.dims['location'])
        
    # write spectra
    for i, door in enumerate(doors):
        outfile = os.path.join(outpath, '%s%s.SP2' % (run, geom[door]['name']))
        
        spc_i = spc[dict(location=door)]
        spc_i['_energy'] *= Kt[i]**2.
        spc_i.to_swan(outfile)


def transmission_through_door(swl, Hs, rmb, beam, road, closed=False, **kwargs):
    '''Compute wave transmission through single barrier door

    Parameters
    ----------
    swl : float
        Still water level
    Hs : float
        Significant wave height
    rmb : float
        Height of rubble mound breakwater
    beam : float
        Height of beam
    road : float
        Height of road
    closed : bool, optional
        Flag indicating whether barrier door is closed

    Returns
    -------
    Kt : float
        Wave transmission coefficient

    '''

    # water column includes 1/2 of the Hs
    crest = swl + Hs / 2.

    # blocking by the rubble mound
    obstr = rmb['height']

    # blocking by the beam
    if crest > beam['bottom']:
        obstr += np.minimum(crest-beam['bottom'],
                            beam['top']-beam['bottom'])
        
    # blocking by the door
    if crest > road['bottom']:
        obstr += np.minimum(crest-road['bottom'],
                            road['top']-road['bottom'])
            
    # blocking by the (closed) door
    # it is assumed that the door.height=rmb.depth+beam.bottom;
    if closed:
        obstr += rmb['depth'] + beam['bottom']
        
    Kt = np.maximum(0., 1. - obstr / (crest + rmb['depth'] + rmb['height']))
                
    return Kt
            
            
def transmission_through_barrier(hbc, geom, closed=False, door=None):
    '''Compute wave transmission through entire barrier

    Parameters
    ----------
    hbc : dict
        Dictionary with hydraulic boundary conditions (x, y, swl, Hs)
    geom : dict
        Dictionary with barrier geometry (x, y, rmb, beam, road)
    closed : bool, optional
        Flag indicating whether barrier doors are closed
    door : int, optional
        Index of barrier door in dimensionsOSK.json (default: all)

    Returns
    -------
    Kt : list
        List with wave transmitions coefficients

    '''

    if door is not None:
        hbc = [hbc[door]]
        geom = [geom[door]]
    
    Kt = []
    for hbc_i, geom_i in zip(hbc, geom):
                    
        kwargs = dict(closed=closed)
        kwargs.update(hbc_i)
        kwargs.update(geom_i)

        Kt.append(transmission_through_door(**kwargs))
                    
    return Kt


def get_conditions(sp1file, tabfile):
    '''Extract relevant conditions from input files'''

    # read swan data
    spc = oceanwaves.from_swan(sp1file)
    tab = oceanwaves.from_swantable(tabfile)

    hbc = dict(Hs = spc.Hm0().values,
               swl = tab['Watlev'].values,
               x = tab['Xp'].values,
               y = tab['Yp'].values)

    # reshape structure
    hbc = [{k:v[i] for k, v in hbc.iteritems()}
           for i in range(spc.dims['location'])]

    return hbc
        
                                                    
def get_geometry(fname=GEOM_FILE):
    if os.path.exists(fname):
        with open(fname, 'r') as fp:
            return json.load(fp)
    else:
        raise IOError('File not found: %s' % fname)


