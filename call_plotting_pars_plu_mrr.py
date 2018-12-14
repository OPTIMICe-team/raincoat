# Script for plotting quicklooks for parsivel, pluvio and mmr: creates one plot for 
# rain rate and one for daily accumulated precipitation
# From previous script organized into functions by RG 21.8.2017

import sys
import datetime

import matplotlib.mlab
matplotlib.use('Agg')

from plotting_functions_pars_plu_mrr import *

sites = sys.argv[1:]
matplotlib.style.use('classic')

days_range = {
  'jue': (1, 20),
  'nya': (0, 5),
  }

for site in sites:
  for dd in range(days_range[site][0], days_range[site][1]):

    datestring = (datetime.datetime.now() - datetime.timedelta(days=dd)).strftime("%Y%m%d") 

    print 'plotting:', datestring

    plu_path = {
      'jue':'/data/hatpro/jue/data/pluvio/netcdf/'+datestring[2:6],
      'nya':'/data/obs/site/nya/pluvio/l1/' + datestring[0:4] + '/'+ datestring[4:6] + '/' + datestring[6:8] + '/',
    }

    pars_path = {
      'jue':'/data/hatpro/jue/data/parsivel/netcdf/'+datestring[2:6],
      'nya':'/data/obs/site/nya/parsivel/l1/' + datestring[0:4] + '/'+ datestring[4:6] + '/' + datestring[6:8] + '/',
    }

    mrr_path = {
      'jue':'/data/hatpro/jue/data/mrr/mrr_ave-6-0-0-6_nc/'+datestring[2:6],
      'nya':'/data/obs/site/nya/mrr/l1/' + datestring[0:4] + '/'+ datestring[4:6] + '/' + datestring[6:8] ,
    }

    rr_title = {
      'jue':'Precipitation Rate Juelich, '  + datestring[6:8] +'.'+datestring[4:6] +'.'+datestring[0:4],
      'nya':'Precipitation Rate Ny-Alesund, '  + datestring[6:8] +'.'+datestring[4:6] +'.'+datestring[0:4],
    }

    acc_title = {
      'jue': 'Accumulated Precipitation Juelich, ' + datestring[6:8] +'.'+datestring[4:6] +'.'+datestring[0:4],
      'nya':'Accumulated Precipitation Ny-Alesund, ' + datestring[6:8] +'.'+datestring[4:6] +'.'+datestring[0:4],
    }
 
    plotpath = {
      'jue':'/home/hatpro/public_html/jue/parsivel_pluvio/',
      'nya':pars_path['nya'],
    }

    rrfile = {
      'jue':plotpath['jue']+datestring[0:4]+'/'+datestring[4:6]+'/'+'rr_pars_plu_mrr_'+datestring+'.png',
      'nya':plotpath['nya']+'rr_pars_plu_mrr_'+datestring+'_nya.png',
    }

    accumfile = {
      'jue':plotpath['jue']+datestring[0:4]+'/'+datestring[4:6]+'/'+'accum_pars_plu_mrr_'+datestring+'.png',
      'nya':plotpath['nya']+'accum_pars_plu_mrr_'+datestring+'_nya.png',
    }


    ncflags, ncdatasets = check_if_files(pars_path[site], plu_path[site], mrr_path[site], datestring, site)

    maxacc = np.zeros(3)
    mrrgtplot = 0.
    for i,ncf in enumerate(ncflags):
      if ncf:
       
        if i==0: #parsivel
          unixt, rr, stat = read_parsivel(ncdatasets[i])
            
        if i==1:#pluvio
          #unixt, rr, acc, acc2, stat = read_pluvio(ncdatasets[i])
          unixt, rr, acc,stat = read_pluvio(ncdatasets[i])
            
        if i==2: #mrr
          unixt, rr, mrrgtplot = read_mrr(ncdatasets[i])  

        # treat missing data (in rr NaN's, in unixt 0's)
        rr, unixt = make_nans(rr, unixt)

        # calculate decimal time
        dc = unix2decimaltime(unixt)   
        
        # calculate accumulation:
        if i == 1: # pluvio
            #accum, maxacc[i] = calc_accumulated_precip_pluvio(rr, acc, acc2)
            accum, maxacc[i] = calc_accumulated_precip_pluvio(rr, acc)

        else:
            accum, maxacc[i] = calc_accumulated_precip(rr, unixt)

        # rain rate plot
        sp = plot_rainrate(dc, rr, stat, i)

        sp2 = plot_accumprecip(dc, accum, stat, i)

      else:   #if flag false. (no data)
        sp, sp2 = subplot_nodata(i)
        stat = 0.

        if len(rr) < 1: continue


    # make global plot cosmetics:
    make_plots_pretty(rr_title[site], acc_title[site], maxacc, mrrgtplot)

    if site == 'jue':
      # make directory where to sort in plot if not already existent:
      make_dirs_jue(plotpath['jue'], datestring)

    # save plots
    save_plots(rrfile[site], accumfile[site])

    if site == 'nya':
      #link files to quicklook browser
      link_nya_quicklooks(datestring, rrfile[site], accumfile[site])

