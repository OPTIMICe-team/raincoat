# -*- coding: utf-8 -*-

"""
Copyright (C) 2019 Davide Ori and TEAM University of Cologne

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

long_description = """A Python code for DOING COOL STUFF

Requires a lot of packages
"""

import sys

def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('raincoat', parent_package, top_path,
        version = '0.0.1',
        author  = "Davide Ori and Jose Dias Neto and... PUT NAMES HERE",
        author_email = "dori@uni-koeln.com",
        description = "Calibration of radars using disdrometer data and T-matrix tables",
        license = "MIT",
        url = 'https://github.com/DaveOri/raincoat',
        download_url = 'https://github.com/DaveOri/raincoat/archive/master.zip',
        long_description = long_description,
        classifiers = [
            "Development Status :: 0 - under development",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: MIT License",
            "Operating System :: should be OS Independent",
            "Programming Language :: Python",
            "Topic :: Scientific/Engineering :: Physics",
        ]
    )

    kw = {}
#    if sys.platform == 'darwin':
#        kw['extra_link_args'] = ['-undefined dynamic_lookup', '-bundle']
    return config


if __name__ == "__main__":

    from numpy.distutils.core import setup
    setup(configuration=configuration,
        packages = ['raincoat','raincoat.test','raincoat.scatTable','raincoat.parsivel'],        
        package_data = {},
        platforms = ['any'],
        requires = ['numpy', 'scipy'])
