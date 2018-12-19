import numpy as np

import datetime
import calendar

import matplotlib.mlab
matplotlib.use('Agg')

from netCDF4 import Dataset

import io

import collections

def time2unix(datestring):
    try:
        f = datetime.datetime.strptime(datestring,"%Y%m%d%H%M%S.%f")
        unix = calendar.timegm(f.timetuple())
    except ValueError:
        unix = np.nan
    return unix


def count_file_lines(fname, site):

    if   site == 'jue':
        f = open(fname, 'r')
    elif site == 'nya':
        f = io.open(fname, 'r', encoding='ISO-8859-1')
    
    line_total = sum(1 for line in f)
    
    f.close()
    return line_total




def readASCII_old(logfile):     #valid for reading in .logs from Aug.2013 until April 17th,2015
    
     #read .log-file:
    dic = {}
    
    colnames = ['unixtime',\
                'rr','r_accum','wawa','z','vis','interval','amp','nmb','T_sensor',\
                'serial_no','version',\
                'curr_heating','volt_sensor',\
                'status_sensor','station_name',\
                'r_amount',\
                'error_code',\
                'n', 'v'    ]   
   #0: datetime string, 1-9:float, 10,11:string, 12,13: float, 14,15: string, 16:float, 17:string 
    
    #check for bad lines to skip:

    
    iline = 0
        
    filelen = count_file_lines(logfile)
   
    rowlen = 570.       # default for files!
    
  
    #set keys where strings will be put in, to string arrays:
    for k,key in enumerate(colnames):
        if k == 10 or k == 11 or k == 14 or k == 15 or k == 17:
            dic[key] = np.empty(filelen,dtype = 'S20')
        elif k == 18 or k == 19:
            dic[key] = np.zeros([32,filelen])
        else:
            dic[key] = np.nan * np.ones(filelen)

    
    #read file:
    f = open(logfile,'r')
    
    
    for line in f:  # for each line split up string, put value into corresponding array if rowlen normal. 
        
        line = line.strip()
        cols = line.split(';')
        #1/0
        
        for i,cname in enumerate(colnames):
            if len(line) == rowlen: 
                if i == 0:
                    #datetime = cols[i] 
                    dic[cname][iline] = time2unix(cols[i])
                
                
                elif i == 10 or i == 11 or i == 14 or i == 15 or i == 17:   #all columns containing strings
                    dic[cname][iline] = str(cols[i])
                 
                
                elif i == 18:
                    for aa in range(32):
                        dic[cname][aa,iline] = float(cols[i+aa])
                        if dic[cname][aa,iline] == -9.999 : dic[cname][aa,iline] = np.nan
                elif i == 19:
                    for aa in range(32):
                        dic[cname][aa,iline] = float(cols[50+aa])
                        if dic[cname][aa,iline] == -9.999 : dic[cname][aa,iline] = np.nan       
                        
                        
                else: dic[cname][iline] = float(cols[i])
        dic['rr'][:] = dic['rr'][:]*60.    #convert from mm/min to mm/h
        iline += 1
        
    f.close()
    
            
    return dic



################################################################################
##############################################################################



def readASCII(logfile, site):     #valid for reading in .logs later than April 17th,2015
    
     #read .log-file:
    dic = {}
    
    colnames = ['unixtime',\
                'rr','r_accum','wawa','z','vis','interval','amp','nmb','T_sensor',\
                'serial_no','version',\
                'curr_heating','volt_sensor',\
                'status_sensor','station_name',\
                'r_amount',\
                'error_code',\
                'n', 'v',
                'M']   
    
   #0: datetime string, 1-9:float, 10,11:string, 12,13: float, 14,15: string, 16:float, 17:string, 18,19: array(32,filelen), 20: array(32,32,filelen)
    
    #check for bad lines to skip:
    
    iline = 0
        
    filelen = count_file_lines(logfile, site)
   
