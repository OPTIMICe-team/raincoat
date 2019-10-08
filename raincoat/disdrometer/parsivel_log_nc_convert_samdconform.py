
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
import configparser
import glob
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


def time2unix(datestring, stringformat):
    '''
    routine converts datestring into unix-time
    INPUT:
        - datestring: string of times, array, read from ascii
        - stringformat: format string of what's in the datestring, eg "%Y%m%d%H%M%S.%f"
    OUTPUT:
        - unixtime: vector of converted times, same dim as datestring
    '''
    
    try:
        f = datetime.datetime.strptime(datestring, stringformat[1:-1]) # why is it formatted like that? it is not in the manual, and why .%f which stands for microseconds?
        unix = calendar.timegm(f.timetuple())
    except ValueError:
        unix = np.nan
    return unix


def count_file_lines(fname, formatting):
    '''
    routine counts lines in .log-file.
    INPUT:
        - fname: filename including path to read from.
    OUTPUT:
        - total number of lines (int)
    '''
    
    if not 'fileencoding' in formatting.keys():
        f = io.open(fname, 'r')
    else:
        f = io.open(fname, 'r', encoding = formatting['fileencoding'])
    
    line_total = sum(1 for line in f)
    
    f.close()
    return line_total


def readASCII(logfile, variables, formatting):  
    '''
    file reads ascii-file into py-dictionnary.
    INPUT:
        - logfile: string of filename including complete path
        - variables: array of value numbers (in string format, see p.30 parsivel manual, '00' for timestamp), ordered in the order of appearance in your personal parsivel configuration
        - formatting: dictionnary containing separator; time format
    OUTPUT:
        - dictionnary with all read variables.
    '''
    dic = {}
    

    colnames = np.asarray([str(v) for v in variables])
    
    iline = 0
        
    #count number of lines with data in ascii-file:
    filelen = count_file_lines(logfile, formatting)
   
  
    #set keys where strings will be put in, to string arrays:
    for k,key in enumerate(colnames):   #following numbers refer to value numbers, p 30 manual.
        if key == '13' or key == '14' or key == '18' or key == '22' or key == '25':
            dic[key] = np.empty(filelen,dtype = 'S20')
        elif key == '90' or key == '91':
            dic[key] = np.zeros([32,filelen])
        elif key == '93':
            dic[key] = np.zeros([32,32,filelen])
        else:
            dic[key] = np.nan * np.ones(filelen)

    
    
    if not 'fileencoding' in formatting.keys():
        f = io.open(logfile,'r')
    else:
        f = io.open(logfile,'r', encoding=formatting['fileencoding'])

    for line in f.readlines():  # for each line split up string, put value into corresponding array if rowlen normal.         
        line = line.strip()
        cols = line.split(formatting['separator'][1])

        
        for i,cname in enumerate(colnames):         # loop through columns
            
            #check that timestamp is available: if not, discard the measurement line.
            try:
                datetime.datetime.strptime(cols[0], formatting['time'][1:-1])
            except: 
                print,'could not find a valid timestamp in first column. omitting line %i'%iline
                continue

            #### i think the following lines arent needed: here, the data is read anyways even if timestamp is missing.
            #if len(cols) == 1106:
                #tempcols = collections.deque(cols)
                #tempcols.extendleft([cols[0][0:18]])
                #tempcols[1] = tempcols[1][18:-1]
                #cols = list(tempcols)
            #elif len(cols) != 1107:
                #continue

            if cname == '00': #time
                dic[cname][iline] = time2unix(cols[i],formatting['time'])
            
            
            elif cname == '13' or cname == '14' or cname == '18' or cname == '22' or cname == '25':   #all columns containing strings
                
                dic[cname][iline] = str(cols[i])
             
            
            elif cname == '90': #nd array
                #calculate the starting column index of the array :
                #count which vars dont have multi-col entries
                starti = len(variables[(variables!= '90') & (variables!= '91') & (variables!= '93')])
                
                for aa in range(32):
                    try:
                        dic[cname][aa,iline] = float(cols[starti+aa])    #cols 18 upto 49 (32 values)
                        
                    except ValueError:
                        dic[cname][aa,iline] = np.nan
                        
                    if dic[cname][aa,iline] == -9.999 : dic[cname][aa,iline] = np.nan
                        
            elif cname == '91': #vd array
                #count cols with 1d-entry:
                starti = len(variables[(variables!= '90') & (variables!= '91') & (variables!= '93')])
                #if 90 as multi-col entry is before, add 32 to start index:
                if '90' in variables:
                    starti += 32
                
                
                for aa in range(32):
                    try:
                        dic[cname][aa,iline] = float(cols[starti+aa])   #cols 50 upto 81 (32 values)
                    except ValueError:
                        dic[cname][aa,iline] = np.nan
                        
                    if dic[cname][aa,iline] == -9.999 : dic[cname][aa,iline] = np.nan       
                    
            
            elif cname == '93': #M rawdata matrix
                #count cols with 1d-entry:
                starti = len(variables[(variables!= '90') & (variables!= '91') & (variables!= '93')])
                #if 90 as multi-col entry is before, add 32 to start index:
                if '90' and '91' in variables:  #if both are in: add 64
                    starti += 64
                elif '90' or '91' in variables: #if only one is in add 32
                    starti += 32
                
                    
                for bb in range(32):    #loop through falling velocities, ie rows in matrix
                    for aa in range(32):    #loop through sizes, ie columns
                        try:
                            dic[cname][aa,bb,iline] = float(cols[starti+32*aa+bb])
                        except ValueError:
                            dic[cname][aa,bb,iline] = np.nan
                        
                        
                        
            else:   #read all the other columns with generic float input. if theres something wrong, set them all to nan.
                
                #if len(cols) == 1107:    # RG 5.8.2016: if some different lenght, something wrong with this line (sth different than missing time stamp)
                try:
                    dic[cname][iline] = float(cols[i])
                   
                except:
                    dic[cname][iline] = np.nan
                

        #if iline == 0: 1/0        
        iline += 1
    f.close()
    
    
    
    return dic


