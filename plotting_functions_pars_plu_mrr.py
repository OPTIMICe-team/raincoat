# Script for plotting quicklooks for parsivel, pluvio and mmr: creates one plot for 
# rain rate and one for daily accumulated precipitation
# From previous script organized into functions by RG 21.8.2017

import glob
import os
import numpy as np
import time
import matplotlib.pyplot as plt

from netCDF4 import Dataset

def check_if_files(pars_path, plu_path, mrr_path, datestring, site):
  #for site in sites:
  #flags if .nc files for mrr, parsivel, pluvio exist. true: file exists, false: file does not exist
  pars_flag = True	
  plu_flag = True
  mrr_flag = True
  mrr_zip_flag = False
   
  pars_nc_file = glob.glob(pars_path+'/parsivel*'+datestring+'.nc')
  if pars_nc_file == []:
    pars_f = []
    pars_flag = False
  else:
    pars_f = Dataset(pars_nc_file[0])

  plu_nc_file = glob.glob(plu_path+'/pluvio*'+datestring+'.nc')
  if plu_nc_file == []:
    plu_f = []
    plu_flag = False
  else:
    plu_f = Dataset(plu_nc_file[0])

# for mrr files: unzip .nc.gz files
  if site == 'jue':
    mrr_nc_file =  glob.glob(mrr_path+'/'+datestring[2:13]+'*mrr*.nc.gz')
  elif site == 'nya':
    mrr_nc_file =  glob.glob(mrr_path+'/'+datestring+'*mrr_ave*.nc.gz')
  else:
    print 'give mrr file name structure in check_if_files-function'

  if mrr_nc_file == []:
    mrr_f = []
    mrr_flag = False
  else:
    os.system("gunzip "+mrr_nc_file[0])
    mrr_zip_flag = True

  if site == 'jue':
    unzipped = glob.glob(mrr_path+'/'+datestring[2:13]+'*mrr*.nc')
  elif site == 'nya':
    unzipped = glob.glob(mrr_path+'/'+datestring+'*mrr*.nc')
  else:
    print 'give mrr file name structure in check_if_files-function'

  if unzipped != []:
    mrr_flag = True
    mrr_f = Dataset(unzipped[0])
  else:
    mrr_f = []

  if mrr_zip_flag:  os.system("gzip -f "+unzipped[0])

  ncflags = [pars_flag,plu_flag,mrr_flag]
  ncdatasets = [pars_f,plu_f,mrr_f]

  return ncflags, ncdatasets


def read_parsivel(dataset):

  unixt = dataset.variables['time'][:]
  rr = dataset.variables['rain_rate'][:]
            
  #accum = dataset.variables['rain_accum'][:]
  try:
    stat = dataset.variables['status_sensor'][:]
    stat = stat.astype('int')
  except ValueError:
    stat = np.ones(len(unixt))
    for s,u in enumerate(unixt):
      try:
        stat[s] = dataset.variables['status_sensor'][s]
      except ValueError:
        stat[s] = -1.

  return unixt, rr, stat


def read_pluvio(dataset):

  unixt = dataset.variables['time'][:]
  #rr = np.array(dataset.variables['rain_rate'][:]) #measurement in mm/min->plot in mm/h
  #rr =  dataset.variables['r_accum_RT'][:]
  rr =  dataset.variables['r_accum_NRT'][:]
  rr[:] = [x * 60 for x in rr]
  #acc = dataset.variables['r_accum_RT'][:]
  acc = dataset.variables['r_accum_NRT'][:]
  #acc2 = dataset.variables['r_accum_NRT'][:]


  try:
    stat = dataset.variables['status'][:]
    stat = stat.astype('int')
  except ValueError:
    stat = np.ones(len(unixt))
    for s,u in enumerate(unixt):
      try:
        stat[s] = dataset.variables['status'][s]
      except ValueError:
        stat[s] = -1.

  return unixt, rr, acc, stat #, acc2