#    if site == 'jue':
#        if int(logfile[-12:-4]) > 20160625 :
#            rowlen = 4662.0  # Station name JOYCE
#        elif 20151016  < int(logfile[-12:-4]) and  int(logfile[-12:-4]) < 20151020 :
#            rowlen = 4665.
#        elif 20151001  < int(logfile[-12:-4]) and  int(logfile[-12:-4]) < 20151015 :
#            rowlen = 4660. 
#        else:
#            rowlen = 4666.0  # Station name Parsivel4
#
#    elif site == 'nya':
#        rowlen = 4660.0
  
    #set keys where strings will be put in, to string arrays:
    for k,key in enumerate(colnames):
        if k == 10 or k == 11 or k == 14 or k == 15 or k == 17:
            dic[key] = np.empty(filelen,dtype = 'S20')
        elif k == 18 or k == 19:
            dic[key] = np.zeros([32,filelen])
        elif k == 20:
            dic[key] = np.zeros([32,32,filelen])
        else:
            dic[key] = np.nan * np.ones(filelen)

    
    #read file:
    if site == 'jue':
        f = open(logfile,'r')
    elif site == 'nya':
        f = io.open(logfile,'r', encoding='ISO-8859-1')

    for line in f.readlines():  # for each line split up string, put value into corresponding array if rowlen normal.         
        line = line.strip()
        cols = line.split(';')

        if 20150917 < int(logfile[-12:-4]) and  int(logfile[-12:-4]) < 20151017 :
            cols = [s.replace('<', '') for s in cols]
            cols = [s.replace('>', '') for s in cols]


        #1/0
        #print 'len(line)', len(line), rowlen, len(line) == rowlen, 'len(cols)', len(cols), len(cols) == 1107

        for i,cname in enumerate(colnames):         # loop through columns
            #if len(line) == rowlen :# and cols[14] < 2:     # check status of parsivel: if 0 or 1: sensor usable, if 2 or 3: not usable.
            if 1 == 1:
                try:
                    test = float(cols[0][0:4])
                except: continue

                if test < 2000: # time stamp missing or in the wrong place
                    continue

                if len(cols) == 1106:
                    tempcols = collections.deque(cols)
                    tempcols.extendleft([cols[0][0:18]])
                    tempcols[1] = tempcols[1][18:-1]
                    cols = list(tempcols)
                elif len(cols) != 1107:
                    continue

                if i == 0:
                    dic[cname][iline] = time2unix(cols[i])
                
                
                elif i == 10 or i == 11 or i == 14 or i == 15 or i == 17:   #all columns containing strings
                    dic[cname][iline] = str(cols[i])
                 
                
                elif i == 18:
                    for aa in range(32):
                        try:
                            dic[cname][aa,iline] = float(cols[i+aa])    #cols 18 upto 49 (32 values)
                        except ValueError:
                            dic[cname][aa,iline] = np.nan
                            
                        if dic[cname][aa,iline] == -9.999 : dic[cname][aa,iline] = np.nan
                        
                elif i == 19:
                    for aa in range(32):
                        try:
                            dic[cname][aa,iline] = float(cols[50+aa])   #cols 50 upto 81 (32 values)
                        except ValueError:
                            dic[cname][aa,iline] = np.nan
                            
                        if dic[cname][aa,iline] == -9.999 : dic[cname][aa,iline] = np.nan       
                        
                
                elif i == 20:
                    for bb in range(32):    #loop through falling velocities, ie rows in matrix
                        for aa in range(32):    #loop through sizes, ie columns
                            try:
                                dic[cname][aa,bb,iline] = float(cols[82+32*aa+bb])
                                if float(cols[82+32*aa+bb]) < 1000000: dic[cname][aa,bb,iline] = np.nan
                            except ValueError:
                                dic[cname][aa,bb,iline] = np.nan
                            
                            
                            
                else: 
                    #if i == 1: 1/0
                    if len(cols) == 1107:    # RG 5.8.2016: if some different lenght, something wrong with this line (e.g. time stamp missing)
                        try:
                            dic[cname][iline] = float(cols[i])
                       
                        except ValueError:
                            dic[cname][iline] = np.nan
                    else :
                        dic[cname][iline] = np.nan


        #if iline == 1: 1/0        
        iline += 1
    f.close()
    
    
    
    return dic

