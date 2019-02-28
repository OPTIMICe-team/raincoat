# -*- coding: utf-8 -*-
#%matplotlib inline

#import matplotlib.pyplot as plt #UNUSED
#import itertools #UNUSED
#from matplotlib.ticker import MultipleLocator #UNUSED unless commented text
#from matplotlib.offsetbox import AnchoredText #UNUSED
#from matplotlib.legend import Legend #UNUSED
#import matplotlib.gridspec as gridspec #UNUSED
#import netCDF4 as nc #UNUSED unless in commented part
#from netCDF4 import Dataset #UNUSED
import numpy as np
# import math UNUSED after switch to np.pi
import pandas as pd
import scipy as sc
from datetime import datetime, timedelta
import glob
#import os #UNUSED in not commented part
# import gzip #UNUSED
#import csv #UNUSED
#from collections import defaultdict #UNUSED
#from csv import DictReader #UNUSED
#import scipy.integrate as integrate #UNUSED used as sc.integrate


#from copy import deepcopy #UNUSED
#import string 

from raincoat.dsd.dsd_core import Binned
from raincoat.disdrometer.read_parsivel import readPars
from raincoat.FWD_sim import FWD_sim
import raincoat.plot_func

import raincoat.disdrometer.pars_class as pc

#******************************************************************************
#Definitions and Functions
#******************************************************************************

#******************************************************************************
# Creation of Parsivel class boundaries (class center and class width) and bin edges for PSD calculation
#******************************************************************************

pars_class = np.zeros(shape=(32,2))
bin_edges = np.zeros(shape=(33,1))

#pars_class[:,0] : Center of Class [mm]
#pars_class[:,1] : Width of Class [mm]
pars_class[0:10,1] = 0.125
pars_class[10:15,1] = 0.250
pars_class[15:20,1] = 0.500
pars_class[20:25,1] = 1.
pars_class[25:30,1] = 2.
pars_class[30:32,1] = 3.

# j = 0
# pars_class[0,0] = 0.062
# for i in range(1,32):
#     if i < 10 or (i > 10 and i < 15) or (i > 15 and i < 20) or (i > 20 and i < 25) or (i > 25 and i < 30) or (i > 30):
#         pars_class[i,0] = pars_class[i-1,0] + pars_class[i,1]

#     const = [0.188, 0.375, 0.75, 1.5, 2.5]
        
#     if i == 10 or i == 15 or i == 20 or i == 25 or i == 30:
#         pars_class[i,0] = pars_class[i-1,0] + const[j]
#         j = j + 1
        
#     bin_edges[i+1,0] = pars_class[i,0] + pars_class[i,1]/2


# bin_edges[0,0] = 0.
# bin_edges[1,0] = pars_class[0,0] + pars_class[0,1]/2

pars_class, bin_edges = pc.pars_class()
# Create a lists of parsivel and radar data
disdrofiles = glob.glob('../samplefiles/parsivel/parsivel_nya*.nc')
radarfiles = glob.glob('../samplefiles/radar/181202*.nc')

start = pd.to_datetime('2018/09/06 01:00')
end = pd.to_datetime('2018/09/06 03:30')

print(start)
print(end)

#******************************************************************************
#Events, Time and Height 
#******************************************************************************

#-Height definition
height_bot = 120
height_top = 200

#-Time definition
# year = '2017'
# month = '09'
# day = '16'

# hourBegin = '12'
# hourEnd = '23'

# minBegin = '00'
# minEnd =  '00'

# secBegin = '00'
# secEnd = '59'

# millisecBegin = '00'
# millisecEnd = '59'

# #-----------------
# strDate = ('').join([year,month,day])

# timeStart = ('').join([hourBegin, minBegin])
# timeEnd = ('').join([hourEnd, minEnd])

# start = pd.datetime(int(year), int(month), int(day),
#             int(hourBegin), int(minBegin),
#             int(secBegin))

# end = pd.datetime(int(year), int(month), int(day),
#           int(hourEnd), int(minEnd), int(secEnd))

#- Definition of height range to extract the data
#height = (height_bot, height_top)

