# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy as sc
import xarray as xr
import glob

from raincoat.dsd.dsd_core import Binned
from raincoat.disdrometer.read_parsivel import readPars
from raincoat.FWD_sim import FWD_sim
#import raincoat.plot_func
import raincoat.disdrometer.pars_class as pc
from raincoat.radarFunctions import getVarTimeRange, getRadarVar

#******************************************************************************
#Definitions and Functions
#******************************************************************************

pars_class, bin_edges = pc.pars_class()
# Create a lists of parsivel and radar data
disdrofiles = glob.glob('../samplefiles/parsivel/parsivel_nya*.nc')
radarfiles = glob.glob('../samplefiles/radar/mirac*.nc')

#******************************************************************************
#Events, Time and Height 
#******************************************************************************

start = pd.to_datetime('2018/09/05 10:00')
end = pd.to_datetime('2018/09/05 15:30')

#-Height definition
height_bot = 120
height_top = 150

#******************************************************************************
#Rain Scattering Table and Calculation of new W-Band Reflectivity
#******************************************************************************

#path of rain scattering tables
filepath_rainscat = '../samplefiles/scattering/'
#filename = filepath_rainscat + '0.C_94.0GHz.csv'
filename = filepath_rainscat + '283.15_94.0GHz.csv'
#filename = filepath_rainscat + '273.15_9.6GHz.csv'
	

#******************************************************************************
#Parsivel Calculations
#******************************************************************************
disdroList = [readPars(i) for i in disdrofiles]
pDF = pd.concat([i[0] for i in disdroList]).sort_index()
nDF = pd.concat([i[1] for i in disdroList]).sort_index()
vDF = pd.concat([i[2] for i in disdroList]).sort_index()

pDF = pDF[start:end]
nDF = nDF[start:end]
vDF = vDF[start:end]

DPars = pars_class[:,0] #[mm]
fwd_DF = FWD_sim(filename, pDF.index, nDF.values.T, bin_edges)

radarList = [ getVarTimeRange(getRadarVar(i, '2001.01.01. 00:00:00', 'Ze'), height_bot, height_top, start, end) for i in radarfiles]
radarData = xr.concat(radarList, 'time')
radarFlat = 10.0*np.log10(radarData.values.flatten())

n, bins, patches = plt.hist(radarFlat, range=[-20, 40], bins=50, density=True)
n, bins, patches = plt.hist(fwd_DF['Ze_tmm'] - fwd_DF['A']*0.0005*(height_top+height_bot), range=[-20, 40], bins=50, density=True)
plt.show()