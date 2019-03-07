# -*- coding: utf-8 -*-

""" DSD module
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

Module class library to provide interface to commonly used DSDs form and in
particular the Binned DSD which is ment to reproduce observational data provided
by disdrometers

The module also provide interfaces to fit analytical DSDs form to data using
common fitting methods such as the method of moments.

"""

import numpy as np
from scipy.special import gamma

def between(x, y, xmin, xmax):
    """
    Set to zero the values of x that are outside the interval [xmin, xmax]

    Args:
        x (array-like): The coordinates of the array to be cut
        y (array-like): The array to be cut
        xmin (scalar): The minimum value of x
        xmax (scalar): The maximum value of x

    Returns:
        y (array-like): values outside of the domain [xmin, xmax] are set to 0
    """

    return np.heaviside(x-xmin,1)*np.heaviside(-x-xmax,1)*y


class DSD(object):
    def __init__(self, Dmin=0.0, Dmax=np.inf):

        if (Dmin > Dmax):
            raise AttributeError('The minimum size of any distribution must be \
                                  smaller then its maximum size, passed Dmin is\
                                  larger than Dmax')
        if (Dmin < 0):
            raise AttributeError('Dmin < 0 implies that negative diameters are \
                                  possible whereas DSDs domains are strictly \
                                  semidefinite positive')
        self.Dmin = Dmin
        self.Dmax = Dmax

    def __call__(self, D):
        if np.shape(D) == ():
            return 0.0
        else:
             return np.zeros_like(D)

    def generator(self, N):
        """
        Generate N samples of the distribution (probably easiest method is 
        the cumulative normalized)
        """
        pass

    def normalizedCumulative(self):
        """
        Numerical method to implement cumulative distribution
        """
        pass
    
    def moment(self, x, N=1.e5):
        """
        Calculate numerically the moment of order x from N samples
        """


class InverseExponential(DSD):
    """Inverse exponential drop size distribution (DSD).
    
    Callable class to provide an inverse exponential DSD:
    N(D) = N0 * exp(-Lambda*D)

    Attributes:
        N0: the intercept parameter
        Lambda: the inverse scale parameter        
        D_max: the maximum diameter to consider (defaults to 11/Lambda,
            i.e. approx. 3*D0, if None) # TODO: set to 99% of DSD volume

    Args (call):
        D: the particle diameter.

    Returns (call):
        The PSD value for the given diameter.    
        Returns 0 for all diameters larger than D_max.
    """

    def __init__(self, N0=1.0, Lambda=1.0, D_max=None):
        self.N0 = float(N0)
        self.Lambda = float(Lambda)
        self.D_max = 11.0/Lambda if D_max is None else D_max

    def __call__(self, D):
        psd = self.N0 * np.exp(-self.Lambda*D)
        if np.shape(D) == ():
            if D > self.D_max:
                return 0.0
        else:
            psd[D > self.D_max] = 0.0
        return psd


class GammaPSD(InverseExponential):
    """Unnormalized Gamma drop size distribution (DSD).
    
    Callable class to provide an gamma DSD with the given parameters:
    N(D) = N0 * D**mu * exp(-Lambda*D)

    Attributes:
        N0: the intercept parameter.
        Lambda: the inverse scale parameter
        mu: the shape parameter
        D_max: the maximum diameter to consider (defaults to 11/Lambda,
            i.e. approx. 3*D0, if None)

    Args (call):
        D: the particle diameter.

    Returns (call):
        The PSD value for the given diameter.    
        Returns 0 for all diameters larger than D_max.
    """
    
    def __init__(self, N0=1.0, Lambda=1.0, mu=0.0, D_max=None):
        super(UnnormalizedGammaPSD, self).__init__(N0=N0, Lambda=Lambda, 
            D_max=D_max)
        self.mu = mu

    def __call__(self, D):
        # For large mu, this is better numerically than multiplying by D**mu
        psd = self.N0 * np.exp(self.mu*np.log(D)-self.Lambda*D)
        if np.shape(D) == ():
            if (D > self.D_max) or (D==0):
                return 0.0
        else:
            psd[(D > self.D_max) | (D == 0)] = 0.0
        return psd



