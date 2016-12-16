import os
import json
import numpy as np
import oceanwaves.swan2 as swan


GEOM_FILE = os.path.join(os.path.split(__file__)[0], 'dimensionsOSK.json')


def get_transmitted_spectrum(sp1file, tabfile, sp2file, closed=False, ix=0):

    hbc = get_conditions(sp1file, tabfile, ix=ix)
    geom = get_geometry()
    K = transmission_through_barrier([hbc], geom, closed=closed)[0]['K']

    # create spectrum
    s = swan.SwanIO()
    ix = dict(location=ix)
    spc = s.read_spc(sp1file)[ix]
    spc.energy *= K**2.
    spc = spc.to_directional(direction=np.arange(0., 360., 10.))
    s.write_spc(spc, sp2file)


def transmission_through_door(swl, Hs, rmb, beam, road, closed=False, **kwargs):

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
            
            
def transmission_through_barrier(hbc, geom, closed=False):
                
    geom = dict(zip([(round(g['x']), round(g['y'])) for g in geom], geom))
    hbc  = dict(zip([(round(h['x']), round(h['y'])) for h in hbc], hbc))
                
    Kt = []
    for (x_i, y_i), hbc_i in hbc.iteritems():
                    
        kwargs = dict(closed=closed)
        kwargs.update(hbc_i)
        kwargs.update(geom[(x_i, y_i)])
        
        Kt.append(dict(x=x_i,
                       y=y_i,
                       K=transmission_through_door(**kwargs)))
                    
    return Kt


def get_conditions(sp1file, tabfile, ix=0):

    # read swan data
    s = swan.SwanIO()
    spc = s.read_spc(sp1file)
    tab = s.read_table(tabfile)

    ix = dict(location=ix)
    hbc = dict(Hs = float(spc.Hm0()[ix].values),
               swl = float(tab[ix]['Watlev'].values),
               x = float(tab[ix]['Xp'].values),
               y = float(tab[ix]['Yp'].values))

    return hbc
        
                                                    
def get_geometry(fname=GEOM_FILE):
    if os.path.exists(fname):
        with open(fname, 'r') as fp:
            return json.load(fp)
    else:
        raise IOError('File not found: %s' % fname)


