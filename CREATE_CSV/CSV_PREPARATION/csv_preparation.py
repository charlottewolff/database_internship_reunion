# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 11:19:16 2017

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






def createCSV(indexName, DATA_path, out, Bdate,Edate, pointsFile, water):

    ### dates parameters ###
    B_date = datetime.strptime(Bdate, "%Y%m%d")    
    E_date = datetime.strptime(Edate, "%Y%m%d")
    W_date = B_date
    delta = timedelta(days=7)
    
    ### Check if beginn with monday    
    if B_date.weekday() != 0:
        print 'Beginning date not a Monday, can\'t process the computation'
    
    else:
        print 'Writting csv file for ', indexName, ' from ', Bdate, ' to ',Edate
        ###
        
        ### points shp file and create BDD###
        fct.createBDDpoints(DATA_path, pointsFile)

        ### write first line of the csv file with points name        
        listPoints = glob.glob(DATA_path + '/sites/extracted*.shp')
        previousWeek = ['date']
        for point in listPoints:
            driver = ogr.GetDriverByName("ESRI Shapefile")
            dataSource = driver.Open(point, 0)
            pointLayer = fct.getSites(dataSource)
            for feature in pointLayer:
                tile = feature.GetField("code_site")
                previousWeek.append(tile)
        
        ### write in csv file
        findexName = open(out, 'w')
        findexName.write(str(previousWeek)[1:-1] + '\n')
        ###        
       
        # --- First date         
        previousWeek[0] = str(W_date)[0:10]
        c = 1
        print '###  WEEK : ',str(W_date), ' ###'

        for point in listPoints: 
            driver = ogr.GetDriverByName("ESRI Shapefile")
            dataSource = driver.Open(point, 0)
            pointLayer = fct.getSites(dataSource)
            
            for feature in pointLayer:
                tile = feature.GetField("tuile")
                listDate = glob.glob(DATA_path + '/' + indexName + '/' + tile + "/*_" + indexName + "*.tif") 
                ### ordered by dates
                listDate.sort()
                for title in listDate:
                    if '_MEAN' not in title:
                        Date = title[-12:-4]
                        convertDate = datetime.strptime(Date, "%Y%m%d")
                        if convertDate.isocalendar()[1] == W_date.isocalendar()[1] or convertDate.isocalendar()[1]+1 == W_date.isocalendar()[1]:                    
                            maskCLD = fct.getCloudMask(title, Date, indexName,tile)
                            print 'Le masque de nuage est : ', maskCLD
                            maskWTR = water +  '/' + tile[1:] + '_WTRMask.tif'
                            indexName_value = fct.find_indexName(title, point, maskCLD, maskWTR)
                            print '---  SITE : ', feature.GetField("code_site"), '  --- DATE : ', str(convertDate), ' --- VALUE : ', indexName_value, ' ---'                            
                            previousWeek[c] = indexName_value
                            break
            c += 1
                
        findexName.write(str(previousWeek)[2:12] + str(previousWeek)[13:-1] + '\n')        
        week = list(previousWeek)        
        W_date += delta
                  
        
        # --- Other dates 
        while W_date < E_date:
            print '###  WEEK : ',str(W_date), ' ###'
            c = 1
            week[0] = str(W_date)[0:10]
            for point in listPoints:
                dataSource = driver.Open(point, 0)
                pointsLayer = fct.getSites(dataSource)
                for feature in pointsLayer:
                    tile = feature.GetField("tuile")
                    listDate = glob.glob(DATA_path + '/' + indexName + '/' + tile + "/*_" + indexName + "*.tif")
                    ### ordered by dates                     
                    listDate.sort()
                    for title in listDate:
                        if '_MEAN' not in title:
                            Date = title[-12:-4]
                            convertDate = datetime.strptime(Date, "%Y%m%d")
                            if convertDate == W_date:
                                # --- MONDAY
                                maskCLD = fct.getCloudMask(title, Date, indexName, tile)
                                print 'Le masque de nuage est : ', maskCLD
                                maskWTR = water +  '/' + tile[1:] + '_WTRMask.tif'
                                indexName_value = fct.find_indexName(title, point, maskCLD, maskWTR)
                                # if point not covered by clouds                                
                                if indexName_value != None:                                    
                                    print '---  SITE : ', feature.GetField("code_site"), '  --- DATE : ', str(convertDate), ' (MONDAY) --- VALUE : ', indexName_value, ' ---'
                                    week[c] = indexName_value
                                ### if covered by clouds >> keep previous value
                                else:
                                    print '---  SITE : ', feature.GetField("code_site"), '  --- DATE : ', str(convertDate), ' (MONDAY) ---   CLOUD   ---' 
                                break
                            
                            elif convertDate > W_date and convertDate.isocalendar()[1] == W_date.isocalendar()[1]:
                                # --- OTHER WEEK DAY
                                maskCLD = fct.getCloudMask(title, Date, indexName, tile)
                                print 'Le masque de nuage est : ', maskCLD
                                maskWTR = water +  '/' + tile[1:] + '_WTRMask.tif'
                                index2 = fct.find_indexName(title, point, maskCLD, maskWTR) 
                                #if point not covered by clouds 
                                if index2 != None:
                                    print '---  SITE : ', feature.GetField("code_site"), '  --- DATE : ', str(convertDate), ' ------  VALUE : ', indexName_value, ' ---'
                                    nbDay = convertDate.weekday()
                                    # Mean computation
                                    indexName_value = (previousWeek[c]*nbDay + (7-nbDay)*index2)/7
                                    week[c] = indexName_value
                                else:
                                    print '---  SITE : ', feature.GetField("code_site"), '  --- DATE : ', str(convertDate), ' ---   CLOUD   ---' 
                                break
                
                c += 1
                        
            # --- Next week
            findexName.write(str(week)[2:12] + str(week)[13:-1] + '\n')
            W_date += delta
            previousWeek = list(week)
        
        
        #remove _MEAN files
        fct.removeMeanFile(indexName, DATA_path)       
        
        findexName.close()
        print 'Time serie file for', indexName, 'created in :', out
        
    return 0 
    
    

if __name__ == '__main__':
    if len(sys.argv) > 1:
        indexName, Bdate, Edate, DATA_path, out, shp, water = fct.readParams(sys.argv[1])
        createCSV(indexName, DATA_path, out, Bdate,Edate, shp, water)
    else:
        print 'No parameters file given' 