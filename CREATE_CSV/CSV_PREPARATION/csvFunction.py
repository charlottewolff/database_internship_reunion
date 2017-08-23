# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 12:41:56 2017

@author: seas-oi
"""

import csv
from datetime import datetime, date, time, timedelta
from osgeo import gdal, ogr
import numpy as np
import os, os.path, optparse,sys
import glob
import shutil
from rasterstats import zonal_stats


def removeMeanFile(indexName,DATA_path):
    """Remove the created mean files 
    indexName : name of the index where we want to remove the mean files
    DATA_path : path to the data folder    
    """
    print 'Finish \n Remove useless files'
    tileList = glob.glob(DATA_path +'/' +  indexName+'/*')
    for tile in tileList:
        meanList = glob.glob(tile + '/*_MEAN.tif')
        for file in meanList:
            os.remove(file)
    return 0
            
            
            
def find_indexName(chosenTile, pointSHP, maskCLD, maskWTR):
    """Get the indexName mean value in the tile
    chosenTile : path to the ndvi tile where we want the mean
    pointSHP : path to the shapefile with the area of the tile where we want the mean
    maskCLD : path to the cloud mask
    maskWTR : path to the water mask
    """
    meanindexName = chosenTile[:-4]+'_MEAN.tif'
    if glob.glob(meanindexName) == []: # -- not created yet 
        #cloud mask
        command1 = 'gdal_calc.py -A' + chosenTile + ' -B ' + maskCLD + ' --outfile=out1.tif --calc="A*(B == 0)+99*(B > 0)"'
        os.system(command1) 
        #water mask
        command2 = 'gdal_calc.py -A out1.tif -B ' + maskWTR + ' --outfile=out2.tif --calc="A*(B == 99)+99*(B < 1)"' 
        os.system(command2)
        #no data
        command3 = 'gdal_translate -a_nodata 99 out2.tif ' + meanindexName
        os.system(command3)
        #remove files
        os.remove('out1.tif')
        os.remove('out2.tif')
    stats = zonal_stats(pointSHP, meanindexName)
    indexName_value = stats[0]['mean']
    print '********* VALEUR',indexName_value
    return indexName_value
    
    
    

def getSites(dataSource):
    """Return points of a layer"""
    pointsLayer = dataSource.GetLayer()
    pointsLayer.SetAttributeFilter("id >= 0")
    return pointsLayer
    
    
    
    
def getCloudMask(date, Date, indexName, tileName):
    """Return path of corresponding cloud mask for date and tile
    date : path to the selected ndvi image whose we want the cloud mask
    Date : selected date
    indexName : name of the index (in params.txt)
    tileName : chosen tile name
    """
    mask = date.replace('/' + indexName + '/' + tileName,'/rawData/' + tileName + '/' + Date)
    mask = mask.replace('_' + indexName + '_' + Date +'.tif', '_' + Date + '_Sen2corMask.tif')
    return mask
    
    
def readParams(path):
    """Read the informations in the parameters file
    path : path to params.txt    
    """
    tiles = open(path, "r")
    #--- Starting date
    tiles.readline()
    index = tiles.readline()[:-1]
    
    #--- Starting date
    tiles.readline()
    B_date = tiles.readline()[:-1]
    
    #--- Stopping date
    tiles.readline()
    E_date = tiles.readline()[:-1]
    
    #--- DATA 
    tiles.readline()
    DATA_path = tiles.readline()[:-1]
    
    #--- Csv 
    tiles.readline()
    out = tiles.readline()[:-1]
    
    #--- Shapefile
    tiles.readline()
    shp = tiles.readline()[:-1]
    
    #--- Water mask
    water = DATA_path + '/waterMask'
    
    return index, B_date, E_date, DATA_path, out, shp, water
    
    
    
def buffer(infile,outfile,erosion,dilatation):
    """Create a buffer for each element of infile and create outfile"""
    ds_in=ogr.Open( infile )
    lyr_in=ds_in.GetLayer(0)
    drv=ds_in.GetDriver()
    ds_out = drv.CreateDataSource(outfile)
    layer = ds_out.CreateLayer( lyr_in.GetLayerDefn().GetName(),lyr_in.GetSpatialRef(), ogr.wkbPolygon)
    n_fields = lyr_in.GetLayerDefn().GetFieldCount()
    for i in xrange ( lyr_in.GetLayerDefn().GetFieldCount() ):
        field_in = lyr_in.GetLayerDefn().GetFieldDefn( i )
        fielddef = ogr.FieldDefn( field_in.GetName(), field_in.GetType() )   
        layer.CreateField ( fielddef )
        
    featuredefn = layer.GetLayerDefn()
        
    for feat in lyr_in:
        geom0 = feat.GetGeometryRef()
        feature0 = feat.Clone()
        feature0.SetGeometry(geom0.Buffer(float(erosion)))
        geom = feature0.GetGeometryRef()
        feature = feature0.Clone()                
        feature.SetGeometry(geom.Buffer(float(dilatation)))
        layer.CreateFeature(feature)
        del geom0
        del geom
    ds_out.Destroy()
    return 0
    
    
def createBDDpoints(DATA_path, shp):
    """create 1 shp/sites
    DATA_path : where the shp will be created
    shp : shapefile with all the points    
    """
    print '************** Points extraction **************'
    
    bufferShp = 'extractedPoints.shp' 
    #5km buffer
    buffer(shp,bufferShp,0.05,0)
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(bufferShp, 0)
    pointsLayer = getSites(dataSource)
    for feature in pointsLayer:
        Name = feature.GetField("code_site")
        interName = 'extracted_' + Name + '.shp'
        finalName = DATA_path + '/sites/extracted_' + Name + '.shp'
        #feature extraction        
        command1 = 'ogr2ogr -f "ESRI Shapefile" ' + finalName + ' -where "code_site = ' + "'" + Name + "'" + '" ' +  bufferShp
        os.system(command1)
        #remove unsued files
    extracted = glob.glob('./extracted*')
    for shp in extracted:
        os.remove(shp)
    return 0
    