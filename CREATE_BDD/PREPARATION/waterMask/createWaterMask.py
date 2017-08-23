# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 16:36:33 2017

@author: seas-oi
"""

import csv
from datetime import datetime, date, time, timedelta
from osgeo import gdal, ogr
import numpy as np
import os, os.path, optparse,sys
import glob
import shutil




def BDD_wtrMask(waterMask, tileList, dataPath):
    """
    Create BDD with water mask, in a raster format
    waterMask : path to the OSM shapefile with continent polygons
    tileList : list of tiles whose we want to create the BDD
    rawData : path to the downloaded sen2cor images and the sen2corMask_wgs84
    """    
    tiles = 'sentinel_2_index_shapefile.shp'    
    for t in tileList:
        Name = t[1:]
        interName = 'extracted_' + Name + '.shp'
        interName2 = 'extracted_' + Name + '2.shp'
        finalName = Name + '_WTRMask.tif'
        finalName2 = Name + '_WTRMask2.tif'
        #-- tile extraction        
        command1 = 'ogr2ogr -f "ESRI Shapefile" ' + interName + ' -where "name = ' + "'" + Name + "'" + '" ' +  tiles
        os.system(command1)
        #-- water mask clipping
        command2 = 'ogr2ogr -f "ESRI Shapefile" -clipsrc ' + interName + ' ' + interName2 + ' ' + waterMask
        os.system(command2)
        #-- vector to raster using cloudMask size
        CLDmaskP = glob.glob(dataPath + '/rawData/' + t + '/*')
        CLDmask = glob.glob(CLDmaskP[0] + '/*_Sen2corMask.tif')
        finalPath = dataPath + '/waterMask' + '/' + finalName
        finalPath2 = dataPath + '/waterMask' + '/' + finalName2
        shutil.copy2(CLDmask[0], finalPath2)
        
        #remove clouds from image
        command3 = 'otbcli_BandMath -il ' + finalPath2 + ' -out ' + finalPath + ' -exp "im1b1 > 0 ? 0 : 0"'        
        os.system(command3)        
        os.remove(finalPath2)        
        
        command4 = 'gdal_rasterize -a land -l ' + interName2[:-4] + ' ' + interName2 + ' ' + finalPath      
        os.system(command4)
        #-- remove unused shp
        extracted = glob.glob('./extracted*')
        for shp in extracted:
            os.remove(shp)
    return 0


if __name__ == '__main__':
    if len(sys.argv) > 1:    
        params = sys.argv[1]
    
        tiles = open(params, "r")
        for i in range(10):
            line = tiles.readline()
        tileList = line.split(",")
        tileList[-1] = tileList[-1][:-1]
        line = tiles.readline()
        waterMask = tiles.readline()
        BDD_wtrMask(waterMask, tileList, sys.argv[2])
        
    else:
        print 'No parameters file given' 