#fileDate = ('').join([year, month, day])

#heightBot = str(height[0])
#heightTop = str(height[1])

#savepath = '/home/sschoger/RAINCOAT/'
#plotId = ('_').join([fileDate, timeStart, timeEnd, heightBot, heightTop])
#print plotId

#- To save the plots use plot = True
#plot = False
#plot = True

#******************************************************************************
#Rain Scattering Table and Calculation of new W-Band Reflectivity
#******************************************************************************

#path of rain scattering tables
filepath_rainscat = '../raincoat/scatTable/'
#filename = filepath_rainscat + '0.C_94.0GHz.csv'
filename = filepath_rainscat + '10C_9.6GHz.csv'
	

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

# parsDataFrame_parsZe = pars_tup[0]
# tPar = pars_tup[1]
# timesPar = pars_tup[2]
# log10_NPar	= pars_tup[3]
# zPar = pars_tup[4]
# vPar = pars_tup[5]
# rainratePar = pars_tup[6]


DPars = pars_class[:,0] #[mm]
#DPars_m = DPars*1e-3 # [m]

#calculate Rain Rate from Parsivel velocity ## THIS IS WRONG TO ME ... VELOCITY CLASSES DO NOT CORRESPOND TO DIAMETER CLASSES
#rho_w = 997 #[kg/m3]
#rrmoment_int = (vPar*(10.0**log10_NPar)).T*((DPars_m**3)) # HERE THERE MIGHT BE ALSO A PROBLEM WITH MEASURING UNITS

#rain rate in mm/h
#rPars_calc = 3600 * rho_w*np.pi/6 *  sc.integrate.trapz(np.nan_to_num(rrmoment_int), x=  pars_class[:,1])
#print rrPars

#FWD_tup = FWD_sim(filename, timesPar, log10_NPar, bin_edges)
fwd_DF = FWD_sim(filename, pDF.index, nDF.values.T, bin_edges)
A_s = FWD_tup[0]
parsDataFrame_TM = FWD_tup[1]
D6parsDataFrame = FWD_tup[2]

plot_func.plotPARS(parsDataFrame_TM, start, end, height, strDate, savepath+plotId,'PARSIVEL',  True)

#******************************************************************************
#W-Band Calculations
#******************************************************************************