def read_mrr(dataset):

  unixt = dataset.variables['time'][:]
  rr = dataset.variables['MRR_RR'][:,2]   #take 3rd bin!
  gate_plotted = dataset.variables['MRR rangegate'][0,2]
  
  return unixt, rr, gate_plotted

def make_nans(rr, unixt):
# treat missing data (in rr NaN's, in unixt 0's)

  #replace -9999 in rr by nans:
  ind = np.where(rr == -9999.)
  if ind != []: rr[ind] = float(np.nan)
      

  # if there are missing values in unixt, it is read as an masked array 
  # (because it is not possible to have integer NaN's)
  # -> convert to normal numpy array with fill value 0
  if isinstance(unixt,np.ma.MaskedArray):
    unixt = unixt.filled([0])  

  #... or not. For some reason NaNs sometimes turn to large negative values, fixing that here  RG 25.9.2017  
  ind = np.where(unixt < 0.)
  if ind != []: unixt[ind] = 0


        
  return rr, unixt


def unix2decimaltime(unixt):
#calculate decimal time
      
  dc = np.zeros(len(unixt))

  for t,time_unix in enumerate(unixt):
    try:
      dc_struct = time.gmtime(unixt[t])
      dc[t] = dc_struct.tm_hour+float(dc_struct.tm_min)/60.+float(dc_struct.tm_sec)/3600.
    except ValueError:
      dc[t] = np.nan

    if dc[t] == 0.: dc[t]=np.nan
    if unixt[t] == 0.: dc[t]=np.nan # rows with missing time stamps filled with 0, because NaN is not possible for integer arrays
    
  return dc

def calc_accumulated_precip(rr, unixt) :

  accum = np.zeros([len(rr), 1])

  flags = np.where(np.isnan(rr))
  cp = rr.copy()
  cp[flags] = 0.
  timediff = 60./3600.  
          
  for n in range(1,len(rr)):

    if unixt[n] == 0:  # check for missing values
      accum[n] = accum[n-1]
    
    elif unixt[n-1] == 0:  # check for missing values  
      accum[n] = accum[n-1]+cp[n]*timediff # approximating time step from previous time step

    else :
     timediff = (unixt[n]-unixt[n-1])/3600.
     accum[n] = accum[n-1]+cp[n]*timediff

  accum[flags] = np.nan

  # maximum accumulated prec. -> value at the end of the day
  w = np.where(np.isnan(accum) == False)
        
  try:
    maxacc = max(accum[w])
  except ValueError:
    maxacc = np.nan


  return accum, maxacc

#def calc_accumulated_precip_pluvio(rr, acc, acc2) :
def calc_accumulated_precip_pluvio(rr, acc) :
  
  accum = np.zeros([len(rr), 1]) # pluvio logs two accumulated precipitation values

  if len(rr) < 1:
    maxacc = np.nan
  else:    
    acflag = np.where(np.isnan(acc)) 

    accp = acc.copy()
    accp[acflag] = 0.

    #accp2 = acc2.copy()
    #accp2[acflag] = 0.
    for n in range(1,len(acc)): 
      accum [n] = accum[n-1] + accp [n]
      #accum [n, 0] = accum[n-1, 0] + accp [n]
      #accum[n, 1] = accum[n-1, 1] + accp2[n]

    accum [acflag] = np.nan
    #accum [acflag,1] = np.nan


    # maximum accumulated prec. -> value at the end of the day
    maxacc = 0.
    #maxacc = np.nanmax(accum[:,0])  
    maxacc = np.nanmax(accum)  

  return accum, maxacc


