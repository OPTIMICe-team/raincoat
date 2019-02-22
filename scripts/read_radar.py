from raincoat.radarFunctions import getVarTimeRange, getRadarVar
import pandas as pd


data = getRadarVar('../samplefiles/radar/181202_000000_P09_ZEN_compact.nc',
	               '2001.01.01. 00:00:00',
	               'Ze')
start = pd.to_datetime('2018-12-02 00:00:00', format='%Y-%m-%d %H:%M:%S')
stop = pd.to_datetime('2018-12-02 01:00:00',format='%Y-%m-%d %H:%M:%S')
data = getVarTimeRange(data,1,2000, start, stop)

