# -*- coding: utf-8 -*-
""" TMMrain module
Copyright (C) 2019 Sybille  and RAINCOAT team - University of Cologne

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

import numpy as np
import pandas as pd

from raincoat.dsd.dsd_core import Binned



def FWD_sim(filename, time, log10_NPar, bin_edges):
	""" This function reads the the scattering table csv, calculates reflectivities with upscaled parsivel values and
        extracts the calculated reflectivities and attenuation.
        
        Arguments
        ---------
        filename 	: scattering table filename
        time		: parsivel time
        log10_Npar	: PSD in logspace from parsivel
        bin_edges	: parsivel class bin_edges
        
        Returns
        -------
		A_s				 : Attenuation for simulated W-Band Reflectivity
		parsDataFrame_TM : Reflectivity for W-Band comparison calculated from parsivel PSD
		D6parsDataFrame  : Reflectivity for normal D**6 comparison calculated from parsivel PSD
    """
	#set return variables
	Z_pars = np.zeros(len(time))
	ZD6_pars = np.zeros(len(time))
	A = np.zeros(len(time))

	#read rain scattering tables into python with pandas as dataframe
	scattab_df = pd.read_csv(filename, skiprows=1)
	with open(filename, 'r') as f:
		firstline = f.readline()
	parameters = eval(firstline)

	#set header names as variables
	diameter = 'diameter[mm]'
	radarxs = 'radarXSh[mm2]'
	wavelength = 'wavelength[mm]'
	#temp = 'T[k]'
	extxs = 'extxs[mm2]'

	#constants
	#T = scattab_df.loc[1,temp] #unused
	wavelen = parameters['wl']
	K2 = parameters['K2']

	#integration constant
	int_const = wavelen**4 / (np.pi**5 * K2)

	#variables
	D = scattab_df.loc[:,diameter]
	radar_cross = scattab_df.loc[:,radarxs]
	ext_cross = scattab_df.loc[:,extxs]

	#upscale Parsivel resolution to rain scattering table resolution of 0.01 mm
	delta = 0.01 # [mm]
	upscale_end = (len(scattab_df)+1.)/100.
	diameter_ups = np.arange(delta,upscale_end,delta)

	for t, val in enumerate(time):
		#upscale parsivel resolution
		N_ups = (10.0**log10_NPar[:,t]) # mm**-1 m**-3

		#convert all nan to zero
		N_ups = np.nan_to_num(N_ups)

		#calculate new PSD from parsivel bin_edges and upscaled parsivel psd
		PSD = Binned(bin_edges,N_ups)

		#calculate Attenuation with Ai = 2.0 * 4.343e-3 * int ext_xsect(D) * N(D) * dD # Correction for 2way
		int_atten = scattab_df.loc[:,extxs]*PSD(diameter_ups)
		A[t] = 8.686e-3 * int_atten.sum()*delta # Correction for 2way

		#calculate upscaled reflectivity values with radar cross section from TMatrix Table (tm)
		#diameter**6 equivalent reflectivity
		d6 = PSD(diameter_ups)*scattab_df.loc[:,diameter]**6
		ZD6_pars[t] = d6.sum()*delta # mm**6 m**-3
		
		#w_band equivalent reflectivity
		wband_sim = PSD(diameter_ups)*scattab_df.loc[:,radarxs]
		Z_pars[t] = int_const * wband_sim.sum()*delta # mm**6 m**-3

	#convert Ze from mm⁶/m³ into dBZ
	Ze_Pars_TM_dbz = 10.0 * np.ma.log10(np.abs(Z_pars))
	Ze_Pars_D6_dbz = 10.0 * np.ma.log10(np.abs(ZD6_pars))

	outDF = pd.DataFrame(data=Ze_Pars_TM_dbz,columns=['Ze_tmm'], index=time)
	outDF['Ze_ray'] = Ze_Pars_D6_dbz
	outDF['A'] = A
	return outDF