def plot_rainrate(dc, rr, stat, i):

  plt.figure(1)
  sp = plt.subplot(3,1,i+1)
        
  sp.set_xlim(0,24)
  if i==1: plt.tick_params(axis='y', which='both', labelleft='off', labelright='on')
        
  rrp, = sp.plot(dc,rr,color = 'blue')
        

  if i == 0:
            
    if np.where(stat ==0) != []:sp.plot(dc[np.where(stat == 0)],np.ones(len(dc[np.where(stat == 0)]))*(-2),'x',markersize=0.7,color='green',label='good')
    if np.where(stat ==1) != []:sp.plot(dc[np.where(stat == 1)],np.ones(len(dc[np.where(stat == 1)]))*(-2),'x',markersize=0.7,color='orange',label='ok')
    if np.where(stat > 1) != []:sp.plot(dc[np.where(stat > 1)],np.ones(len(dc[np.where(stat > 1)]))*(-2),'x',markersize=0.7,color='red',label='bad')
            
    handles,titles = sp.axes.get_legend_handles_labels()
    sp.legend().get_title().set_fontsize('9')
    sp.legend(handles,titles,title='status',bbox_to_anchor=(1.025, 0.4), loc=2, borderaxespad=0.,fontsize=9,handlelength=0.3,labelspacing=0.1,frameon=False)
            
            
            
  if i == 1:
    sp2 = plt.subplot(3,1,i+1)
    if np.where(stat == 0) != []:sp.plot(dc[np.where(stat == 0)],np.ones(len(dc[np.where(stat == 0)]))*(-2),'x',markersize=0.7,color='green',label='good')
    if np.where(stat > 0) != []:sp.plot(dc[np.where(stat > 0)],np.ones(len(dc[np.where(stat > 0)]))*(-2),'x',markersize=0.7,color='red',label='bad')
            
    handles,titles = sp.axes.get_legend_handles_labels()
    sp.legend().get_title().set_fontsize('9')
    sp.legend(handles,titles,title='status',bbox_to_anchor=(1.03, 0.2), loc=2, borderaxespad=0.,fontsize=9,handlelength=0.3,labelspacing=0.1,frameon=False)
           

  marr = np.nanmax(rr)
  if marr < 5. or np.isnan(marr): 
    sp.set_ylim([-3,6.])
    tickpos = range(0,11,2)
        
  else: 
  
    maxval = int(round(marr+0.1*marr))
    tickdist = int(round(maxval/6))
    if tickdist == 1: tickdist = 2
    if tickdist == 3: tickdist = 2
    if tickdist == 4: tickdist = 5
    if tickdist == 6: tickdist = 5
    if tickdist == 7: tickdist = 5
    if tickdist == 8: tickdist = 10
    if tickdist == 9: tickdist = 10
    if tickdist > 10: tickdist = 10
    sp.set_ylim([-3,maxval])
    tickpos = range(0,maxval,tickdist)

  sp.axes.set_yticks(tickpos,minor=False)
  sp.axes.set_yticklabels(tickpos,fontdict=None,minor=False)        #print ma
        

  return sp
        

