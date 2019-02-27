
from __future__ import print_function
import numpy as np

import datetime
import calendar

import matplotlib.mlab
matplotlib.use('Agg')

from netCDF4 import Dataset
import netCDF4 as nc
import datetime as dt
import io

import collections

'''
history:
- written by RG, 08/2017
- edited by SaS, 03/2018: now netcdf-files are SAMD conform according to http://icdc.cen.uni-hamburg.de/index.php?id=samd_data_standard&L=0
    - changed:
        - variable and dimension names
        - global attributes
'''

'''
This module is very specific to our institute configuration and works at the moment but cannot be published as it is.
Better to pass all the insititu specific arguments as function argument with default option.
It would be great to have a generic parser instead of one specific to our parsivel configuration, I can help on that. The script looks like it has been inherited by long time and we can take advantage of python progress to make it better
this script also put nan to legitimate data if some weird characters are detected, maybe we can recover them by passing error='ignore' to io.open for removing all non utf8 encoding
'''


def time2unix(datestring):
    try:
        f = datetime.datetime.strptime(datestring,"%Y%m%d%H%M%S.%f") # why is it formatted like that? it is not in the manual, and why .%f which stands for microseconds?
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
        #print('len(line)', len(line), rowlen, len(line) == rowlen, 'len(cols)', len(cols), len(cols) == 1107)

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

def data_with_nans(data):
    '''
    this function is used to replace bad values with floating point nans.
    '''
    data_corr = data
    #data.keys = 
    
    #sort out wrong sensor status, replace by nan.
    for i in range(len(data['status_sensor'])):
        if data['z'][i] == -9.999:
            data_corr['z'][i] = np.nan
        try:
            data_corr['status_sensor'][i] = int(data['status_sensor'][i])
            data_corr['unixtime'][i] = int(data['unixtime'][i])
        except ValueError:
            data_corr['status_sensor'][i] = -9999
            data_corr['unixtime'][i] = -9999
    
    
    
    
    return data_corr


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
    time = ncout.createDimension('time', filelen)       #filelen, set='none' if unlimited dimension
    classes = ncout.createDimension('classes',32)
    stri = ncout.createDimension('stri',None)
    
    
    #read variables:
    
    time = ncout.createVariable('time','i8',('time',))      #time in double-precision...
    time.units = 'seconds since 1/1/1970 00:00:00'
    time.fill_value = -9999
    time[:] = data['unixtime']
  
    rain_rate = ncout.createVariable('rain_rate','f',('time',))
    rain_rate.units = 'mm/h'
    rain_rate.fill_value = np.nan
    rain_rate[:] = data['rr']


    rain_accum = ncout.createVariable('rain_accum','f',('time',))
    rain_accum.units = 'mm'
    rain_accum.fill_value = np.nan
    rain_accum[:] = data['r_accum']
  
    wawa = ncout.createVariable('wawa','f',('time',))
    wawa.fill_value = np.nan
    wawa.units = 'weather code'
    wawa[:] = data['wawa']
  
    zeff = ncout.createVariable('Z','f',('time',))
    zeff.fill_value = np.nan
    zeff.units = 'dB'
    zeff[:] = data['z']
  
    vis = ncout.createVariable('MOR_visibility','f',('time',))
    vis.fill_value = np.nan
    vis.units = 'm'
    vis[:] = data['vis']
  
    interval = ncout.createVariable('sample_interval','f',('time',))
    interval.units = 's'
    interval[:] = data['interval']
  
    ampli = ncout.createVariable('signal_amplitude','f',('time',))
    ampli.units = ''
    ampli[:] = data['amp']
  
    n_part = ncout.createVariable('n_particles','f',('time',))
    n_part.units = '#'
    n_part.description = 'number of detected particles'
    n_part[:] = data['nmb']
  
    temp_sens = ncout.createVariable('T_sensor','f',('time',))
    temp_sens.units = 'deg C'
    temp_sens[:] = data['T_sensor']
    
    serial_no = ncout.createVariable('serial_no','S',('stri',))
    serial_no[:] = data['serial_no']
    
    version = ncout.createVariable('version','S',('stri',))
    version.description = 'IOP firmware version'
    version[:] = data['version']
    
    curr_heating = ncout.createVariable('curr_heating','f',('time',))
    curr_heating.units = 'A'
    curr_heating.description = 'Current heating system'
    curr_heating[:] = data['curr_heating']
    
    volt_sensor = ncout.createVariable('volt_sensor','f',('time',))
    volt_sensor.units = 'V'
    volt_sensor.description = 'Power supply voltage in the sensor'
    volt_sensor[:] = data['volt_sensor']
    
    status_sensor = ncout.createVariable('status_sensor','S',('stri',))
    status_sensor[:] = data['status_sensor']
    
    station_name = ncout.createVariable('station_name','S',('stri',))
    station_name[:] = data['station_name']    


    rain_am = ncout.createVariable('rain_am','f',('time',))
    rain_am.units = 'mm'
    rain_am.description = 'rain amount absolute'
    rain_am[:] = data['r_amount']
    
    error_code = ncout.createVariable('error_code','S',('stri',))
    error_code[:] = data['error_code']    
    
    
    N = ncout.createVariable('N','f',('classes','time'))
    N.units = '1/m3'
    N.description = 'mean volume equivalent diameter per preci class'
    N[:,:] = data['n']
  
    v = ncout.createVariable('v','f',('classes','time'))
    v.units = 'm/s'
    v.description = 'mean falling speed per preci class'
    v[:,:] = data['v']
    
    
    #close .nc-file:
    ncout.close()

    return
