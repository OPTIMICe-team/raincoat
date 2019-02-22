#this is to produce the prototype of .netcdf-file for the SAMD database to check its compatibility.



import numpy as np


from parsivel_log_nc_convert_samdconform import writeNC,writeNC_old

import matplotlib.mlab
matplotlib.use('Agg')

import glob

import sys
import os

import datetime



logfile = '/data/hatpro/jue/data/parsivel/201812/parsivel_jue_20181202.log'
ncfile = '/home/schnitts/precipitation/testbed/sups_joy_dm00_l1_any_v00_20181202000000.nc'


writeNC(logfile,ncfile,'jue')
