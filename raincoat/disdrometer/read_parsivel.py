# -*- coding: utf-8 -*-

import netCDF4 as nc
import numpy as np
import pandas as pd


def readPars(fileName, var_Ze="Ze", var_time="time", var_vmean="vmean", var_dmean="dmean", var_rr="rr", **kwargs):
	""" This function reads the parsivel netCDF files and
        extracts the desired variables.
        
        Arguments
        ---------
        fileName of the .nc parsivel data file
        var_Ze: variable name of radar reflectivity in Parsivel netcdf, default is "Ze"
        var_time: variable name of time in Parsivel netcdf, default is "time"
        var_vmean: variable name of mean velocity, default is "vmean"
        var_dmean: variable name of number concentration [log10(m-3 mm-1)], default is "dmean"
        var_rr: variable name of rain rate, default is "rr"

        Keyword arguments
        -------
        transpose: Should Z and V matrices be transposed (this is necessary if time dimension is the first dimension)

        Returns
        -------
        parsDataFrame_parsZe : DataFrame of the Parsivel Reflectivtiy values
        tPar				 : unixTime from Parsivel
        timesPar			 : converted unixTime to NormalTime
        log10_NPar			 : original Number concentration per diameter class
        zPar				 : original Reflectivity
        vPar				 : original velocity
        rainratePar			 : original rainrate
    """

	#Reading the NetCDF File from Parsivel Data
	parsNC = nc.Dataset(fileName, 'r')

	zPar_raw = parsNC.variables[var_Ze][:] 				# dB
	tPar_raw = parsNC.variables[var_time][:] 				# seconds since 1/1/1970 00:00:00
	vPar_raw = parsNC.variables[var_vmean][:]				# m/s
	log10_NPar_raw = parsNC.variables[var_dmean][:]		# log10(m-3 mm-1)
	rainratePar_raw = parsNC.variables[var_rr][:] 	# mm/h


	# check for type (as some files contained masked arrays) # IS THIS REALLY NECESSARY?
	if type(tPar_raw) == np.ma.core.MaskedArray:
		tPar_raw = tPar_raw.data

	if 'transpose' in kwargs and kwargs['transpose']:
		log10_NPar_raw = log10_NPar_raw.T
		vPar_raw = vPar_raw.T


	# check for valid time values (values above zero) # IS THIS REALLY NECESSARY?
	valid_idx = np.where(tPar_raw > 0)[0]
	
	# and save only valid indices from other values # IS THIS REALLY NECESSARY?
	tPar = tPar_raw[valid_idx]
	log10_NPar = log10_NPar_raw[:,valid_idx]
	zPar = zPar_raw[valid_idx]
	vPar = vPar_raw[:,valid_idx]
	rainratePar = rainratePar_raw[valid_idx]

	# convert unix time to normal time # THIS CAN BE DONE BETTER WITH nc.num2date, BUT SOLVE PREVIOUS MARKS FIRST
	epoch = pd.datetime(1970, 1, 1)
	timesPar = epoch + pd.to_timedelta(tPar,'s')

	# Create a DataFrame to look at the Data and to prepare for plot
	parsDataFrame = pd.DataFrame(data=zPar, columns=['Ze'], index=timesPar)
	parsDataFrame['unixtime'] = tPar
	parsDataFrame['rainrate'] = rainratePar

	nDataFrame = pd.DataFrame(data=log10_NPar.T, index=timesPar)
	vDataFrame = pd.DataFrame(data=vPar.T, index=timesPar)
	
	return parsDataFrame, nDataFrame, vDataFrame
