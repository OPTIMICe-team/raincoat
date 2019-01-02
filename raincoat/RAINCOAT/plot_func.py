# -*- coding: utf-8 -*-
"""
Created on Tue Jan  1 13:28:38 2019

@author: sschoger

Functions to Plot Radar and Parsivel Data
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plotMRR(data, start, end, height, strDate, plotId,figTitle, plot):

    data=data[start:end]
    epoch = pd.datetime(1970, 1, 1)
    newTimes = np.array(data.index, np.float64)
    legend = np.arange(1,11) * (newTimes[-1] - newTimes[0])/10
    legend = legend+newTimes[0]
    legendDate = epoch + pd.to_timedelta(legend)
    date=legendDate[0].date().strftime('%Y.%m.%d')

    X,Y = np.meshgrid(newTimes, data.columns)
    dataToPlot = np.array(data[start:end])
    dataToPlot = np.ma.masked_invalid(dataToPlot)


    plt.figure(figsize=(15,6))
    plt.pcolormesh(X,Y,dataToPlot.T, cmap='jet')
    plt.ylim(height[0], height[1])
    plt.xticks(legend,legendDate.strftime('%H:%M:%S'), rotation=0)
    plt.ylabel('height [$m$]',fontsize=18)
    plt.title(figTitle+' '+strDate, fontsize=18)
    plt.colorbar().set_label('[dBZ]', fontsize=18)
    plt.grid()

    if plot == True: 
        out = plotId+'_'
        plt.savefig(out+figTitle+'.png', format='png', dpi=200,bbox_inches='tight')
        print out+figTitle+'.png'    
    
    return plt.show()



def calcPosition(val, xMin, xMax):
    decVal = (val - xMin)/(xMax - xMin)
    return decVal

def plot_W_Band(data, start, end, height, strDate, plotId, figTitle, plot):

    data=data[start:end]
    epoch = pd.datetime(2001, 1, 1, 0, 0, 0)
    newTimes = np.array(data.index, np.float64)
    legend = np.arange(1,11) * (newTimes[-1] - newTimes[0])/10
    legend = legend+newTimes[0]
    legendDate = epoch + pd.to_timedelta(legend)
    date=legendDate[0].date().strftime('%Y.%m.%d')

    X,Y = np.meshgrid(newTimes, data.columns)
    dataToPlot = np.array(data[start:end])
    dataToPlot = np.ma.masked_invalid(dataToPlot)

    plt.figure(figsize=(15,6))
    plt.pcolormesh(X,Y,dataToPlot.T,vmin=-15, vmax=30, cmap='jet')
    plt.ylim(height[0], height[1])
    plt.xticks(legend,legendDate.strftime('%H:%M:%S'), rotation=0)
    plt.ylabel('height [$m$]',fontsize=18)
    plt.title(figTitle+' '+strDate, fontsize=18)
    plt.colorbar().set_label('[dBZ]', fontsize=18)
    plt.grid()

    if plot == True: 
        out = plotId+'_'
        plt.savefig(out+figTitle+'.png', format='png', dpi=200,bbox_inches='tight')
        print out+figTitle+'.png'

    return plt.show()

def plotPARS(data, start, end, height, strDate, plotId,figTitle, plot): 
    # add after plot to run anywhere besides jupyter: ,start, end):

    data=data[start:end] #figure out how to implement different start and end times!! 
    epoch = pd.datetime(1970, 1, 1)
    newTimes = np.array(data.index, np.float64)
    legend = np.arange(1,11) * (newTimes[-1] - newTimes[0])/10
    legend = legend+newTimes[0]
    legendDate = epoch + pd.to_timedelta(legend)
    date=legendDate[0].date().strftime('%Y.%m.%d')

    plt.figure(figsize=(15,8))
    plt.plot(newTimes, data.Ze) #actually data[start:end]
    plt.ylabel('Ze [dBZ]', fontsize=18)
    plt.xticks(legend,legendDate.strftime('%H:%M:%S'), rotation=0)
    plt.xlim(newTimes[0], newTimes[-1])
    plt.title(figTitle+' '+strDate, fontsize=18)
    plt.legend()
    plt.grid()


    if plot == True: 
        out = plotId+'_'
        plt.savefig(out+figTitle+'.png', format='png', dpi=200,bbox_inches='tight')
        print out+figTitle+'.png'
    return plt.show()
    
def refl_check(data, start, end, height, strDate, figTitle,epoch):
    data=data[start:end]
    #epoch = pd.datetime(2001, 1, 1, 0, 0, 0)
    newTimes = np.array(data.index, np.float64)
    legend = np.arange(1,11) * (newTimes[-1] - newTimes[0])/10
    legend = legend+newTimes[0]
    legendDate = epoch + pd.to_timedelta(legend)
    date=legendDate[0].date().strftime('%Y.%m.%d')
     
    X,Y = np.meshgrid(newTimes, data.columns)
    dataToPlot = np.array(data[start:end])
    dataToPlot = np.ma.masked_invalid(dataToPlot)
     
    plt.pcolormesh(X,Y,dataToPlot.T,vmin=-10, vmax=30, cmap='jet')
    plt.ylim(height[0], height[1])
    plt.xticks(legend,legendDate.strftime('%H:%M'), rotation=0)
    plt.ylabel('height [$m$]',fontsize=18)
    plt.title(figTitle+' '+strDate, fontsize=18)
    plt.colorbar().set_label('[dBZ]', fontsize=18)
    return plt.grid()