################################################################################################
################################################################################################

def writeNC_old(logfile,ncname):    #valid for data Aug2013-Apr17,2015
    
    #read .log-file into dictionnary:
    data = readASCII_old(logfile)
    
    #get number of lines in file ie length of data columns
    filelen = len(data['unixtime'])
    
    #open .nc outfile.
    ncout = Dataset(ncname,'w',format='NETCDF4') 
    
    # define dimensions:
    dim = ncout.createDimension('dim', filelen)       #filelen, set='none' if unlimited dimension
    ndim = ncout.createDimension('ndim',32)
    stri = ncout.createDimension('stri',None)
    
    
    #read variables:
    
    time = ncout.createVariable('time','i8',('dim',))      #time in double-precision...
    time.units = 'seconds since 1/1/1970 00:00:00'
    time[:] = data['unixtime']
  
    rain_rate = ncout.createVariable('rain_rate','f',('dim',))
    rain_rate.units = 'mm/h'
    rain_rate[:] = data['rr']


    rain_accum = ncout.createVariable('rain_accum','f',('dim',))
    rain_accum.units = 'mm'
    rain_accum[:] = data['r_accum']
  
    wawa = ncout.createVariable('wawa','f',('dim',))
    wawa.units = 'weather code'
    wawa[:] = data['wawa']
  
    zeff = ncout.createVariable('Z','f',('dim',))
    zeff.units = 'dB'
    zeff[:] = data['z']
  
    vis = ncout.createVariable('MOR_visibility','f',('dim',))
    vis.units = 'm'
    vis[:] = data['vis']
  
    interval = ncout.createVariable('sample_interval','f',('dim',))
    interval.units = 's'
    interval[:] = data['interval']
  
    ampli = ncout.createVariable('signal_amplitude','f',('dim',))
    ampli.units = ''
    ampli[:] = data['amp']
  
    n_part = ncout.createVariable('n_particles','f',('dim',))
    n_part.units = '#'
    n_part.description = 'number of detected particles'
    n_part[:] = data['nmb']
  
    temp_sens = ncout.createVariable('T_sensor','f',('dim',))
    temp_sens.units = 'deg C'
    temp_sens[:] = data['T_sensor']
    
    serial_no = ncout.createVariable('serial_no','S',('stri',))
    serial_no[:] = data['serial_no']
    
    version = ncout.createVariable('version','S',('stri',))
    version.description = 'IOP firmware version'
    version[:] = data['version']
    
    curr_heating = ncout.createVariable('curr_heating','f',('dim',))
    curr_heating.units = 'A'
    curr_heating.description = 'Current heating system'
    curr_heating[:] = data['curr_heating']
    
    volt_sensor = ncout.createVariable('volt_sensor','f',('dim',))
    volt_sensor.units = 'V'
    volt_sensor.description = 'Power supply voltage in the sensor'
    volt_sensor[:] = data['volt_sensor']
    
    status_sensor = ncout.createVariable('status_sensor','S',('stri',))
    status_sensor[:] = data['status_sensor']
    
    station_name = ncout.createVariable('station_name','S',('stri',))
    station_name[:] = data['station_name']    


    rain_am = ncout.createVariable('rain_am','f',('dim',))
    rain_am.units = 'mm'
    rain_am.description = 'rain amount absolute'
    rain_am[:] = data['r_amount']
    
    error_code = ncout.createVariable('error_code','S',('stri',))
    error_code[:] = data['error_code']    
    
    
    N = ncout.createVariable('N','f',('ndim','dim'))
    N.units = '1/m3'
    N.description = 'mean volume equivalent diameter per preci class'
    N[:,:] = data['n']
  
    v = ncout.createVariable('v','f',('ndim','dim'))
    v.units = 'm/s'
    v.description = 'mean falling speed per preci class'
    v[:,:] = data['v']
    
    
    #close .nc-file:
    ncout.close()

    return
##################################################################################################
##################################################################################################



