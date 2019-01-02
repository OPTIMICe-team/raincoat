# -*- coding: utf-8 -*-
#%matplotlib inline

import numpy as np
            
#******************************************************************************
# Creation of Parsivel class boundaries (class center and class width) and bin edges for PSD calculation
#******************************************************************************

def pars_class():
	""" This function generates the volume equivalent diameter class center and widths
	
        Arguments
        ---------
        
        Returns
        -------
        pars_class	: 2dim array, volume equivalent diameter class center & width
        bin_edges	: valuese of volume equivalent diameter class edges
    """
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

	j = 0
	pars_class[0,0] = 0.062
	for i in range(1,32):
		if i < 10 or (i > 10 and i < 15) or (i > 15 and i < 20) or (i > 20 and i < 25) or (i > 25 and i < 30) or (i > 30):
		    pars_class[i,0] = pars_class[i-1,0] + pars_class[i,1]

		const = [0.188, 0.375, 0.75, 1.5, 2.5]
		if i == 10 or i == 15 or i == 20 or i == 25 or i == 30:
		    pars_class[i,0] = pars_class[i-1,0] + const[j]
		    j = j + 1

		#print pars_class[i,0]
		bin_edges[i+1,0] = pars_class[i,0] + pars_class[i,1]/2


	bin_edges[0,0] = 0.
	bin_edges[1,0] = pars_class[0,0] + pars_class[0,1]/2
	
	return pars_class, bin_edges