#==============================================================================
# 
# if year == '2017' and month < '07' or (year == '2017' and month == '07' and day <= '27'):
# W_Band_Path = ('/').join(['/data/obs/site/nya/joyrad94/l1', year, month, day])
# #ncFiles = 'joyrad94_nya_compact_' + year + month + day + '*.nc'
# 
# ncFiles = [f for f in os.listdir(W_Band_Path) if (f.endswith('.nc') and f.startswith('joyrad94_nya_compact_'))]
# 
# label = 'W-Band (Joyrad94)'
# color = 'g'
# 
# if year > '2017' or (month >= '07' and day > '29') or month >= '08':
# W_Band_Path = ('/').join(['/data/obs/site/nya/mirac-a/l1', year, month, day])
# #ncFiles = 'joyrad94_nya_compact_' + year + month + day + '*.nc'
# 
# ncFiles = [f for f in os.listdir(W_Band_Path) if (f.endswith('.nc') and f.startswith('mirac-a_nya_compact_'))]
# 
# label = 'W-Band (MiRAC)'
# color = 'olive'
# 
# 
# for nn, ncFile in enumerate(ncFiles):
# try:
# ncData = nc.Dataset(W_Band_Path + '/' + ncFile,'r')
# except:
# raise RuntimeError("Could not open file: '" + ncFile+"'")
# 
# 
# keys = ncData.variables.keys()
# needed_keys = ['range', 'time', 'Ze', 'sampleTms']
# n_time = len(ncData.variables['time'])
# 
# #initialize dictionary
# if nn == 0:
# joinedData = {}
# 
# for key in keys:
# if key not in needed_keys:
#     continue
# 
# if ncData.variables[key].shape == ():
#     data = ncData.variables[key].getValue()
# else:
#     data = ncData.variables[key][:]
#     shape = data.shape
# 
# #concatenate values of different files
# if nn == 0:
#      joinedData[key] = data
# elif n_time in shape:
#        #print joinedData.keys()
#     t_axis = shape.index(n_time)
#     joinedData[key] = np.concatenate((joinedData[key],data),axis=t_axis)
# else:
#     continue
# 
# ncData.close()
# #if (tmpFile and ncFile.split(".")[-2] == "tmp"):
# #    os.remove(ncFile)
# 
# 
# #print joinedData['Ze'].shape
# #print joinedData['time'].shape
# 
# Ze_W_Band = joinedData['Ze']
# height_W_Band = joinedData['range']
# time_W_Band_secondssince = joinedData['time']
# sample_W_Band = joinedData['sampleTms']
# 
# 
# #convert Ze from mm⁶/m³ into dBZ
# #Ze_joyrad_dbz = []
# Ze_W_Band_dbz = 10 * np.log10(np.abs(Ze_W_Band))
# 
# type(time_W_Band_secondssince)
# 
# #print Ze_joyrad.shape
# #print time_joyrad_secondssince.shape
# #print Ze_joyrad_dbz.shape
# 
# #convert time into UTC
# reference_date = pd.datetime(2001,1,1,0,0,0)
# n_time_vec = len(time_W_Band_secondssince)
# 
# time_W_Band = reference_date + pd.to_timedelta(time_W_Band_secondssince, 'S') + pd.to_timedelta(sample_W_Band, 'ms')
# #print time_joyrad
# #print time_W_Band
# W_Band_DataFrame = pd.DataFrame(index=time_W_Band, columns= height_W_Band, data=Ze_W_Band_dbz)
# W_Band_DataFrame_null = pd.DataFrame(index=time_W_Band, columns= height_W_Band, data=np.nan_to_num(Ze_W_Band_dbz))
# 
# #plot_func.plot_W_Band(W_Band_DataFrame,start, end, height, strDate, plotId, label, plot)
#==============================================================================

#******************************************************************************
#MRR ImproToo Calculations
#******************************************************************************

#- MRR improtoo data path
#==============================================================================
# tmpDir = '/tmp'
# mrrDataPath = ('/').join(['/data/obs/site/nya/mrr/l1',year, month, day])
# mrrData_gzFile = year+month+day+'_nya_mrr_improtoo_0-101.nc.gz'
# 
# mrrData = ('/').join([mrrDataPath, mrrData_gzFile])
# print mrrData
# 
# if mrrData.split(".")[-1]=="gz":
# tmpFile = True
# mrrData_gzFile = deepcopy(mrrData)
# mrrData_ncFile = tmpDir+ '/' + year+month+day+'_nya_mrr_improtoo_0-101.tmp.nc'
# 
# print 'uncompressing of'
# print mrrData_gzFile
# print ' into '
# print mrrData_ncFile
# 
# returnValue = os.system("zcat "+mrrData_gzFile+">"+mrrData_ncFile)
# print returnValue
# assert returnValue == 0
# 
# #open Nc-File or give an Error message    
# try: 
# ncData = nc.Dataset(mrrData_ncFile,'r')
# except: 
# raise RuntimeError("Could not open file: '" +  mrrData_ncFile+"'")
# 
# #Reading MRR improtoo files
# timeMrr = ncData.variables['time'][:]
# heightMrr = ncData.variables['height'][:][0]
# Ze_Mrr = ncData.variables['Ze_noDA'][:]
# quality = ncData.variables['quality'][:]
# #print type(timeMrr)
# #saveing the right time
# epoch = pd.datetime(1970, 1, 1)
# timesMrr = epoch + pd.to_timedelta(timeMrr,'s')
# #print timesMrr[0:10]
# 
# mrrDataFrame = pd.DataFrame(index=timesMrr, columns= heightMrr, data=Ze_Mrr)
# 
# #print mrrDataPath
# 
# ncData.close()
# #plot_func.plotMRR(mrrDataFrame,start, end, height, strDate, plotId, 'K_band_MRR', True)
# 
# if (tmpFile and mrrData_ncFile.split(".")[-2] == "tmp"): os.remove(mrrData_ncFile)
#==============================================================================