def plot_accumprecip(dc, accum, stat, i):
  plt.figure(2)
  sp2 = plt.subplot(3,1,i+1)
        
  sp2.set_xlim(0,24)
  if i==1: plt.tick_params(axis='y', which='both', labelleft='off', labelright='on')

  hand, = sp2.plot(dc,accum[:,0],color = 'blue')        
       
  #if i == 1: hand2, = sp2.plot(dc,accum[:,1], color='blue', linestyle='--')
        
        
  if i == 0:
    
    if np.where(stat ==0) != []:sp2.plot(dc[np.where(stat == 0)],np.ones(len(dc[np.where(stat == 0)]))*(-2),'x',markersize=0.7,color='green',label='good')
    if np.where(stat ==1) != []:sp2.plot(dc[np.where(stat == 1)],np.ones(len(dc[np.where(stat == 1)]))*(-2),'x',markersize=0.7,color='orange',label='ok')
    if np.where(stat > 1) != []:sp2.plot(dc[np.where(stat > 1)],np.ones(len(dc[np.where(stat > 1)]))*(-2),'x',markersize=0.7,color='red',label='bad')
            
    handles,titles = sp2.axes.get_legend_handles_labels()
    sp2.legend().get_title().set_fontsize('9')
    sp2.legend(handles,titles,title='status',bbox_to_anchor=(1.025, 0.4), loc=2, borderaxespad=0.,fontsize=9,handlelength=0.3,labelspacing=0.1,frameon=False)
            
            
  if i == 1:
    sp2 = plt.subplot(3,1,i+1)
    if np.where(stat == 0) != []: stathand1, = sp2.plot(dc[np.where(stat == 0)],np.ones(len(dc[np.where(stat == 0)]))*(-2),'x',markersize=0.7,color='green',label='good')
    if np.where(stat > 0) != []:  stathand2, = sp2.plot(dc[np.where(stat > 0)],np.ones(len(dc[np.where(stat > 0)]))*(-2),'x',markersize=0.7,color='red',label='bad')
            
            
    #l1 = sp2.legend([hand, hand2], ['Real Time', 'Non-Real Time'],loc=3, fontsize=9)
 
    handles,titles = sp2.axes.get_legend_handles_labels()
    sp2.legend().get_title().set_fontsize('9')
    sp2.legend([stathand1, stathand2], titles,title='status',bbox_to_anchor=(1.03, 0.2), loc=2, borderaxespad=0.,fontsize=9,handlelength=0.3,labelspacing=0.1,frameon=False)
            

  mi2,ma2 = sp2.get_ylim()
        
  macc = np.nanmax(accum)

  if macc < 5. or np.isnan(macc): 
    sp2.set_ylim([-3,6.])
    tickpos = range(0,11,2)
            
  else: 
    #sp2.set_ylim([-3,int(round(ma2+0.1*ma2))])
    #tickpos = range(0,int(round(ma2+0.1*ma2)),2)
    maxval = int(round(macc+0.1*macc))
    tickdist = int(round(maxval/6))
    if tickdist == 1: tickdist = 2
    if tickdist == 3: tickdist = 2
    if tickdist == 4: tickdist = 5
    if tickdist == 6: tickdist = 5
    if tickdist == 7: tickdist = 5
    if tickdist >  7: tickdist = 10
    sp2.set_ylim([-3,maxval])
    tickpos = range(0,maxval,tickdist)


  sp2.axes.set_yticks(tickpos,minor=False)
  sp2.axes.set_yticklabels(tickpos,fontdict=None,minor=False)


  return sp2


def subplot_nodata(i):

  plt.figure(1)
        
  sp = plt.subplot(3,1,i+1)
        
  sp.set_xlim(0,24)
        
  plt.setp(sp.get_yticklabels(),visible=False)
  sp.annotate('no data available',xy=(0.4,0.5),xycoords='axes fraction',fontsize = 10)

        
  plt.figure(2)
        
  sp2 = plt.subplot(3,1,i+1)
  sp2.set_xlim(0,24)
  plt.setp(sp2.get_yticklabels(),visible=False)
        
  sp2.annotate('no data available',xy=(0.4,0.5),xycoords='axes fraction',fontsize = 10)


  return sp, sp2



