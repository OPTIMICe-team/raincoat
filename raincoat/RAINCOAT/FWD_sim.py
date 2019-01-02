# -*- coding: utf-8 -*-
#%matplotlib inline

import netCDF4 as nc
from netCDF4 import Dataset
import numpy as np
import math
import pandas as pd
from csv import DictReader

from BinnedPSD import BinnedPSD



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
	scattab_df = pd.read_csv(filename)

	#set header names as variables
	diameter = 'diameter[mm]'
	radarxs = 'radarsx[mm2]'
	wavelength = 'wavelength[mm]'
	temp = 'T[k]'
	extxs = 'extxs[mm2]'

	#constants
	T = scattab_df.loc[1,temp]
	wavelen = scattab_df.loc[1,wavelength]
	K2 = scattab_df.loc[1,'K2']

	#integration constant
	int_const = wavelen**4 / ((math.pi)**5 *K2)

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
		N_ups = (10.0**log10_NPar[:,t])

		#convert all nan to zero
		N_ups = np.nan_to_num(N_ups)

		#calculate new PSD from parsivel bin_edges and upscaled parsivel psd
		PSD = BinnedPSD(bin_edges,N_ups)

		#calculate Attenuation with Ai = 4.343e-3 * int ext_xsect(D) * N(D) * dD 
		int_atten = scattab_df.loc[:,extxs]*PSD(diameter_ups)
		A[t] = 4.343e-3 * int_atten.sum()*delta

		#calculate upscaled reflectivity values with radar cross section from TMatrix Table (tm)
		#diameter**6 equivalent reflectivity
		d6 = PSD(diameter_ups)*scattab_df.loc[:,diameter]**6
		ZD6_pars[t] = d6.sum()*delta
		
		#w_band equivalent reflectivity
		wband_sim = PSD(diameter_ups)*scattab_df.loc[:,radarxs]
		Z_pars[t] = int_const * wband_sim.sum()*delta#np.trapz(y, dx = delta)

	#convert Ze from mm⁶/m³ into dBZ
	Ze_Pars_TM_dbz = 10 * np.ma.log10(np.abs(Z_pars))
	Ze_Pars_D6_dbz = 10 * np.ma.log10(np.abs(ZD6_pars))

	#save attenuation, d6 and tmm Ze into series and dataframe
	A_s = pd.Series(data=A, index=time)
	parsDataFrame_TM = pd.DataFrame(data=Ze_Pars_TM_dbz,columns=['Ze'], index=time)
	D6parsDataFrame = pd.DataFrame(data=Ze_Pars_D6_dbz,columns=['Ze'], index=time)  

	return A_s, parsDataFrame_TM, D6parsDataFrame  
