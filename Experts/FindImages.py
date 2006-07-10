#!/usr/bin/env python
# FindImages.py
#   Copyright (C) 2006 CCLRC, Graeme Winter
#
#   This code is distributed under the terms and conditions of the
#   CCP4 Program Suite Licence Agreement as a CCP4 Library.
#   A copy of the CCP4 licence can be obtained by writing to the
#   CCP4 Secretary, Daresbury Laboratory, Warrington WA4 4AD, UK.
#
# 9th June 2006
# 
# A set of routines for finding images and the like based on file names.
# This includes all of the appropriate handling for templates, directories
# and the like.
#
# 15/JUN/06 
# 
# Also routines for grouping sets of images together into sweeps based on 
# the file names and the information in image headers.
# 

import os
import re
import string
import math

def image2template(filename):
    '''Return a template to match this filename.'''

    # check that the file name doesn't contain anything mysterious
    if filename.count('#'):
        raise RuntimeError, '# characters in filename'

    # the patterns in the order I want to test them

    pattern_keys = [r'(.*)_([0-9]*)\.(.*)',
                    r'([^\.]*)\.([0-9]+)',
                    r'(.*?)([0-9]*)\.(.*)']

    # patterns is a dictionary of possible regular expressions with
    # the format strings to put the file name back together

    patterns = {r'(.*)_([0-9]*)\.(.*)':'%s_%s.%s',
                r'([^\.]*)\.([0-9]+)':'%s.%s%s',
                r'(.*?)([0-9]*)\.(.*)':'%s%s.%s'}

    for pattern in pattern_keys:
        match = re.compile(pattern).match(filename)

        if match:
            prefix = match.group(1)
            number = match.group(2)
            try:
                exten = match.group(3)
            except:
                exten = ''

            for digit in string.digits:
                number = number.replace(digit, '#')
                
            return patterns[pattern] % (prefix, number, exten)

    raise RuntimeError, 'filename %s not understood as a template' % \
          filename

def image2image(filename):
    '''Return an integer for the template to match this filename.'''

    # check that the file name doesn't contain anything mysterious
    if filename.count('#'):
        raise RuntimeError, '# characters in filename'

    # the patterns in the order I want to test them

    pattern_keys = [r'(.*)_([0-9]*)\.(.*)',
                    r'([^\.]*)\.([0-9]+)',
                    r'(.*?)([0-9]*)\.(.*)']

    # patterns is a dictionary of possible regular expressions with
    # the format strings to put the file name back together

    patterns = {r'(.*)_([0-9]*)\.(.*)':'%s_%s.%s',
                r'([^\.]*)\.([0-9]+)':'%s.%s%s',
                r'(.*?)([0-9]*)\.(.*)':'%s%s.%s'}

    for pattern in pattern_keys:
        match = re.compile(pattern).match(filename)

        if match:
            prefix = match.group(1)
            number = match.group(2)
            try:
                exten = match.group(3)
            except:
                exten = ''

            return int(number)

    raise RuntimeError, 'filename %s not understood as a template' % \
          filename

def image2template_directory(filename):
    '''Separate out the template and directory from an image name.'''

    directory = os.path.dirname(filename)
    image = os.path.split(filename)[-1]
    template = image2template(image)

    return template, directory

def find_matching_images(template, directory):
    '''Find images which match the input template in the directory
    provided.'''

    files = os.listdir(directory)

    # to turn the template to a regular expression want to replace
    # however many #'s with EXACTLY the same number of [0-9] tokens,
    # e.g. ### -> ([0-9]{3})
    
    length = template.count('#')
    regexp = re.compile(template.replace('#' * length, '([0-9]{%d})' % length))

    images = []

    for f in files:
        match = regexp.match(f)

        if match:
            images.append(int(match.group(1)))

    images.sort()

    return images

def template_directory_number2image(template, directory, number):
    '''Construct the full path to an image from the template, directory
    and image number.'''

    length = template.count('#')

    # check that the number will fit in the template

    if (math.pow(10, length) - 1) < number:
        raise RuntimeError, 'number too big for template'

    # construct a format statement to give the number part of the
    # template
    format = '%%0%dd' % length

    # construct the full image name
    image = os.path.join(directory,
                         template.replace('#' * length,
                                          format % number))

    return image

def headers2sweep_ids(header_dict):
    '''Get a list of sweep ids (first images) from the header list.'''

    sweeps = headers2sweeps(header_dict)

    ids = []

    for s in sweeps:
        ids.append(min(s['images']))

    return ids

def headers2sweeps(header_dict):
    '''Parse a dictionary of headers to produce a list of summaries.'''

    images = header_dict.keys()
    images.sort()

    if len(images) == 0:
        return []

    sweeps = []

    current_sweep = header_dict[images[0]]
    
    current_sweep['images'] = [images[0]]
    current_sweep['collect_start'] = current_sweep['epoch']
    current_sweep['collect_end'] = current_sweep['epoch']

    for i in images[1:]:
        header = header_dict[i]

        # if wavelength the same and distance the same and this image
        # follows in phi from the previous chappie then this is the
        # next frame in the sweep. otherwise it is the first frame in
        # a new sweep.

        if header['wavelength'] == current_sweep['wavelength'] and \
           header['distance'] == current_sweep['distance'] and \
           header['phi_start'] == current_sweep['phi_end']:
            # this is another image in the sweep
            current_sweep['images'].append(i)
            current_sweep['phi_end'] = header['phi_end']
            current_sweep['collect_end'] = header['epoch']
        else:
            sweeps.append(current_sweep)
            current_sweep = header_dict[i]
            current_sweep['images'] = [i]
            current_sweep['collect_start'] = current_sweep['epoch']
            current_sweep['collect_end'] = current_sweep['epoch']

    sweeps.append(current_sweep)

    return sweeps
    
if __name__ == '__main__':
    # run some tests...

    if not os.environ.has_key('DPA_ROOT'):
        raise RuntimeError, 'DPA_ROOT not defined'

    print image2template('foo_bar_1_001.img')
    print image2template('foo_bar_001.img')
    print image2template('foo_bar001.img')
    print image2template('foo_bar.001')

    print find_matching_images(image2template('12287_1_E1_001.img'),
                               os.path.join(os.environ['DPA_ROOT'],
                                            'Data', 'Test', 'Images'))

    
    print template_directory_number2image(image2template('12287_1_E1_001.img'),
                                          os.path.join(os.environ['DPA_ROOT'],
                                                       'Data', 'Test',
                                                       'Images'), 1)
    print template_directory_number2image(image2template('12287_1_E1_001.img'),
                                          os.path.join(os.environ['DPA_ROOT'],
                                                       'Data', 'Test',
                                                       'Images'), 1000)