#******************************************************************************
#Editing arrays
#******************************************************************************

#block comment begin
#==============================================================================
# # MRR    
# dfSelTimeMrr = mrrDataFrame[start:end]
# dfSelTimeRangeMrr = dfSelTimeMrr.transpose()[height[0]:height[1]]
# dfArrayMrr = np.array(dfSelTimeRangeMrr.transpose(), np.float)
# 
# # It makes the array one dimensional and
# # removes the nan values 
# dfArrayFlatMrr = dfArrayMrr.flatten()
# dfArrayFlatMrr =  dfArrayFlatMrr[~np.isnan(dfArrayFlatMrr)]    
# 
# # W-Band
# dfSelTime_W_Band = W_Band_DataFrame[start:end]
# dfSelTimeRange_W_Band = dfSelTime_W_Band.transpose()[height[0]:height[1]]
# dfArray_W_Band = np.array(dfSelTimeRange_W_Band.transpose(), np.float)
# 
# # It makes the array one dimensional and
# # removes the nan values 
# dfArrayFlat_W_Band = dfArray_W_Band.flatten()
# dfArrayFlat_W_Band =  dfArrayFlat_W_Band[~np.isnan(dfArrayFlat_W_Band)]
# 
# # Parsivel
# TM_ParsDF = parsDataFrame_TM[start:end]
# #    TM_ParsDF = TM_ParsDF.dropna()    
# TM_ParsDF = TM_ParsDF[(TM_ParsDF.Ze > -30)]
# 
# D6ParsDF =  D6parsDataFrame[start:end]
# D6ParsDF = D6ParsDF[(D6ParsDF.Ze > -9)]
# #parsDataFrame_parsZe=10.0*np.ma.log10(parsDataFrame_parsZe)
# 
# #for internal Ze parsivel choose values above -5 as default is -9.999
# parsZeDF = parsDataFrame_parsZe[start:end]
# parsZeDF = parsZeDF[(parsZeDF.Ze > -9)]
# 
# 
# dfArrayFlatMrr = dfArrayFlatMrr[dfArrayFlatMrr > -9]
# #dfArrayFlatMrrOld = dfArrayFlatMrrOld[dfArrayFlatMrrOld > -5]
# 
# #min_value = min(TM_ParsDF.Ze)
# #    dfArrayFlat_W_Band = dfArrayFlat_W_Band[dfArrayFlat_W_Band > min_value]
# dfArrayFlat_W_Band = dfArrayFlat_W_Band[dfArrayFlat_W_Band > -30]
# #print(TM_ParsDF.Ze)
# 
# A_mean = A_s[start:end].mean()
# 
# #calculating the median and their differencees
# med_TMpars = np.median(TM_ParsDF.Ze)
# 
# med_D6pars = np.median(D6ParsDF.Ze)
# 
# med_Zepars = np.median(parsZeDF.Ze)
# 
# med_WBand = np.median(dfArrayFlat_W_Band)
# 
# med_Mrr = np.median(dfArrayFlatMrr)
# 
# diff_TMparsW =  med_TMpars - med_WBand
# deltaZe_TMW = np.round(diff_TMparsW,1)
# 
# diff_D6parsW =  med_D6pars - med_WBand
# deltaZe_D6parsW = np.round(diff_D6parsW,1)
# 
# diff_ZeparsW =  med_Zepars - med_WBand
# deltaZe_parsZeW = np.round(diff_ZeparsW,1)
# 
# diff_ZeparsMrr = med_Zepars - med_Mrr
# deltaZe_mrr_pars = np.round(diff_ZeparsMrr,1)
# 
# diff_ZeparsMrr = med_D6pars - med_Mrr
# deltaZe_mrr_D6 = np.round(diff_ZeparsMrr,1)
# 
# diff_TMparsMrr = med_TMpars -med_Mrr
# deltaZe_TMmrr = np.round(diff_TMparsMrr,1)
# 
#==============================================================================
#block comment end

#******************************************************************************
#PLOTTING
#******************************************************************************

