# -*- coding: utf-8 -*-

import numpy as np
from scipy import stats

'''
this module estimates the offset of two distribution by the cumulative distribution test
'''


def histogram_intersection(h1, h2, bins):
    '''
    calculation of the intersection of two histograms
    
    ARGUMENTS;
        h1: first histogram
        h2: second histogram
        bins: bin edges of the histograms
    '''
    bins = np.diff(bins) #from http://blog.datadive.net/histogram-intersection-for-change-detection/
    sm = 0 #initialize the overlap by 0
    for i in range(len(bins)): #loop over all bins
        sm += min(bins[i]*h1[i], bins[i]*h2[i]) #this is the overlapping area at each bin
    return sm


def offset_calc_median(dist1,dist2,shiftrange):
    '''
    calculation of the offset by equalizing the median (shift of the dist1 distribution)
    
    ARGUMENTS:
        dist1: distribution which is shifted
        dist2: reference distribution
    RETURN:
        calculated offset
    '''
    
    #calculate the median of both distributions
    median_dist1 = np.nanmedian(dist1)
    median_dist2 = np.nanmedian(dist2)
    
    #calculate the offset
    offset = median_dist2-median_dist1
    #check if the calculated offset is in the possible shift range
    if offset>shiftrange:
        print "warning in statistical_analysys.methods: offset derived from median-method is bigger than shiftrange={0:.2f}".format(shiftrange)
    
    return offset

def offset_calc_overlap(dist1,dist2,binsize,range_val,shiftrange,shiftstep):
    '''
    calculation of the offset by maximizing the overlap of the distributions (shift of the dist1 distribution)
    
    ARGUMENTS:
        dist1: distribution which is shifted
        dist2: reference distribution
        binsize: number of bins of the histogram
        range_val: range of the considered reflectivities
    RETURN:
        calculated offset
    '''

    
    #calculate the histograms for the reference distribution
    histdist2,bin_edges = np.histogram(dist2, bins=binsize, range=range_val)
    
    #range of allowed shifts
    vshift = np.arange(-shiftrange,shiftrange,shiftstep)
    #initialize array with intersection values per shift
    overlap_area = np.zeros(vshift.size)
    
    #calculate possible shifts
    for i_shift,shift in enumerate(vshift):
        histdist1,bin_edges = np.histogram(dist1+shift, bins=binsize, range=range_val) #calculate the histogram of the shifted values
        overlap_area[i_shift] = histogram_intersection(histdist1, histdist2, bin_edges) #get the intersection values 
        
    #select the shift with the biggest overlap
    index_of_biggest_overlap = np.argmax(overlap_area)
    selshift = vshift[index_of_biggest_overlap]
        
    #Correction by means of values with the biggest overlap
    offset = selshift.mean() #this is only relevant if there are two shifts with equally high overlap
    

    #compare the selected overlap with the overlap at the boundaries (if that is equal we might hit the range boundaries of allowed shifts)
    if overlap_area[index_of_biggest_overlap]==overlap_area[0] or overlap_area[index_of_biggest_overlap]==overlap_area[-1]:
        print "warning in statistical_analysys.methods: offset derived from overlap-method is bigger (or equal) than the shiftrange={0:.2f}".format(shiftrange)

    return offset

def offset_calc_cumulative_dist(dist1,dist2,binsize,range_val,shiftrange,shiftstep,display_cdf):
    '''
    calculation of the offset by comparison of the cumulative distributions (using the Kolmogorov-Smirnov test routine from scipy) (shift of the dist1 distribution)
    
    ARGUMENTS:
        dist1: distribution which is shifted
        dist2: reference distribution
    RETURN:
        calculated offset
    '''
    
    #range of allowed shifts
    vshift = np.arange(-shiftrange,shiftrange,shiftstep)
    #initialize array with intersection values per shift
    stat_shift = np.zeros(vshift.size)
    pval_shift = np.zeros(vshift.size)
    
    #calculate possible shifts
    for i_shift,shift in enumerate(vshift):
        stat_shift[i_shift],pval_shift[i_shift] = stats.ks_2samp(dist1 + shift, dist2) #this is a scipy.stats function (see https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.stats.ks_2samp.html for reference)
    #select the shift with the highest p-value
    selshift = vshift[np.max(pval_shift)==pval_shift]
    #Correction by means of values with the  highest p-value
    offset = selshift.mean() #this is only relevant if there are two shifts with equally high overlap
    
    #compare the selected overlap with the overlap at the boundaries (if that is equal we might hit the range boundaries of allowed shifts)
    if abs(offset)>=shiftrange:
        print "warning in statistical_analysys.methods: offset derived from overlap-method is probably bigger (or equal) than the shiftrange={0:.2f}".format(shiftrange)
    
    if display_cdf: #display the raw, forward operated and shifted cdf to evaluate this method
        import matplotlib.pyplot as plt

        #calculate the histograms for the both distributions
        histdist1,bin_edges = np.histogram(dist1, bins=binsize, range=range_val)
        histdist1_shifted,bin_edges = np.histogram(dist1+offset, bins=binsize, range=range_val)
        histdist2,bin_edges = np.histogram(dist2, bins=binsize, range=range_val)
        #calculate the cdfs
        cdfdist1 = np.true_divide(np.cumsum(histdist1),np.cumsum(histdist1)[-1])
        cdfdist1_shifted = np.true_divide(np.cumsum(histdist1_shifted),np.cumsum(histdist1_shifted)[-1])
        cdfdist2 = np.true_divide(np.cumsum(histdist2),np.cumsum(histdist2)[-1])
        #plot finally
        plt.plot(cdfdist1,label="raw")
        plt.plot(cdfdist1_shifted,label="shifted")
        plt.plot(cdfdist2,label="fwd")
        plt.legend()#show the legend
        plt.show()
    
    return offset