################################################################################################
################################################################################################

def data_with_nans(data):
    '''
    this function is used to replace bad values with floating point nans. filters by status_sensor, z, and unixtime, and sets those values to np.nan
    INPUT:
        - data dictionnary containing variables read by read_ascii().
    OUTPUT:
        - data dictionnary with bad values replaced by nan
    '''
    data_corr = data
    
    #sort out wrong sensor status, replace by nan.
    for i in range(len(data['18'])):
        if data['07'][i] == -9.999:
            data_corr['07'][i] = np.nan
        try:
            data_corr['18'][i] = int(data['18'][i])
            data_corr['00'][i] = int(data['00'][i])
        except ValueError:
            data_corr['18'][i] = -9999
            data_corr['00'][i] = -9999
    
    
    
    
    return data_corr

##################################################################################################
##################################################################################################

def get_var_from_format(formatstring, separator):
    '''
    this routine reads from the given formatstring all the variables.
    INPUT:
        - formatstring as sent to parsivelk
        - separator used in the formatstring
    OUTPUT:
        - array of variables using the value numbers given in the manual.
    '''
    
    varis = formatstring[1:-1].split(str(separator[1]))
    variables = np.asarray([varis[i][-2:] for i in range(len(varis))])
    
    
    return variables


##################################################################################################
##################################################################################################


