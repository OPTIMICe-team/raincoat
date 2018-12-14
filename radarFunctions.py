import numpy as np
import xarray as xr


def getRadarVar(filePath, refTime, varName):

    """ This function reads the radar netCDF files and
        extract the desired variable.

        Arguments
        ---------

        filePath : Path to the netCDF file

        refTime : String specifying the starting time
           for example 1970-01-01 00:00:00

        varName : Name of the desired variable

        Returns
        -------

        dataArray : xarray DataArray
            The extracted DataArray

    """

    timeAtt = 'seconds since {refTime} UTC'.format(refTime=refTime)
    tempDS = xr.open_dataset(filePath)
    tempDS.time.attrs['units'] = timeAtt
    tempDS = xr.decode_cf(tempDS)
    tempDSZe = tempDS[varName]

    return tempDSZe


def getVarTimeRange(dataArray, rangeMin, rangeMax,
                    timeStrt, timeEnd):

    """ This function extracts the radar variable
        for a desired range and time interval.

        Arguments
        ---------

        dataArray : xarray DataArray of the variable

        rangeMin : minimum range

        rangeMax : maximum range

        timeStrt : starting time (pandas datetime)

        timeEnd : ending time (pandas datetime)

        Returns
        -------

        dataArray : xarray DataArray
            The select DataArray

    """

    dataArray = dataArray.sel(time=slice(timeStrt, timeEnd))
    dataArray = dataArray.sel(range=slice(rangeMin, rangeMax))

    return dataArray


def getFlatVar(dataArray):

    """This function flattens the variable and
       removes the nan and inf values.

       Argment
       -------

       dataArray : xarray DataArray of the variable

       Return
       ------

       dataFlat : numpy 1D array of the variable

    """

    dataFlat = dataArray.values.flatten()
    dataFlat = dataFlat[~ np.isnan(dataFlat)]
    dataFlat = dataFlat[~ np.isinf(dataFlat)]

    return dataFlat
