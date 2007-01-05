#!/usr/bin/env python
# xia2scan.py
#   Copyright (C) 2006 CCLRC, Graeme Winter
#
#   This code is distributed under the BSD license, a copy of which is 
#   included in the root directory of this package.
#
# 9th June 2006
# 
# A small program to summarise the diffraction strength from a list of
# diffraction images. This will use labelit for both indexing and 
# distling.
# 
# Requires:
# 
# The correct beam centre.
# 
# 

import sys
import os
import exceptions

if not os.environ.has_key('XIA2_ROOT'):
    raise RuntimeError, 'XIA2_ROOT not defined'
if not os.environ.has_key('XIA2CORE_ROOT'):
    raise RuntimeError, 'XIA2CORE_ROOT not defined'

if not os.environ['XIA2_ROOT'] in sys.path:
    sys.path.append(os.environ['XIA2_ROOT'])

# prevent the usual standard output stuff...
from Handlers.Streams import streams_off
streams_off()

from Handlers.CommandLine import CommandLine
from Schema.Sweep import SweepFactory

# program wrappers we will use
from Wrappers.Labelit.LabelitScreen import LabelitScreen
from Wrappers.Labelit.LabelitStats_distl import LabelitStats_distl

def xia2scan():
    '''Do the scan.'''

    template, directory = CommandLine.get_template(), \
                          CommandLine.get_directory()

    first, last = CommandLine.get_first_last()

    if not template or not directory:
        raise RuntimeError, 'no image information supplied'

    # if this isnot set, then we will presume that it is correct
    # in the image headers
    
    beam = CommandLine.get_beam()

    if '-omit' in sys.argv:
        omit = True
    else:
        omit = False

    sweeps = SweepFactory(template, directory, beam)

    summary_info = { }

    for s in sweeps:

        # if > 1 image then these are probably stills... but we don't care
        # about that!

        for i in s.get_images():

            beam = s.get_beam()

            # FIXME 27/OCT/06 want to be able to deal with first,
            # last images
            if (first > 0 and last > 0) and (i < first or i > last):
                sys.stdout.write('.')
                sys.stdout.flush()
                continue

            sys.stdout.write('o')
            sys.stdout.flush()

            try:

                ls = LabelitScreen()
                ls.setup_from_image(s.imagename(i))
                ls.add_indexer_image_wedge(i)
                ls.set_beam(beam)
                ls.set_refine_beam(False)
                ls.index()

                solution = ls.get_solutions()[1]
                # P1 cell is always solution #1
                lsd = LabelitStats_distl()
                lsd.stats_distl()
                stats = lsd.get_statistics(s.imagename(i))
                summary_info[i] = { }
                summary_info[i]['volume'] = solution['volume']
                summary_info[i]['mosaic'] = solution['mosaic']
                summary_info[i]['spots_good'] = stats['spots_good']
                summary_info[i]['spots_total'] = stats['spots_total']
                summary_info[i]['resol_one'] = stats['resol_one']
                summary_info[i]['resol_two'] = stats['resol_two']
                summary_info[i]['saturation'] = stats['saturation']

            except exceptions.Exception, e:
                # print 'Uh oh! %s' % str(e)

                summary_info[i] = { }
                summary_info[i]['volume'] = 0.0
                summary_info[i]['mosaic'] = 0.0
                summary_info[i]['spots_good'] = 0.0
                summary_info[i]['spots_total'] = 0.0
                summary_info[i]['resol_one'] = 0.0
                summary_info[i]['resol_two'] = 0.0
                summary_info[i]['saturation'] = 0.0

    sys.stdout.write('\n')

    images = summary_info.keys()
    images.sort()
    for i in images:
        if summary_info[i]['volume'] == 0 and omit:
            continue
        
        print '%3d %6d %6d %6.2f %6.2f %6.2f %6.2f %9d' % \
              (i, summary_info[i]['spots_total'],
               summary_info[i]['spots_good'],
               summary_info[i]['resol_one'],
               summary_info[i]['resol_two'],
               summary_info[i]['mosaic'],
               summary_info[i]['saturation'],
               summary_info[i]['volume'])

if __name__ == '__main__':
    xia2scan()

    