##################################################################################################
##################################################################################################



def writeNC(logfile,ncname, site):
    #get today's date:
    dtod = dt.datetime.today()
    #read .log-file into dictionnary:
    data_nc = readASCII(logfile, site)      #data not quality filtered
    
    data = data_with_nans(data_nc)      # replace bad data with nans.
    #get number of lines in file ie length of data columns
    filelen = len(data['unixtime'])
    
    #open .nc outfile.
    ncout = Dataset(ncname,'w',format='NETCDF4') 
    
    # define dimensions:
    time = ncout.createDimension('time', filelen)       #filelen, set='none' if unlimited dimension
    vclasses = ncout.createDimension('vclasses',32)          #sorting into velocity classes = bins
    dclasses = ncout.createDimension('dclasses',32)          #sorting into diameter classes = bins
    
    #define global attributes:
    ncout.Title = "Parsivel disdrometer data"
    ncout.Institution = 'University of Cologne (IGMK)'
    ncout.Contact_person = 'Bernhard Pospichal (joyce-cf@uni-koeln.de)'
    ncout.Source = 'OTT Parsivel 2.10.1: 70.210.001.3.0, serial number: %s'%(data['serial_no'][0])
    ncout.History = 'Data processed with parsivel_log_nc_convert_samdconform.py'
    ncout.Dependencies = 'external'
    ncout.Conventions = "CF-1.6 where applicable"
    ncout.Processing_date = dt.datetime.today().strftime('%Y-%m-%d,%H:%m:%S')
    ncout.Author = 'Sabrina Schnitt, s.schnitt@fz-juelich.de'
    ncout.Comments = 'none'
    ncout.Licence = 'For non-commercial use only. This data is subject to the SAMD data policy to be found at www.icdc.cen.uni-hamburg.de/projekte/samd.html and in the SAMD Observation Data Product standard.'
    #ncout.Measurement_site = 'JOYCE Juelich Observatory for Cloud Evolution'
    
    #read variables:
    
    time = ncout.createVariable('time','i',('time',))      #time in double-precision...
    time.units = 'seconds since 1970-01-01 00:00:00 UTC'
    time.long_name = 'time'
    time.fill_value = -9999
    time[:] = data['unixtime']
    
    rr_si = data['rr']*0.001/3600.  #convert from mm/h in m/s
 
    rain_rate = ncout.createVariable('rr','f',('time',))
    rain_rate.units = 'm s-1'
    rain_rate.long_name = 'rainfall_rate'
    rain_rate.fill_value = np.nan
    rain_rate[:] = rr_si


    rain_accum = ncout.createVariable('precipitation_amount','f',('time',))
    rain_accum.units = 'kg m-2'
    rain_accum[:] = data['r_accum']-data['r_accum'][0]
    rain_accum.long_name = 'precipitation amount'
    rain_accum.fill_value = np.nan
    rain_accum.comment = 'accumulated precipitation amount (32 bit) since start of day'
  
    wawa = ncout.createVariable('wawa','f',('time',))
    wawa.long_name = 'weather code according to WMO SYNOP 4680'
    wawa.units = '1'
    wawa.fill_value = np.nan
    wawa.comment = 'WMO Code Table 4680: 00: No Precip., 51-53: Drizzle, 57-58: Drizzle and Rain, 61-63: Rain, 67-68: Rain and Snow, 71-73: Snow, 77: Snow Grains, 87-88: Graupel, 89: Hail; Increasing Intensity in one category indicated by increasing numbers'
    #wawa.missing_value = np.Nan
    wawa[:] = data['wawa']
  
    zeff = ncout.createVariable('Ze','f',('time',))
    zeff.fill_value = np.nan
    zeff.long_name = 'equivalent_reflectivity_factor; identical to the 6th moment of the drop size distribution'
    zeff.units = 'dBZ'
    zeff[:] = data['z']
  
    vis = ncout.createVariable('vis','f',('time',))
    vis.fill_value = np.nan
    vis.long_name = 'visibility_in_air'
    vis.units = 'm'
    vis[:] = data['vis']
    
    '''
    interval = ncout.createVariable('sample_interval','f',('time',))
    interval.long_name = 'time interval for each sample'
    interval.units = 's'
    interval[:] = data['interval']
    '''
    '''
    ampli = ncout.createVariable('signal_amplitude','f',('time',))
    ampli.units = ''
    ampli[:] = data['amp']
    '''
    
    n_part = ncout.createVariable('n_particles','f',('time',))
    n_part.fill_value = np.nan
    n_part.units = '1'
    n_part.long_name = 'number of detected particles'
    n_part[:] = data['nmb']
    
    '''
    temp_sens = ncout.createVariable('T_sensor','f',('time',))
    temp_sens.fill_value = np.nan
    temp_sens.long_name = 'temperature_of_sensor'
    temp_sens.units = 'K'
    temp_sens[:] = data['T_sensor']+273.15
    '''
    
    '''
    serial_no = ncout.createVariable('serial_no','S6',('stri',))
    serial_no[:] = data['serial_no']
    '''
    '''
    version = ncout.createVariable('version','S5',('stri',))
    version.description = 'IOP firmware version'
    version[:] = data['version']
    '''
    '''
    curr_heating = ncout.createVariable('I_heating','f',('time',))
    curr_heating.fill_value = np.nan
    curr_heating.units = 'A'
    curr_heating.long_name = 'Current of heating system'
    curr_heating[:] = data['curr_heating']
    
    volt_sensor = ncout.createVariable('volt_sensor','f',('time',))
    volt_sensor.fill_value = np.nan
    volt_sensor.units = 'V'
    volt_sensor.long_name = 'Power supply voltage of the sensor'
    volt_sensor[:] = data['volt_sensor']
    '''
    
    status_sensor = ncout.createVariable('status_sensor','i',('time',))
    status_sensor.fill_value = -9999
    status_sensor.units = '1'
    status_sensor.long_name = 'Status of the Sensor'
    status_sensor.comments = '0: everything OK, 1: Laser protective glass is dirty, but measurements are still possible, 2: Laser protective glass is dirty, partially covered. No further usable measurements are possible.'
    status_sensor[:] = data['status_sensor']
    
    
    '''
    station_name = ncout.createVariable('station_name','S5',('stri',))
    station_name[:] = data['station_name']    
    '''
    '''
    rain_am = ncout.createVariable('precipitation_amount2','f',('time',))
    rain_am.units = 'mm'
    rain_am.fill_value = np.nan
    rain_am.long_name = 'absolute precipitation_amount'
    rain_am[:] = data['r_amount']
    '''
    
    '''
    error_code = ncout.createVariable('error_code','S3',('stri',))
    error_code[:] = data['error_code']    
    '''
    
    d = ncout.createVariable('dmean','f',('dclasses','time'))
    d.fill_value = np.nan
    d.units = 'log10(m-3 mm-1)'
    #d.long_name = 'mean volume equivalent diameter per class'
    d.long_name = 'number of particles per diameter class'
    d[:,:] = data['n']
    
    v = ncout.createVariable('vmean','f',('vclasses','time'))
    v.fill_value = np.nan
    v.units = 'm s-1'
    v.long_name = 'mean falling velocity per diameter class'
    v[:,:] = data['v']
    
    vclass =ncout.createVariable('vclasses','f',('vclasses'))
    vclass.units = 'm s-1'
    vclass.long_name = 'velocity class center'
    vclass[:] = np.asarray([0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 1.1, 1.3, 1.5, 1.7, 1.9, 2.2, 2.6, 3., 3.4, 3.8, 4.4, 5.2, 6., 6.8, 7.6, 8.8, 10.4, 12., 13.6, 15.2, 17.6, 20.8])
    
    
    vclassw =ncout.createVariable('vwidth','f',('vclasses'))
    vclassw.units = 'm s-1'
    vclassw.long_name = 'velocity class width'
    vclassw[:] = np.asarray([0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.2, 0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.8, 0.8, 0.8, 0.8, 0.8, 1.6, 1.6, 1.6, 1.6, 1.6, 3.2, 3.2])
    
    dclass =ncout.createVariable('dclasses','f',('dclasses'))
    dclass.units = 'mm'
    dclass.long_name = 'volume equivalent diameter class center'
    dclass[:] = np.asarray([0.062, 0.187, 0.312, 0.437, 0.562, 0.687, 0.812, 0.937, 1.062, 1.187, 1.375, 1.625, 1.875, 2.125, 2.375, 2.750, 3.250, 3.75, 4.25, 4.75, 5.5, 6.5, 7.5, 8.5, 9.5, 11., 13., 15., 17., 19., 21.5, 24.5])
    
    dclassw =ncout.createVariable('dwidth','f',('dclasses'))
    dclassw.units = 'mm'
    dclassw.long_name = 'volume equivalent diameter class width'
    dclassw[:] = np.asarray([0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.250, 0.250, 0.250, 0.250, 0.250, 0.5, 0.5, 0.5, 0.5, 0.5, 1., 1., 1., 1., 1., 2., 2., 2., 2., 2., 3., 3.])
    
    
    M = ncout.createVariable('M','f',('dclasses','vclasses','time'))
    M.fill_value = np.nan
    M.units = '1'
    M.long_name = 'number of particles per volume equivalent diameter class and fall velocity class'
    M[:,:,:] = data['M']
    
    #additional needed variables (by hdcp standards)
    lat = ncout.createVariable('lat','f')
    lat.standard_name = 'latitude'
    lat.comments = 'Latitude of instrument location'
    lat.units = 'degrees_north'
    lat[:] = 50.908547
    
    lon = ncout.createVariable('lon','f')
    lon.standard_name = 'longitude'
    lon.comments = 'Longitude of instrument location'
    lon.units = 'degrees_east'
    lon[:] = 6.413536
    
    zsl = ncout.createVariable('zsl','f')
    zsl.standard_name = 'altitude'
    zsl.comments = 'Altitude of instrument above mean sea level'
    zsl.units = 'm'
    zsl[:] = 111.
    
    
    #close .nc-file:
    ncout.close()
    
    
    return
    
    