#add if-clauses here: if var in variables: then store variable, give units, etc here.
def writeNC(logfile,ncname, variables, globatts, globvars, formatting):
    '''
    routine writes variables into netcdf-file.
    INPUT:
        - logfile: string of complete ascii-filename including path
        - ncname: string of outputfilename including outputpath
        - globatts: dictionnary with global nc-file attributes. required keys (str format): institution, contact_person, source, author. source example string: 'OTT Parsivel 2.10.1: 70.210.001.3.0, serial number: xxxxx
        - globvars: dictionnary with global variables. required keys: latitude (float);  longitude (float); zasl (height of instrument above sea level [m]; serial number
    '''
    
    #check if globatts and globvars contain all necessary keys:
    if not ('institution'or 'contact_person'or 'source' or 'author') in globatts.keys():
        print, 'not all required keys are found in globatts. required keys (strings): institution, contact_person, source, author. source should contain serial_no (string; can also be read through %13); version (string; can be read through %14'
        return
    
    if not ('latitude' or 'latitude' or 'zasl') in globvars.keys():
        print, 'not all required keys are found in globvars. required keys (strings): latitude (float);  longitude (float); zasl (height of instrument above sea level [m]; )'
        return
    
    #namecatalog gives the name of the value numbers from telegram configuration string:
    namecatalog = {'00':'time', '01': 'rr','02':'precipitation_amount', '03':'wawa','04':'wawa_4677','05':'wawa_metar','06':'wawa_nws', '07':'Ze','08':'vis', '09':'sample_interval', '10':'signal_amplitude', '11':'n_particles' , '12':'T_sensor', '13':'serial_no', '14':'version','16':'I_heating', '17':'volt_sensor', '18':'status_sensor','19':'t_begin','20':'sensor_time','21':'sensor_date', '25': 'error_code', '30':'rain_intensity_16b', '31':'rain_intensity_12b','32':'precipitation_amount_abs', '33':'Ze_16b', '90':'nd', '91':'vd', '93':'M' }
    
    
    #get today's date:
    dtod = dt.datetime.today()
    #read .log-file into dictionnary:
    data_nc = readASCII(logfile, variables, formatting)      #data not quality filtered
    
    
    
    if ('00' and '18' and '07') in data_nc.keys():
        data = data_with_nans(data_nc)      # replace bad data with nans.
    else:
        print, 'could not replace bad values with nans.'
        data = data_nc
    #get number of lines in file ie length of data columns
    filelen = len(data['00'])
    
    #open .nc outfile.
    ncout = Dataset(ncname,'w',format='NETCDF4') 
    
    # define dimensions:
    time = ncout.createDimension('time', filelen)       #filelen, set='none' if unlimited dimension
    vclasses = ncout.createDimension('vclasses',32)          #sorting into velocity classes = bins
    dclasses = ncout.createDimension('dclasses',32)          #sorting into diameter classes = bins
    nstring = ncout.createDimension('nstring',3)
    
    #define global attributes:
    ncout.Title = "Parsivel disdrometer data"
    ncout.Institution = globatts['institution']
    ncout.Contact_person = globatts['contact_person']
    ncout.Source = globatts['source']
    ncout.History = 'Data processed with raincoat package.'
    ncout.Dependencies = 'external'
    ncout.Conventions = "CF-1.6 where applicable"
    ncout.Processing_date = dt.datetime.today().strftime('%Y-%m-%d,%H:%m:%S')
    ncout.Author = globatts['author']
    ncout.Comments = 'none'
    ncout.Licence = 'For non-commercial use only. This data is subject to the SAMD data policy to be found at www.icdc.cen.uni-hamburg.de/projekte/samd.html and in the SAMD Observation Data Product standard.'

    if '15' in variables:
        ncout.Version = 'Firmware DSP version number %s'%data['15'][0]
    
    #read variables:
    if '00' in variables:   #time
        time = ncout.createVariable('time','i',('time',))      #time in double-precision...
        time.units = 'seconds since 1970-01-01 00:00:00 UTC'
        time.long_name = 'time'
        time.fill_value = -9999
        time[:] = data['00']
    
    
    
    if '01' in variables:   #rain rate
        rr_si = data['01']#*0.001/3600.  #convert from mm/h in m/s
        rain_rate = ncout.createVariable(namecatalog['01'],'f',('time',))
        rain_rate.units = 'm h-1'
        rain_rate.long_name = 'rainfall_rate'
        rain_rate.fill_value = np.nan
        rain_rate[:] = rr_si

    if '02' in variables:   #accumulated precip amount
        rain_accum = ncout.createVariable(namecatalog['02'],'f',('time',))
        rain_accum.units = 'kg m-2'
        rain_accum[:] = data['02']-data['02'][0]
        rain_accum.long_name = 'precipitation amount'
        rain_accum.fill_value = np.nan
        rain_accum.comment = 'accumulated precipitation amount (32 bit) since start of day'
    
    if '03' in variables:   #wmo weather code 4680
        wawa = ncout.createVariable(namecatalog['03'],'f',('time',))
        wawa.long_name = 'weather code according to WMO SYNOP 4680'
        wawa.units = '-'
        wawa.fill_value = np.nan
        wawa.comment = 'WMO Code Table 4680: 00: No Precip., 51-53: Drizzle, 57-58: Drizzle and Rain, 61-63: Rain, 67-68: Rain and Snow, 71-73: Snow, 77: Snow Grains, 87-88: Graupel, 89: Hail; Increasing Intensity in one category indicated by increasing numbers'
        wawa[:] = data['03']
    
    if '04' in variables:   #wmo weather code 4677
        wawa = ncout.createVariable(namecatalog['04'],'f',('time',))
        wawa.long_name = 'weather code according to WMO SYNOP 4677'
        wawa.units = '-'
        wawa.fill_value = np.nan
        wawa.comment = 'WMO Code Table 4677'
        wawa[:] = data['04']
    
    if '05' in variables:   #wmo weather code 4678
        wawa = ncout.createVariable(namecatalog['05'],'f',('time',))
        wawa.long_name = 'weather code according to WMO METAR/SPECI'
        wawa.units = '-'
        wawa.fill_value = np.nan
        wawa.comment = 'WMO Code Table 4678'
        wawa[:] = data['05']
    
    if '06' in variables:   #wmo weather code NWS code
        wawa = ncout.createVariable(namecatalog['06'],'f',('time',))
        wawa.long_name = 'weather code according to NWS code'
        wawa.units = '-'
        wawa.fill_value = np.nan
        wawa[:] = data['06']
    
    
    if '07' in variables:   # radar reflectivity
        zeff = ncout.createVariable(namecatalog['07'],'f',('time',))
        zeff.fill_value = np.nan
        zeff.long_name = 'equivalent_reflectivity_factor (32 bit); identical to the 6th moment of the drop size distribution'
        zeff.units = 'dBZ'
        zeff[:] = data['07']
  
    if '08' in variables:   #MOR visibility in the precipitation
        vis = ncout.createVariable(namecatalog['08'],'f',('time',))
        vis.fill_value = np.nan
        vis.long_name = 'MOR visibility in the precipitation'
        vis.units = 'm'
        vis[:] = data['08']
    
    if '09' in variables:   #sample interval
        interval = ncout.createVariable(namecatalog['09'],'f',('time',))
        interval.long_name = 'time interval for each sample'
        interval.units = 's'
        interval[:] = data['09']
    
    if '10' in variables:      #signal signal_amplitude
        ampli = ncout.createVariable(namecatalog['10'],'f',('time',))
        ampli.units = ''
        ampli[:] = data['10']
    
    if '11' in variables:   #number of detected particles
        n_part = ncout.createVariable(namecatalog['11'],'f',('time',))
        n_part.fill_value = np.nan
        n_part.units = '-'
        n_part.long_name = 'number of detected particles'
        n_part[:] = data['11']
    
    if '12' in variables:   #T in sensor
        temp_sens = ncout.createVariable(namecatalog['12'],'f',('time',))
        temp_sens.fill_value = np.nan
        temp_sens.long_name = 'temperature in sensor'
        temp_sens.units = 'K'
        temp_sens[:] = data['12']+273.15

    #%13 and %14 are within global variables. %15 if specified.

    if '16' in variables:
        curr_heating = ncout.createVariable(namecatalog['16'],'f',('time',))
        curr_heating.fill_value = np.nan
        curr_heating.units = 'A'
        curr_heating.long_name = 'Current through the heating system'
        curr_heating[:] = data['16']
    
    if '17' in variables:
        volt_sensor = ncout.createVariable(namecatalog['17'],'f',('time',))
        volt_sensor.fill_value = np.nan
        volt_sensor.units = 'V'
        volt_sensor.long_name = 'Power supply voltage in the sensor'
        volt_sensor[:] = data['17']
    
    if '18' in variables:
        status_sensor = ncout.createVariable(namecatalog['18'],'i',('time',))
        status_sensor.fill_value = -9999
        status_sensor.units = '-'
        status_sensor.long_name = 'Sensor status'
        status_sensor.comments = '0: everything OK, 1: Laser protective glass is dirty, but measurements are still possible, 2: Laser protective glass is dirty, partially covered. No further usable measurements are possible.'
        status_sensor[:] = data['18']
    
    if '19' in variables:
        start_time = ncout.createVariable(namecatalog['19'], 'i',('time',))
        start_time.fill_value = -9999
        start_time.units = 'time'
        start_time.long_name = 'Date/time measurement begins'
        start_time[:] = data['19']
    
    if '20' in variables:
        sens_time = ncout.createVariable(namecatalog['20'], 'i',('time',))
        sens_time.fill_value = -9999
        sens_time.units = '-'
        sens_time.long_name = 'Sensor Time'
        sens_time[:] = data['20']
    
    if '21' in variables:
        sens_time = ncout.createVariable(namecatalog['21'], 'i',('time',))
        sens_time.fill_value = -9999
        sens_time.units = '-'
        sens_time.long_name = 'Sensor Date'
        sens_time[:] = data['21']
    
    #%%22 (station name) and %23 (station number) in global attributes (through institution key).
    
    
    if '25' in variables:
        error_code = ncout.createVariable(namecatalog['25'],'S1',('time','nstring'))
        error_code[:] = nc.stringtochar(np.asarray(data['25'],'S3'))    
    
    if '30' in variables:   #rain intensity 16bit
        rain_in = ncout.createVariable(namecatalog['30'],'f',('time',))
        rain_in.units = 'mm/h'
        rain_in.fill_value = np.nan
        rain_in.long_name = 'Rain intensity (16 bit)'
        rain_in[:] = data['30']
    
    
    if '31' in variables:   #rain intensity 12 bit
        rain_in = ncout.createVariable(namecatalog['31'],'f',('time',))
        rain_in.units = 'mm/h'
        rain_in.fill_value = np.nan
        rain_in.long_name = 'Rain intensity (12 bit)'
        rain_in[:] = data['31']
    
    
    if '32' in variables:   #absolute amount
        rain_am = ncout.createVariable(namecatalog['32'],'f',('time',))
        rain_am.units = 'mm'
        rain_am.fill_value = np.nan
        rain_am.long_name = 'absolute precipitation_amount since start of device'
        rain_am[:] = data['32']
    
    if '33' in variables:   # radar reflectivity
        zeff = ncout.createVariable(namecatalog['33'],'f',('time',))
        zeff.fill_value = np.nan
        zeff.long_name = 'equivalent_reflectivity_factor (16 bit); identical to the 6th moment of the drop size distribution'
        zeff.units = 'dBZ'
        zeff[:] = data['33']
    
    
    if '90' in variables:
        d = ncout.createVariable(namecatalog['90'],'f',('dclasses','time'))
        d.fill_value = np.nan
        d.units = 'log10(m-3 mm-1)'
        d.long_name = 'number of particles per diameter class'
        d[:,:] = data['90']
        
        #also store extra information about the classes:
        dclass =ncout.createVariable('dclasses','f',('dclasses'))
        dclass.units = 'mm'
        dclass.long_name = 'volume equivalent diameter class center'
        dclass[:] = np.asarray([0.062, 0.187, 0.312, 0.437, 0.562, 0.687, 0.812, 0.937, 1.062, 1.187, 1.375, 1.625, 1.875, 2.125, 2.375, 2.750, 3.250, 3.75, 4.25, 4.75, 5.5, 6.5, 7.5, 8.5, 9.5, 11., 13., 15., 17., 19., 21.5, 24.5])
    
        dclassw =ncout.createVariable('dwidth','f',('dclasses'))
        dclassw.units = 'mm'
        dclassw.long_name = 'volume equivalent diameter class width'
        dclassw[:] = np.asarray([0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.250, 0.250, 0.250, 0.250, 0.250, 0.5, 0.5, 0.5, 0.5, 0.5, 1., 1., 1., 1., 1., 2., 2., 2., 2., 2., 3., 3.])
        
        
    if '91' in variables:
        v = ncout.createVariable(namecatalog['91'],'f',('vclasses','time'))
        v.fill_value = np.nan
        v.units = 'm s-1'
        v.long_name = 'mean falling velocity per diameter class'
        v[:,:] = data['91']
        
        vclass =ncout.createVariable('vclasses','f',('vclasses'))
        vclass.units = 'm s-1'
        vclass.long_name = 'velocity class center'
        vclass[:] = np.asarray([0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 1.1, 1.3, 1.5, 1.7, 1.9, 2.2, 2.6, 3., 3.4, 3.8, 4.4, 5.2, 6., 6.8, 7.6, 8.8, 10.4, 12., 13.6, 15.2, 17.6, 20.8])
        
        
        vclassw =ncout.createVariable('vwidth','f',('vclasses'))
        vclassw.units = 'm s-1'
        vclassw.long_name = 'velocity class width'
        vclassw[:] = np.asarray([0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.2, 0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.8, 0.8, 0.8, 0.8, 0.8, 1.6, 1.6, 1.6, 1.6, 1.6, 3.2, 3.2])
        
    
    if '93' in variables:
        M = ncout.createVariable(namecatalog['93'],'f',('dclasses','vclasses','time'))
        M.fill_value = np.nan
        M.units = '-'
        M.long_name = 'number of particles per volume equivalent diameter class and fall velocity class'
        M[:,:,:] = data['93']
    
    #%94 to %98 not available as storage options.
    
    #additional global variables
    lat = ncout.createVariable('lat','f')
    lat.standard_name = 'latitude'
    lat.comments = 'Latitude of instrument location'
    lat.units = 'degrees_north'
    lat[:] = globvars['latitude']
    
    lon = ncout.createVariable('lon','f')
    lon.standard_name = 'longitude'
    lon.comments = 'Longitude of instrument location'
    lon.units = 'degrees_east'
    lon[:] = globvars['longitude']
    
    zsl = ncout.createVariable('zsl','f')
    zsl.standard_name = 'altitude'
    zsl.comments = 'Altitude of instrument above mean sea level'
    zsl.units = 'm'
    zsl[:] = globvars['zasl']
    
    
    #close .nc-file:
    ncout.close()
    
    
    return
    


