# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 14:13:36 2017

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

import csvFunction as fct



def automatization(indexName,csvFile,DATA_path):
    with open(csvFile, 'r') as file:  
    #find number of lines
        nbLines = 0
        for row in file:
            nbLines += 1
    file.close()
    with open(csvFile, 'r') as file:  
    # Keep 2 last lines
        for i in range(nbLines-2):
            file.readline()
        linePrev2 = file.readline()[:-1].split(',')
        linePrev1 = file.readline()[:-1].split(',')
        # conversion linePrev in float
        for i in range(len(linePrev1)-1):
            linePrev1[i+1] = float(linePrev1[i+1])
            
    file.close()
    
    datePrev = datetime.strptime(str(linePrev1[0]), "%Y-%m-%d")
    dateWeek = datePrev + timedelta(days=7)
    lineWeek = list(linePrev1)
    lineWeek[0] = str(dateWeek)[0:10]  
 
    
    listPoints = glob.glob(DATA_path + '/sites/extracted*.shp')
    
    c = 0
    for point in listPoints:
        c += 1
        driver = ogr.GetDriverByName("ESRI Shapefile")
        dataSource = driver.Open(point, 0)
        pointLayer = fct.getSites(dataSource)            
        for feature in pointLayer:
            tile = feature.GetField("tuile")
            listDate = glob.glob(DATA_path + '/' + indexName + '/' + tile + "/*_" + indexName + "*.tif") 
            listDate.sort()
            print 'Computation previous date : ', linePrev1[0], ' --- SITE : ',feature.GetField("code_site"), ' ---'            
            for title in listDate:
                if '_MEAN' not in title:
                    Date = title[-12:-4]
                    convertDate = datetime.strptime(Date, "%Y%m%d")
                    if convertDate == datePrev:
                        #MONDAY
                        maskCLD = fct.getCloudMask(title, Date, indexName, tile)
                        maskWTR = water +  '/' + tile[1:] + '_WTRMask.tif'
                        indexName_value = fct.find_indexName(title, point, maskCLD, maskWTR)
                        # no clouds
                        if indexName_value != None:
                            linePrev1[c] = indexName_value
                        break
                    elif convertDate > datePrev and convertDate.isocalendar()[1] == datePrev.isocalendar()[1]:
                         # --- OTHER WEEK DAY
                        maskCLD = fct.getCloudMask(title, Date, indexName, tile)
                        maskWTR = water +  '/' + tile[1:] + '_WTRMask.tif'
                        index2 = fct.find_indexName(title, point, maskCLD, maskWTR) 
                        # no clouds 
                        if index2 != None:
                            nbDay = convertDate.weekday()
                            # Mean computation
                            indexName_value = (float(linePrev2[c])*nbDay + (7-nbDay)*index2)/7
                            linePrev1[c] = indexName_value
                            break
            print 'Computation new date : ', lineWeek[0], ' --- SITE : ',feature.GetField("code_site"), ' ---'            
            for title in listDate:
                if '_MEAN' not in title:
                    Date = title[-12:-4]
                    convertDate = datetime.strptime(Date, "%Y%m%d")
                    if convertDate == dateWeek:
                        #MONDAY
                        maskCLD = getCloudMask(title, Date, indexName, tile)
                        maskWTR = water +  '/' + tile[1:] + '_WTRMask.tif'
                        indexName_value = fct.find_indexName(title, point, maskCLD, maskWTR)
                        # no clouds
                        if indexName_value != None:
                            lineWeek[c] = indexName_value
                        break 
                    elif convertDate > dateWeek and convertDate.isocalendar()[1] == dateWeek.isocalendar()[1]:
                         # --- OTHER WEEK DAY
                        maskCLD = fct.getCloudMask(title, Date, indexName, tile)
                        maskWTR = water +  '/' + tile[1:] + '_WTRMask.tif'
                        index2 = fct.find_indexName(title, point, maskCLD, maskWTR) 
                        # no clouds 
                        if index2 != None:
                            nbDay = convertDate.weekday()
                            # Mean computation
                            indexName_value = (float(linePrev1[c])*nbDay + (7-nbDay)*index2)/7
                            lineWeek[c] = indexName_value
    
                        break
    #remove _MEAN files
    fct.removeMeanFile(indexName, DATA_path) 
    # Write lines in out file
    print 'Writting in', out
    out2 = out[:-4] + '2.csv' 
    with open(out, 'r') as fileR:
        with open(out2, 'w') as fileW:
            for i in range(nbLines-1):
                text = fileR.readline()
                fileW.write(str(text))
            fileW.write(str(linePrev1)[2:12] + str(linePrev1)[13:-1] + '\n')
            fileW.write(str(lineWeek)[2:12] + str(lineWeek)[13:-1] + '\n')
    fileR.close()
    fileW.close() 
    os.remove(out)
    os.rename(out2, out)
    print 'Following lines added : \n', str(linePrev1)[2:12] , str(linePrev1)[13:-1], '\n', str(lineWeek)[2:12] , str(lineWeek)[13:-1] , '\n'                                
    return 0
        



if __name__ == '__main__':
    if len(sys.argv) > 1:
        indexName, Bdate, Edate, DATA_path, out, shp, water = fct.readParams(sys.argv[1])
        automatization(indexName,out,DATA_path)