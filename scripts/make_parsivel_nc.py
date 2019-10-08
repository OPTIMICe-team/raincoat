from raincoat.disdrometer.parsivel_log_nc_convert_samdconform import convertNC

#writeNC('../samplefiles/parsivel/parsivel_jue_20190209.log', '../samplefiles/parsivel/parsivel_jue_20190209.nc', 'jue')
#writeNC('../samplefiles/parsivel/parsivel_jue_20190210.log', '../samplefiles/parsivel/parsivel_jue_20190210.nc', 'jue')
#writeNC('../samplefiles/parsivel/parsivel_jue_20190211.log', '../samplefiles/parsivel/parsivel_jue_20190211.nc', 'jue')
#writeNC('../samplefiles/parsivel/parsivel_nya_20180904.log', '../samplefiles/parsivel/parsivel_nya_20180904.nc', 'nya')
#writeNC('../samplefiles/parsivel/parsivel_nya_20180905.log', '../samplefiles/parsivel/parsivel_nya_20180905.nc', 'nya')
#writeNC('../samplefiles/parsivel/parsivel_nya_20180906.log', '../samplefiles/parsivel/parsivel_nya_20180906.nc', 'nya')






convertNC('../samplefiles/parsivel/parsivel_jue_20190209.log', '../samplefiles/parsivel/parsivel_jue_20190209.nc')
convertNC('../samplefiles/parsivel/parsivel_jue_20190210.log', '../samplefiles/parsivel/parsivel_jue_20190210.nc')
convertNC('../samplefiles/parsivel/parsivel_jue_20190211.log', '../samplefiles/parsivel/parsivel_jue_20190211.nc')

convertNC('../samplefiles/parsivel/parsivel_nya_20180904.log', '../samplefiles/parsivel/parsivel_nya_20180904.nc',inifile = 'parsivel_globals_nya.ini')
convertNC('../samplefiles/parsivel/parsivel_nya_20180905.log', '../samplefiles/parsivel/parsivel_nya_20180905.nc',inifile = 'parsivel_globals_nya.ini')
convertNC('../samplefiles/parsivel/parsivel_nya_20180906.log', '../samplefiles/parsivel/parsivel_nya_20180906.nc',inifile = 'parsivel_globals_nya.ini')
