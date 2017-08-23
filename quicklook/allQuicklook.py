# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 11:34:22 2017

@author: seas-oi
"""

from osgeo import gdal, ogr
import os, os.path, optparse,sys
import glob
import shutil

import quicklook as ql


def createAllQuickLook(DataPath,indexName):
    """Create all the quicklook images for the given index, in the given data base
    DataPath : Path to the data base
    indexName : index name whose we want to create the quicklook images 
    """
    
    listTile = glob.glob(DataPath + '/' + indexName+'/*')
    for tile in listTile:
        tileName = tile[-6:]
        images2remove = glob.glob(tile+'/*_QL.tif*')
        for img in images2remove:
            os.remove(img)
            
        images = glob.glob(tile+'/*.tif')
        for img in images:
            print '###################################  Create quick look image for : ' + img
            date = img[-12:-4]
            CLDmask = glob.glob(DataPath + '/rawData/' + tileName + '/' + date + '/*_Sen2corMask.tif')
            print 'IMAGE',img
            out = '/home/seas-oi/Documents/quick_look/DATA/QL/' + img[-24:-4] + '_QL.tif'
            print out
            ql.createColourImage(img,CLDmask[0],out)
    
    return 0
    
    
    
if __name__ == '__main__':
    #'/home/seas-oi/Documents/quick_look/DATA ','ndvi'
    
    if len(sys.argv) > 1:
        createAllQuickLook(sys.argv[1],sys.argv[2])
    else:
        print 'two arguments needed : DataPath and indexName'     