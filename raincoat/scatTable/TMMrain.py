# -*- coding: utf-8 -*-
from __future__ import print_function

""" TMMrain module
Copyright (C) 2019 Davide Ori and RAINCOAT team - University of Cologne

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

Python class to compute the polarimetric scattering properties of a series of
raindrop sizes according to specified parameters. The class acts as an interface
to the pytmatrix package which implements the T-Matrix method for single 
spheroids.

"""
from multiprocessing import Process
from multiprocessing import Manager
from multiprocessing import Pool
import numpy as np
import pandas as pd

from pytmatrix.tmatrix import Scatterer
from pytmatrix import tmatrix_aux
from pytmatrix import orientation
from pytmatrix import radar
from pytmatrix import scatter

from . import utilities

c = 299792458. # [m/s] speed of light in vacuum
columns =  ['radarXSh[mm2]', 'radarXSv[mm2]', 
            'extxs[mm2]', 'ray[mm2]', 'sKdp[mm2]', 'aspect_ratio']

class scatTable(object):
    """ Class to compute the scattering properties of a range of drop sizes

    Attributes:
        frequency - scalar: frequency of the electromagnetic wave [GHz]
        n - complex scalar: complex refractive index of water
        sizes - array: vector of sizes of drops for which scattering proparties
                       have to be computed
        canting - scalar: if not None (default value) the scattering properties
                          are averaged over a gaussian distribution of pitch
                          angles with mean=0 and standard deviation [deg] 
                          defined by the canting attribute [deg]
        aspect_ratio_func - scalar or function: defines a constant aspect ratio
                            for the raindrops or a function that returns the 
                            aspect-ratio according to the drop size.
                            The aspect-ratio is defined here as the ratio
                            between the vertical and the horizontal dimensions
                            of the drops, thus, <1 means oblate >1 means prolate
                            and by default it is set to 1.0 (spherical)
        elevation - scalar: elevation angle of the observing radar [deg].
                            90 (default value) means vertically pointing
                            and 0 means no elevation (horizontal scan).
    """

    def __init__(self, frequency, n, sizes=np.arange(0.01, 8.5, 0.01),
                 canting=None, elevation=90.,
                 aspect_ratio_func=1.0):

        self.frequency = frequency  # GHz
        self.n = n
        self.sizes = sizes          # millimeters
        self.canting = canting      # deg
        self.elevation = elevation  # deg
        self.wl = 1.e-6*c/frequency # millimeters
        self.K2 = utilities.K2(self.n*self.n)
        self.prefactor = np.pi**5*self.K2/self.wl**4

        self._theta0 = 90.0 - self.elevation

        # Deal with aspect_ratio_func
        if hasattr(aspect_ratio_func, '__call__'):
            self.aspect_ratio_func = aspect_ratio_func
        elif isinstance(aspect_ratio_func, (int, float)): #exclude py2 long type
            def constant_func(x):
                return float(aspect_ratio_func)
            self.aspect_ratio_func = constant_func
            self.aspect_ratio_func.__name__ = "constant aspect ratio " + \
                                               str(aspect_ratio_func)
        else:
            raise AttributeError('aspect_ratio_func must be either a callable' \
                                 + 'or a constant a numeric value')

        # Inititialize the scattering table
        self.table = pd.DataFrame(index=self.sizes, columns=columns)
        self.table.index.name = 'diameter[mm]'


    def compute(self, verbose=False, procs=1):
        """ Computes internally the scattering properties of the series of drop
        sizes according to the set parameters
        """
        nchunk = len(self.sizes)//(procs*5) # we can multiply procs by a factor
                                            # that makes chuncks larger than
                                            # nprocs resulting in less cycles
                                            # more parallel executions, but
                                            # also more memory, take care
        for chunk in np.array_split(self.sizes, nchunk):
            pn = Pool(processes=procs)
            res = pn.map(self._compute_single_size, chunk)
            self.table.loc[chunk] = res
            if verbose:
                print(self.table.loc[chunk])

    
    def _compute_single_size(self, d):
        ar = self.aspect_ratio_func(d)
        rain = Scatterer(radius=0.5*d,
                         wavelength=self.wl,
                         m=self.n,
                         axis_ratio=1.0/ar)
        rain.Kw_sqr = self.K2
        if self.canting is not None:
            rain.or_pdf = orientation.gaussian_pdf(std=self.canting)
            rain.orient = orientation.orient_averaged_fixed
        # Set backward scattering for reflectivity calculations
        rain.set_geometry((self._theta0, self._theta0, 0., 180., 0., 0.))
        rxsh = radar.radar_xsect(rain, h_pol=True)
        rxsv = radar.radar_xsect(rain, h_pol=False)
        # Set forward scattering for attenuation and phase computing
        rain.set_geometry((self._theta0, self._theta0, 0., 0., 0., 0.))
        ext = scatter.ext_xsect(rain)
        skdp = radar.Kdp(rain)

        # Calculate Rayleigh approximation for reference
        ray = self.prefactor*d**6
        #print(d, rxsh, rxsv, ext, ray, skdp, ar)
        return rxsh, rxsv, ext, ray, skdp, ar


    def save_text_scat_table(self, filename):
        """ Saves the scattering table to a formatted text file and includes the
            computing parameters as attributes in the header row.
        """
        key_list = ['elevation', 'canting', 'aspect_ratio_func', 'K2',
                    'frequency', 'n', 'wl', 'prefactor']
        properties = {k: self.__dict__[k] for k in key_list}
        properties['aspect_ratio_func'] = self.aspect_ratio_func.__name__
        with open(filename, 'w') as fn:
            fn.write(str(properties)+'\n')
        self.table.to_csv(filename, mode='a')


    def save_binary_scat_table(self, filename):
        raise NotImplementedError()