""" scattering utilities module

Copyright (C) 2017 - 2019 Davide Ori dori@uni-koeln.de
Institute for Geophysics and Meteorology - University of Cologne

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

This module provides a short list of utilities and complementary functions
for the refractive index module.

Basic conversion from refractive index to dielectric permittivity
(and viceversa) is implemented.
The module also provides a conversion function from dielectric permittivity to
radar dielectric factor K2 which is of great importance in radar applications

"""

from __future__ import absolute_import

import numpy as np

speed_of_light = 299792458.0

def eps2n(eps): return np.sqrt(eps)

def n2eps(n): return n*n

def wavenumber(frequency=None, wavelength=None):
    if (frequency is None):
        if (wavelength is None):
            raise AttributeError('Frequency or wavelength must be not None')
        else:
            return 2.0*np.pi/wavelength
    elif (wavelength is None):
        if (frequency is None):
            raise AttributeError('Frequency or wavelength must be not None')
        else:
            return 2.0*np.pi*frequency/speed_of_light
    else:
        raise AttributeError('You cannot pass both frequency and wavelength')

def K(eps):
    """ Rayleigh complex dielectric factor
    This is basically the K complex factor that defines the Radar dielectric
    factor |K|**2. It is useful in Rayleigh theory to define absorption cross
    section from its imaginary part

    Parameters
    ----------
    eps : complex
        nd array of complex relative dielectric constants

    Returns
    -------
    nd - float
        Rayleigh complex dielectric factor K
    """
    return (eps-1.0)/(eps+2.0)


def K2(eps):
    """ Radar dielectric factor |K|**2

    Parameters
    ----------
    eps : complex
        nd array of complex relative dielectric constants

    Returns
    -------
    nd - float
        Radar dielectric factor |K|**2 real

    """
    K_complex = (eps-1.0)/(eps+2.0)
    return (K_complex*K_complex.conj()).real
