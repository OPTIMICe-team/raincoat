# adapted from original script to handle data from different stations
# so that the Ny Alesund data can be processed with the same scripts
# RG 18.8.2017

import numpy as np


from parsivel_log_nc_convert import writeNC,writeNC_old

import matplotlib.mlab
matplotlib.use('Agg')

import glob

import sys
import os

import datetime


sites = sys.argv[1:]


logpath = {
  'jue':'/data/hatpro/jue/data/parsivel/*/',
  'nya':'/data/obs/site/nya/parsivel/l1/*/*/*/',
}

ncpath = {
  'jue':'/data/hatpro/jue/data/parsivel/netcdf/',
  'nya':'/data/obs/site/nya/parsivel/l1/',
}


noDaysAgo = {
  'jue':20,
  'nya':5,
}


for site in sites:

  #find log-files:
  files = sorted(glob.glob(logpath[site]+'parsivel*.log'))

  files = sorted(files)[::-1][:noDaysAgo[site]]   # go back the number of days specified


  for ff,flog in enumerate(files):

    #get date of file:
    datestring = flog.split("/")[-1][-12:-4]
    
    # get string to describe insrument
    descrstring = flog.split("/")[-1][0:13]

    # make output file directory, if needed
    if site == 'jue':  
      if not os.path.isdir(ncpath[site]+datestring[2:6]):
        os.mkdir(ncpath[site]+datestring[2:6])
    
    #build outputfilenames
    if   site == 'jue': 
      ncout = ncpath[site]+datestring[2:6]+'/'+descrstring+datestring+'.nc'
    elif site == 'nya': 
      ncout = ncpath[site] + datestring[0:4] + '/'+ datestring[4:6] + '/' + datestring[6:8] + '/parsivel_nya_' +  datestring+'.nc'
 
    if site == 'jue':
    #check if .nc-file already exists, if so: continue with next date.
    # this note done for nya, since files transfered hourly and should be updated
      if os.path.isfile(ncout):
        print "skipped .log: ", datestring
        continue
  
    #write parsivel .nc-file
    print "writing .nc: ",ncout
  
    if int(datestring) < 20150417:    #measurements earlier than this don't have array on N,v
        writeNC_old(flog,ncout)
    else:
        writeNC(flog,ncout, site)
  