def make_plots_pretty(title_str1, title_str2, maxacc, mrrgateplot):

  #labels = ['Parsivel','Pluvio','MRR at 90 m height'] 
  labels = ['Parsivel','Pluvio', ''] 
  labels[2] = 'MRR at {} m height'.format(mrrgateplot)
  
  #rr plot:
  plt.figure(1)
  plt.subplot(3,1,1)
  plt.title(title_str1)
  
 
  #axis labelsing:  
  plt.subplot(312)
  plt.annotate('Precipitation Rate [mm/h]',xy=(0.05,0.65),xycoords='figure fraction',rotation=90)
  plt.subplot(3,1,3)
  plt.xlabel('UTC [h]')
  
  #switch off xticks in middle panels
  for n in range(2):
    sp = plt.subplot(3,1,n+1)
    plt.setp(sp.get_xticklabels(),visible=False)
  
    plt.subplots_adjust(hspace = .001)

  #add labels:
  for l in range(3):
    sp = plt.subplot(3,1,l+1)
    xloc = 0.9
    if l is 2: xloc = 0.70
    sp.annotate(labels[l],xy=(xloc,0.9),xycoords='axes fraction',fontsize=10)
  
  #accum plot:  
  plt.figure(2)
  plt.subplot(3,1,1)
  plt.title(title_str2)

  #axis labels:
  plt.subplot(312)
  x=plt.annotate('Accumulated Precipitation [mm]',xy=(0.05,0.7),xycoords='figure fraction',rotation=90)
  

  plt.subplot(3,1,3)
  plt.xlabel('UTC [h]')
 
  #switch off x-axislabeling for middle panels
  for n in range(2):
    sp = plt.subplot(3,1,n+1)
    plt.setp(sp.get_xticklabels(),visible=False)

  #add labels:
  for l in range(3):
    sp = plt.subplot(3,1,l+1)
    sp.annotate(labels[l],xy=(0.14,0.87-l*0.27),xycoords='figure fraction',fontsize=10)
    sp.annotate('total acc [mm]: '+str(maxacc[l])[0:5],xy=(0.72,0.9),xycoords='axes fraction',fontsize=10)     #annotate total daily accumulation!
 
  plt.subplots_adjust(hspace = .001)


def save_plots(rrfile, accumfile) :

  #start with time-rr-plot:
  plt.figure(1)
  
  #save plot:
  plt.savefig(rrfile,dpi=100)
  print 'written: '+rrfile
  plt.close(1)
 

  #time-accum plot: 
  plt.figure(2)
  
  #save plot:
  plt.savefig(accumfile,dpi=100)
  print 'written: '+accumfile
  plt.close(2)

  return


def make_dirs_jue(plotpath, datestring):

  #make directory where to sort in plot if not already existent:
  if not os.path.isdir(plotpath+datestring[0:4]):
    os.mkdir(plotpath+datestring[0:4])
  
  if not os.path.isdir(plotpath+datestring[0:4]+'/'+datestring[4:6]):
    os.mkdir(plotpath+datestring[0:4]+'/'+datestring[4:6])

  return

def link_nya_quicklooks(datestring, rrfile, accumfile):

  link_dir = '/home/hatpro/public_html/nya/parsivel/level1/' + datestring[0:4] + '/' + datestring[4:6] + '/'
  link_rr = link_dir + 'rr_pars_plu_mrr_'+datestring+'_nya.png'
  if not os.path.islink(link_rr):
    mkdir_p(os.path.dirname(link_rr), 2)
    print('linking: ln -s "%s" "%s"' % (rrfile, link_rr))
    os.symlink(rrfile, link_rr)

  link_accum = link_dir + 'accum_pars_plu_mrr_'+datestring+'_nya.png'
  if not os.path.islink(link_accum):
    print('linking: ln -s "%s" "%s"' % (accumfile, link_accum))
    os.symlink(accumfile, link_accum)


def mkdir_p(path, parents=-1):
  """make directories with parents
  Make all directories that are given after the `parents`th '/' counted from the end.
  e.g. mkdir_p('/tmp/1/2/3/4/',5) makes everything below `tmp`. It is the same as mkdir_p('/tmp/1/2/3/4',4)
  """
  if parents != int(parents) or parents < -1:
    raise ValueError('`parents` must be larger or equal to -1. given %s' % parents)
  d = '/'.join(path.split('/')[:-parents]) + '/'
  for directory in path.split('/')[-parents:]:
      d = d + directory + '/'
      if not os.path.isdir(d):
          os.mkdir(d) 

