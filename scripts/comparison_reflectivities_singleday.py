# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
import glob

from raincoat.disdrometer.read_parsivel import readPars
from raincoat.FWD_sim import FWD_sim
#import raincoat.plot_func
import raincoat.disdrometer.pars_class as pc
from raincoat.radarFunctions import getVarTimeRange, getRadarVar
from raincoat.statistical_analysis.stat_anal_core import calculate_offset


# Definitions and Functions
pars_class, bin_edges = pc.pars_class()
# Create a list of parsivel and radar data
disdrofiles = glob.glob('../samplefiles/parsivel/parsivel_nya*.nc')
radarfiles = glob.glob('../samplefiles/radar/mirac*.nc')


# Events, Time and Height
start = pd.to_datetime('2018/09/05 10:00')
end = pd.to_datetime('2018/09/05 15:30')

# Height definition
height_bot = 120
height_top = 150

# Rain Scattering Table and Calculation of new W-Band Reflectivity

# path of rain scattering tables
filepath_rainscat = '../samplefiles/scattering/'
#filename = filepath_rainscat + '0.C_94.0GHz.csv'
filename = filepath_rainscat + '283.15_94.0GHz.csv'
#filename = filepath_rainscat + '273.15_9.6GHz.csv'

# Parsivel Calculations
disdroList = [readPars(i, var_Ze="Ze", var_time="time", var_vmean="vd", var_dmean="nd", var_rr="rr") for i in disdrofiles]
pDF = pd.concat([i[0] for i in disdroList]).sort_index() # Ze, time and rain rate
nDF = pd.concat([i[1] for i in disdroList]).sort_index() # log10(d mean)
vDF = pd.concat([i[2] for i in disdroList]).sort_index() # mean v

pDF = pDF[start:end]
nDF = nDF[start:end]
vDF = vDF[start:end]

DPars = pars_class[:, 0]  # [mm]
fwd_DF = FWD_sim(filename, pDF.index, nDF.values.T, bin_edges)

radarList = [getVarTimeRange(getRadarVar(i, '2001.01.01. 00:00:00', 'Ze'), height_bot, height_top, start, end)
             for i in radarfiles]
radarData = xr.concat(radarList, 'time')
radarFlat = 10.0*np.log10(radarData.values.flatten())

# statistical analysis
offset_dic = calculate_offset(radarFlat, fwd_DF['Ze_tmm'] - fwd_DF['A']*0.0005*(height_top+height_bot),
                              method='all', binsize=50, range_val=[-20, 30], shiftrange=20, shiftstep=0.1)

# display the raw and fwd operated histograms
n, bins, patches = plt.hist(radarFlat, range=[-20, 40], bins=50, density=True,
                            label='raw radar Ze', alpha=0.5)
n, bins, patches = plt.hist(fwd_DF['Ze_tmm'] - fwd_DF['A']*0.0005*(height_top+height_bot), range=[-20, 40], bins=50, density=True,label='fwd op Ze',alpha=0.5)
# display the shifted histograms
if "offset_calc_median" in offset_dic.keys():
  n, bins, patches = plt.hist(radarFlat+offset_dic["offset_calc_median"], range=[-20, 40], bins=50, density=True,
                              label='median corrected (+ {0:.2f})'.format(offset_dic["offset_calc_median"]),alpha=0.5)
if "offset_calc_overlap" in offset_dic.keys():
  n, bins, patches = plt.hist(radarFlat+offset_dic["offset_calc_overlap"], range=[-20, 40], bins=50, density=True,
                              label='max. overlap corrected (+ {0:.2f})'.format(offset_dic["offset_calc_overlap"]),alpha=0.5)
if "offset_calc_cumulative_dist" in offset_dic.keys():
	n, bins, patches = plt.hist(radarFlat+offset_dic["offset_calc_cumulative_dist"], range=[-20, 40], bins=50,
                                density=True,label='max. cumul. dist corrected (+ {0:.2f})'.format(offset_dic["offset_calc_cumulative_dist"]),alpha=0.5)

plt.legend()
plt.show()

# Test reflectivities
plt.figure()
plt.scatter(pDF.Ze, fwd_DF.Ze_tmm);
plt.scatter(pDF.Ze, fwd_DF.Ze_ray)
plt.show()