def writeNC(logfile,ncname, site):
    #read .log-file into dictionnary:
    data = readASCII(logfile, site)
    
    #get number of lines in file ie length of data columns
    filelen = len(data['unixtime'])
    
    #open .nc outfile.
    ncout = Dataset(ncname,'w',format='NETCDF4') 
    
    # define dimensions:
    dim = ncout.createDimension('dim', filelen)       #filelen, set='none' if unlimited dimension
    ndim = ncout.createDimension('ndim',32)
    stri = ncout.createDimension('stri',None)
    
    #read variables:
    
    time = ncout.createVariable('time','i8',('dim',))      #time in double-precision...
    time.units = 'seconds since 1/1/1970 00:00:00'
    time[:] = data['unixtime']
 
    rain_rate = ncout.createVariable('rain_rate','f',('dim',))
    rain_rate.units = 'mm/h'
    rain_rate[:] = data['rr']


    rain_accum = ncout.createVariable('rain_accum','f',('dim',))
    rain_accum.units = 'mm'
    rain_accum[:] = data['r_accum']
  
    wawa = ncout.createVariable('wawa','f',('dim',))
    wawa.units = 'weather code'
    wawa[:] = data['wawa']
  
    zeff = ncout.createVariable('Z','f',('dim',))
    zeff.units = 'dB'
    zeff[:] = data['z']
  
    vis = ncout.createVariable('MOR_visibility','f',('dim',))
    vis.units = 'm'
    vis[:] = data['vis']
  
    interval = ncout.createVariable('sample_interval','f',('dim',))
    interval.units = 's'
    interval[:] = data['interval']
  
    ampli = ncout.createVariable('signal_amplitude','f',('dim',))
    ampli.units = ''
    ampli[:] = data['amp']
  
    n_part = ncout.createVariable('n_particles','f',('dim',))
    n_part.units = '#'
    n_part.description = 'number of detected particles'
    n_part[:] = data['nmb']
  
    temp_sens = ncout.createVariable('T_sensor','f',('dim',))
    temp_sens.units = 'deg C'
    temp_sens[:] = data['T_sensor']
    
    serial_no = ncout.createVariable('serial_no','S6',('stri',))
    serial_no[:] = data['serial_no']
    
    version = ncout.createVariable('version','S5',('stri',))
    version.description = 'IOP firmware version'
    version[:] = data['version']
    
    curr_heating = ncout.createVariable('curr_heating','f',('dim',))
    curr_heating.units = 'A'
    curr_heating.description = 'Current heating system'
    curr_heating[:] = data['curr_heating']
    
    volt_sensor = ncout.createVariable('volt_sensor','f',('dim',))
    volt_sensor.units = 'V'
    volt_sensor.description = 'Power supply voltage in the sensor'
    volt_sensor[:] = data['volt_sensor']
    
    status_sensor = ncout.createVariable('status_sensor','S2',('stri',))
    status_sensor[:] = data['status_sensor']
    
    station_name = ncout.createVariable('station_name','S5',('stri',))
    station_name[:] = data['station_name']    


    rain_am = ncout.createVariable('rain_am','f',('dim',))
    rain_am.units = 'mm'
    rain_am.description = 'rain amount absolute'
    rain_am[:] = data['r_amount']
    
    error_code = ncout.createVariable('error_code','S3',('stri',))
    error_code[:] = data['error_code']    
    
    
    N = ncout.createVariable('N','f',('ndim','dim'))
    N.units = '1/m3'
    N.description = 'mean volume equivalent diameter per preci class'
    N[:,:] = data['n']
  
    v = ncout.createVariable('v','f',('ndim','dim'))
    v.units = 'm/s'
    v.description = 'mean falling velocity per preci class'
    v[:,:] = data['v']
    
    M = ncout.createVariable('M','f',('ndim','ndim','dim'))
    M.units = ''
    M.description = 'raw data matrix. number of particles per volume diameter and fall velocity'
    M[:,:,:] = data['M']
    
    
    
    #close .nc-file:
    ncout.close()
    
    
    return
    
    
