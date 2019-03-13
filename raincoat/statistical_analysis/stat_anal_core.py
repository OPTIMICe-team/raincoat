# -*- coding: utf-8 -*-

from methods import offset_calc_median,offset_calc_overlap,offset_calc_cumulative_dist

'''
this is the core of the statistical analysis and calls different methods which estimate the offset of the reflectivity distribution
'''

def calculate_offset(Ze_radar,Ze_fwd_oper,method='all',binsize = 50,range_val=[-20,30],shiftrange=20,shiftstep=0.1,display_cdf=False):
    '''
    calculates the offset of the radar using different statistical methods
    
    Arguments
    ---------
    Ze_radar: array of reflectivities from the radar
    Ze_fwd_oper: forward operated reflectivities from the distrometer
    method: method with which the offset is calculated ["median","overlap","cumulative_dist"]
    binsize: number of bins (used by overlap and cumulative_dist methods to set up the histogram)
    range_val: range of considered Ze-values (used by overlap and cumulative_dist methods to set up the histogram)
    shiftrange: possible range (positive or negative) by which the offset is searched ("median" method is not depending on this value)
    shifstep:  accuracy of the offset search("median" method is not depending on this value)
    display_cdf: display the raw, forward operated and shifted cdf to evaluate the cumulative_dist method
    Returns
    ---------
    dictionary containing the offsets obtained with the different statistical methods
    
    '''
    
    #initialize the dictionary which contains the offset values
    offset_dic = dict()
    if method in ("median","all"):
        offset_dic["offset_calc_median"] = offset_calc_median(Ze_radar,Ze_fwd_oper,shiftrange)
    if method in ("overlap","all"):
        offset_dic["offset_calc_overlap"] = offset_calc_overlap(Ze_radar,Ze_fwd_oper,binsize,range_val,shiftrange,shiftstep)
    if method in ("cumulative_dist","all"):
        offset_dic["offset_calc_cumulative_dist"] = offset_calc_cumulative_dist(Ze_radar,Ze_fwd_oper,binsize,range_val,shiftrange,shiftstep,display_cdf)
        
    return offset_dic