def convertNC(logfile, ncfile, inifile = None):
    '''
    script to guide the conversion and call all the subfunctions
    INPUT:
        - logfile: logfilename incl path
        - ncfile: outputfilename incl path
        #- formatstring: format string sent to parsivel
        #- ncformatstring: format string used to save specified variables to netcdf. default: all variables stored in .log-file.
    '''
    print, 'converting %s........'%logfile
    #here: read the INIT-file for globatts, globvars
    config = configparser.RawConfigParser()
    
    #search for the ini-file within the raincoat directory:
    if inifile == None:
        try:
            inifile = glob.glob('./*/parsivel_globals.ini')[0]
        except:
            try:
                inifile = glob.glob('./parsivel_globals.ini')[0]
            except:
                print, 'could not find your ini-file in current or subdirectory.'
                return
    #inifile = './parsivel_globals.py'
    config.read(inifile)
    
    globatts = config['GLOBAL_ATTS']
    globvars = config['GLOBAL_VARS']
 
    variables = get_var_from_format(config['FORMATTING']['string'], config['FORMATTING']['separator'])
    
    formatting = {}
    for k in config['FORMATTING'].keys():
        formatting[k] = config['FORMATTING'][k]
    #formatting = {'separator':config['FORMATTING']['separator'], 'time':config['FORMATTING']['time'], 'fileencoding':config['FORMATTING']['fileencoding']}
    
    writeNC(logfile,ncfile, variables, globatts, globvars, formatting)
    
    return