#block comment begin
#==============================================================================
# xmin = -10
# xmax = 40
# 
# ymin = 0
# ymax = 0.25    
# 
# fig = plt.figure(figsize=(15,6))
# 
# #### first plot  
# ax1 = plt.subplot(2,1,1) 
# plt.tight_layout()
# 
# #alpha = transparency[0,1] 
# 
#                    
# #    n, bins, patches = plt.hist(D6ParsDF.Ze, bins = 50, range=(xmin,xmax),
# #                               normed=1, facecolor='darksalmon',
# #                               alpha=0.6, label = 'D6 Ze')
# 
# #    n, bins, patches = plt.hist(parsZeDF.Ze, bins = 50, range=(xmin,xmax), 
# #                               normed=1, facecolor='salmon',
# #                               alpha=0.6, label = 'Parsivel Ze')
#                    
# 
# n, bins, patches = plt.hist(dfArrayFlat_W_Band, bins = 50, range=(xmin,xmax),
#                  normed=1, facecolor= color,
#                alpha=0.6, label = label)
# 
# n, bins, patches = plt.hist(TM_ParsDF.Ze, bins = 50, range=(xmin,xmax),
#                    normed=1, facecolor='darkred',
#                    alpha=0.6, label = 'TMM (new Ze)')
#                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
# plt.ylabel('PDF', fontsize=18)
# plt.xlabel('Ze [dBZ]', fontsize=18)
# plt.title((' ').join([strDate, start.strftime('%H:%M'), '-',
#               end.strftime('%H:%M'), str(height[0]), '-',
#               str(height[1]),'[m]']), fontsize=18)
# 
# majorLocator = MultipleLocator(5)
# minorLocator = MultipleLocator(2.5)
# 
# ax1.xaxis.set_major_locator(majorLocator)
# 
# # for the minor ticks, use no labels; default NullFormatter
# ax1.xaxis.set_minor_locator(minorLocator)
# 
# #plt.xticks(np.arange(-50, 35, 5),fontsize=18)
# plt.xticks(fontsize=20)
# plt.yticks(fontsize=20)
# 
# #plt.ylim(0,ymax)
# plt.xlim(xmin, xmax)
# plt.ylim(ymin, ymax)
# plt.grid(which = 'both')
# first_legend = plt.legend(fontsize=16, loc = 1)
# plt.gca().add_artist(first_legend)
# 
# #    plt.text(xmin+0.1, 0.15, 'Minimum Ze-Value: %5.2f dBZ'%min_value, fontsize=18)
# plt.text(xmin+0.1, 0.12, 'Attenuation:  \n %5.4f dB/m'% (A_mean/1000.), fontsize=18)
# 
# 
# 
# #    D6pars = ax1.axvline(x=med_D6pars, ymin= 0, ymax = 1, color = 'darksalmon', linewidth = 4, 
# #               linestyle='dashed',alpha = 0.8, label = 'median D6 = '+ "%5.2f" % med_D6pars+' dBZ')
# 
# #    Zepars = ax1.axvline(x=med_Zepars, ymin= 0, ymax = 1, color = 'salmon', linewidth = 4, 
# #               linestyle='dashed',alpha = 0.8, label = 'median Pars = '+ "%5.2f" % med_Zepars+' dBZ')
# 
# Wband = ax1.axvline(x=med_WBand, ymin= 0, ymax = 1, color = color, linewidth = 4, 
#    linestyle='dashed',alpha = 0.8, label = 'median W-Band = '+ "%5.2f" % med_WBand+' dBZ')
# 
# TMpars = ax1.axvline(x=med_TMpars, ymin= 0, ymax = 1, color = 'darkred', linewidth = 4, 
#    linestyle='dashed',alpha = 0.8, label = 'median TMM = '+ "%5.2f" % med_TMpars+' dBZ')
# 
# #    handles1 = [TMpars, Zepars, Wband]
# handles2 = [TMpars, Wband]
# 
# plt.axhline(y = 0.14, xmin=calcPosition(med_WBand, xmin, xmax), 
#     xmax=calcPosition(med_TMpars, xmin, xmax), color='k')
# 
# #    plt.axhline(y = 0.07, xmin=calcPosition(med_WBand, xmin, xmax), 
# #                xmax=calcPosition(med_Zepars, xmin, xmax), color='k')
#     
# #    plt.axhline(y = 0.09, xmin=calcPosition(med_WBand, xmin, xmax), 
# #                xmax=calcPosition(med_D6pars, xmin, xmax), color='k')
# 
# plt.text(med_WBand + deltaZe_TMW/6., 0.15, str(deltaZe_TMW)+' dB', fontsize=18)
# 
# #    plt.text(med_WBand + deltaZe_parsZeW/6., 0.08, str(deltaZe_parsZeW)+' dB', fontsize=18)
# 
# #    plt.text(med_WBand + deltaZe_D6parsW/6., 0.1, str(deltaZe_D6parsW)+' dB', fontsize=18)
# 
# 
# 
# #handles, labels = ax.get_legend_handles_labels()
# second_legend = plt.legend(handles = handles2, fontsize=16,loc = 2)#, bbox_to_anchor=(0.01, 1.125), borderaxespad=0.)
# ax1 = plt.gca().add_artist(second_legend)
# #ax.add_artist(second_leged)
# 
# 
# #### second plot    
# ax2 = plt.subplot(2,1,2) 
# 
# n, bins, patches = plt.hist(dfArrayFlatMrr, bins = 50, range=(xmin,xmax),
#                 normed=1, facecolor='b', 
#                 alpha=0.6, label = 'K-Band (MRR Max)')
#                 
# #    n, bins, patches = plt.hist(parsZeDF.Ze, bins = 50, range=(xmin,xmax), 
# #                               normed=1, facecolor='salmon',
# #                               alpha=0.6, label = 'Parsivel Ze')
# #                               
# n, bins, patches = plt.hist(D6ParsDF.Ze, bins = 50, range=(xmin,xmax), 
#                    normed=1, facecolor='darksalmon',
#                    alpha=0.6, label = 'Ze D6 calc')
# #    if ii >= 2:
# #        
# #        n, bins, patches = plt.hist(TM_ParsDF.Ze, bins = 50, range=(xmin,xmax),
# #                                normed=1, facecolor='darkred',
# #                               alpha=0.6, label = 'TMM (new Ze)')
# #
# #        plt.axhline(y = 0.14, xmin=calcPosition(med_Mrr, xmin, xmax), 
# #                xmax=calcPosition(med_D6pars, xmin, xmax), color='k')
# #        plt.text(med_Mrr + deltaZe_TMmrr/6., 0.15, str(deltaZe_TMmrr)+' dB', fontsize=18)
# 
# #    plt.title((' ').join([strDate, start.strftime('%H:%M'), '-',
# #                          end.strftime('%H:%M'), str(height[0]), '-',
# # sschoger/Dropbox/WHK/                         str(height[1]),'[m]']), fontsize=18)
# 
# majorLocator = MultipleLocator(5)
# minorLocator = MultipleLocator(2.5)
# 
# ax2.xaxis.set_major_locator(majorLocator)
# 
# # for the minor ticks, use no labels; default NullFormatter
# ax2.xaxis.set_minor_locator(minorLocator)
# 
# #plt.xticks(np.arange(-50, 35, 5),fontsize=18)
# plt.xticks(fontsize=20)
# plt.yticks(fontsize=20)
# 
# #plt.ylim(0,ymax)
# plt.xlim(xmin, xmax)
# plt.ylim(ymin, ymax)
# plt.grid(which = 'both')
# first_legend = plt.legend(fontsize=16, loc = 1)
# plt.gca().add_artist(first_legend)
# 
# #    Zepars = ax2.axvline(x=med_Zepars, ymin= 0, ymax = 1, color = 'salmon', linewidth = 4, 
# #                         linestyle='dashed',alpha = 0.8, label = 'median Pars = '+ "%5.2f" % med_Zepars+' dBZ')
# 
# Mrr = ax2.axvline(x=med_Mrr, ymin= 0, ymax = 1, color = 'b', linewidth = 4, linestyle='dashed',alpha = 0.8, label = 'median Mrr = '+ "%5.2f" % med_Mrr+' dBZ')
# 
# D6pars = ax2.axvline(x=med_D6pars, ymin= 0, ymax = 1, color = 'peachpuff', linewidth = 4, 
#           linestyle='dashed',alpha = 0.8, label = 'median D6pars = '+ "%5.2f" % med_D6pars+' dBZ')
#           
# #    handles = [Zepars, Mrr, D6pars]
# handles = [Mrr, D6pars]
# #   
# #    if ii >= 2:
# #
# #        TMpars = ax2.axvline(x=med_TMpars, ymin= 0, ymax = 1, color = 'darkred', linewidth = 4, 
# #               linestyle='dashed',alpha = 0.8, label = 'median TMM = '+ "%5.2f" % med_TMpars+' dBZ')
# #        handles=[Mrr,D6pars,TMpars]
# 
# #    plt.axhline(y = 0.12, xmin=calcPosition(med_Mrr, xmin, xmax), 
# #                xmax=calcPosition(med_Zepars, xmin, xmax), color='k')
# #    plt.text(med_Mrr + deltaZe_mrr_pars/6., 0.13, str(deltaZe_mrr_pars)+' dB', fontsize=18)
# 
# plt.axhline(y = 0.09, xmin=calcPosition(med_Mrr, xmin, xmax), 
#     xmax=calcPosition(med_D6pars, xmin, xmax), color='k')
# plt.text(med_Mrr + deltaZe_mrr_D6/6., 0.1, str(deltaZe_mrr_D6)+' dB', fontsize=18)
# 
# second_legend = plt.legend(handles = handles, fontsize=16,loc = 2)
# ax2 = plt.gca().add_artist(second_legend)
# 
# #plot=True
# #plot=False
# 
# if plot == True: 
# out = plotId+'_'
# plt.savefig(savepath+out+'pdf_analysis_'+str(ii)+'_final.png', format='png', dpi=200,bbox_inches='tight')
# #print out+'pdf_analysis'+'.png'
#==============================================================================