class Lognormal(DSD):
    """Lognormal drop size distribution (DSD)

    Callable object to provide a lognormal drop size distribution with the given
    parameters

    The DSD form is:
    N(D) = Nt/(sqrt(2*pi)*g(D-theta)) * exp(-(ln(D-theta)-mu)**2 / (2*sigma**2))

    Attributes:
        Nt:
        g:
        theta:
        mu:
        sigma:

    """

    def __init__(self, Nt=1., g=1., theta=1., mu=0., sigma=1.):
        """
        """
        self.Nt = Nt
        self.g = g
        self.theta = theta
        self.mu = mu
        self.sigma = sigma

    def __call__(self, D):
        coeff = Nt/(np.sqrt(2*np.pi) * g * (D - theta))
        expon = np.exp(-(np.log(D - theta) -mu)**2 / (2. * sigma**2))
        psd = coeff * expon
        psd[D > Dmax] = 0.0
        psd[D < Dmin] = 0.0
        return psd



class NormalizedGamma(DSD):
    """Normalized gamma particle size distribution (DSD).
    
    Callable class to provide a normalized gamma DSD with the given 
    parameters.

    TODO: the value of 3.67 comes from observation that RR is proportional to
    3.67th moment of the DSD, not sure if that is still ok 

    The PSD form is:
    N(D) = Nw * f(mu) * (D/D0)**mu * exp(-(3.67+mu)*D/D0)
    f(mu) = 6/(3.67**4) * (3.67+mu)**(mu+4)/Gamma(mu+4)

    Attributes:
        D0: the median volume diameter.
        Nw: the intercept parameter.
        mu: the shape parameter.
        D_max: the maximum diameter to consider (defaults to 3*D0 when
            if None)

    Args (call):
        D: the particle diameter.

    Returns (call):
        The DSD value for the given diameter.    
        Returns 0 for all diameters larger than D_max.
    """

    def __init__(self, D0=1.0, Nw=1.0, mu=0.0, D_max=None):
        self.D0 = float(D0)
        self.mu = float(mu)
        self.D_max = 3.0*D0 if D_max is None else D_max
        self.Nw = float(Nw)
        self.nf = Nw * 6.0/3.67**4 * (3.67+mu)**(mu+4)/gamma(mu+4)

    def __call__(self, D):
        d = (D/self.D0)
        psd = self.nf * np.exp(self.mu*np.log(d)-(3.67+self.mu)*d)
        if np.shape(D) == ():
            if (D > self.D_max) or (D==0.0):
                return 0.0
        else:
            psd[(D > self.D_max) | (D==0.0)] = 0.0
        return psd


class Binned(DSD):
    """Binned drop size distribution (DSD).
    
    Binned DSD given the bin edges and DSD values per bin.

    Args (constructor):
        The first argument to the constructor should specify n+1 bin edges, 
        and the second should specify n bin_psd values.        
        
    Args (call):
        D: the particle diameter.

    Returns (call):
        The PSD value for the given diameter.    
        Returns 0 for all diameters outside the bins.
    """
    
    def __init__(self, bin_edges, bin_psd):
        if len(bin_edges) != len(bin_psd)+1:
            raise ValueError("There must be n+1 bin edges for n bins.")
        
        self.bin_edges = bin_edges
        self.bin_psd = bin_psd
        
    def psd_for_D(self, D):       
        if not (self.bin_edges[0] < D <= self.bin_edges[-1]):
            return 0.0
        
        # binary search for the right bin
        start = 0
        end = len(self.bin_edges)
        while end-start > 1:
            half = (start+end)//2
            if self.bin_edges[start] < D <= self.bin_edges[half]:
                end = half
            else:
                start = half
                                
        return self.bin_psd[start]                    
        
    def __call__(self, D):
        if np.shape(D) == (): # D is a scalar
            return self.psd_for_D(D)
        else:
            return np.array([self.psd_for_D(d) for d in D])