#block comment end

#block comment begin

#==============================================================================
# Scatter Plots
#        
#    out = plotId+'_'    
#    commonIndex = TM_ParsDF.index.intersection(parsZeDF.index)
#    plt.figure()
#    plt.scatter(parsZeDF.loc[commonIndex],TM_ParsDF.loc[commonIndex],label='TMM',marker='h', c='r')
#    plt.scatter(parsZeDF.loc[commonIndex],D6ParsDF.loc[commonIndex],label='D6',marker='x', c = 'k')
#    ax=plt.gca()
#    ax.set_xlim([-5,35])
#    ax.set_ylim([-5,35])
#    plt.plot(ax.get_xlim(),ax.get_ylim())
#    plt.legend(loc=3)
#    plt.grid()
#    plt.xlabel('Parsivel reflectivity  [dBZ]')
#    plt.ylabel('Computed reflectivity  [dBZ]')
##    plt.savefig(out+'scatter_analysis_'+str(ii)+'.png', format='png', dpi=200,bbox_inches='tight')
##    
#    
#    #average W-Band times to 1 min (same temp resolution as mrr)
#    W_Band_df_min = W_Band_DataFrame_null.resample('1T',label='right').mean()
#    W_Band_mrrheight = np.zeros((heightMrr.shape[0], timeMrr.shape[0]))
#
#    #average W-Band heights over 30 meter (same vertical resolution as mrr)
#    #starting at height heightMrr = 90m 
#    for ind, hval in enumerate(heightMrr):
#        W_Band_mrrheight[ind,:] = np.nan
#        #print ind
#        if hval >= 120.:
#            #print hval
#            W_Band_mrrheight[ind,:] = W_Band_df_min.transpose()[hval-30:hval].mean()
#    W_Band_mrrheight_df = pd.DataFrame(index=W_Band_df_min.index, columns= heightMrr, data=W_Band_mrrheight.transpose())
#    
#    dfSelTimeMin_W_Band = W_Band_mrrheight_df[start:end]
#    dfSelTimeMinRange_W_Band = dfSelTimeMin_W_Band.transpose()[height[0]:height[1]]
#    
#    DWR = dfSelTimeRangeMrr - dfSelTimeMinRange_W_Band
#    
#    commonIndex = dfSelTimeRangeMrr.transpose().index.intersection(dfSelTimeMinRange_W_Band.transpose().index)
#    plt.figure()
#    plt.scatter(dfSelTimeRangeMrr.mean().loc[commonIndex],DWR.mean().loc[commonIndex],s=5)
#    ax=plt.gca()
#    ax.set_xlim([-5,35])
#    ax.set_ylim([-5,35])
#    plt.plot(ax.get_xlim(),ax.get_ylim())
#    plt.legend()
#    plt.grid()
#    plt.title(strDate)
#    plt.xlabel('MRR reflectivity  [dBZ]')
#    plt.ylabel('$\Delta$  $(Z_e(MRR) - Z_e(MiRAC)$)  [dBZ]')
#    plt.savefig(out+'scatter_Mrr_DWR.png', format='png', dpi=200,bbox_inches='tight')
#    
#    #Scatterplot TMM Ze against Ze MiRAC
#    
#    TM_ParsDF_5min = TM_ParsDF.resample('5T',label='right').mean()
#    W_Band_df_5min = dfSelTimeRange_W_Band.transpose().resample('5T', label='right').mean()
#    
#    commonIndex = TM_ParsDF_5min.index.intersection(W_Band_df_5min.index)
#
#    plt.figure()
#    plt.scatter(TM_ParsDF_5min.loc[commonIndex],W_Band_df_5min.transpose().mean().loc[commonIndex],s=5)
#    ax=plt.gca()
#    ax.set_xlim([-5,35])
#    ax.set_ylim([-5,35])
#    plt.plot(ax.get_xlim(),ax.get_ylim())
#    plt.legend()
#    plt.grid()
#    plt.title(strDate)
#    plt.xlabel('$Z_e$ (TMM) [dBZ]')
#    plt.ylabel('$Z_e$ (MiRAC)  [dBZ]')
#    plt.savefig(out+'scatter_TMM_MiRAC.png', format='png', dpi=200,bbox_inches='tight')
#
#
#    #Scatterplot Parsivel Ze against Ze MRR
#
#    parsZeDF_5min = parsZeDF.resample('5T',label='right').mean()
#    Mrr_df_5min = dfSelTimeRangeMrr.transpose().resample('5T', label='right').mean()
#    
#    commonIndex = parsZeDF_5min.index.intersection(W_Band_df_5min.index)
#
#    plt.figure()
#    plt.scatter(parsZeDF_5min.loc[commonIndex],Mrr_df_5min.transpose().mean().loc[commonIndex],s=5)
#    ax=plt.gca()
#    ax.set_xlim([-5,35])
#    ax.set_ylim([-5,35])
#    plt.plot(ax.get_xlim(),ax.get_ylim())
#    plt.legend()
#    plt.grid()
#    plt.title(strDate)
#    plt.xlabel('$Z_e$ (Parsivel) [dBZ]')
#    plt.ylabel('$Z_e$ (MRR) [dBZ]')
#    plt.savefig(out+'scatter_Pars_Mrr.png', format='png', dpi=200,bbox_inches='tight')

#==============================================================================

#     
#     plt.figure(figsize=(15,6))
#     ax1 = plt.subplot(2,1,1) 
#     plt.tight_layout()
#     plot_func.refl_check(W_Band_DataFrame,start, end, height, strDate, plotId, pd.datetime(2001, 1, 1, 0, 0, 0))
# 
#     ax2 = plt.subplot(2,1,2) 
#     plt.tight_layout()
#     refl_check(mrrDataFrame, plotId, pd.datetime(1970, 1, 1))
#==============================================================================

#==============================================================================
#     if plot == True: 
#         out = plotId+'_'
#         plt.savefig(out+'.png', format='png', dpi=200,bbox_inches='tight')
#         print out+'.png'
#==============================================================================

#if ii == 0: break

plt.show()
