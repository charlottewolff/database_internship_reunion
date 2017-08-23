# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 16:32:01 2017

@author: seas-oi
"""

from osgeo import gdal, ogr
import os, os.path, optparse,sys
import glob
import shutil


def createColourImage(image2color,CLDmask,out):
    """create the colour image for the quick look
    image2color : path to index image
    CLDmask : corresponding cloud mask for the image2color
    out : path to created quicklook image
    """
    
    #--- Resized image
    print '--------------------------------------------------------  New image [0 ; 255]  --------------------------------------------------------'
    command1 = 'gdal_calc.py -A ' + image2color + ' --outfile=resized.tif --calc="255-(255*(A)*(A>0))" --overwrite' 
    os.system(command1)    
    
    #--- Image coloration
    print '--------------------------------------------------------  3-band image -- colorized with summer look-up table  --------------------------------------------------------'
    command2 = 'otbcli_ColorMapping -in resized.tif -method continuous -method.continuous.lut summer -out Colorized_summer.tif'
    os.system(command2)
    os.remove('resized.tif')

    #--- Cloud in black
    print '--------------------------------------------------------  Clouds colored in black  --------------------------------------------------------'
    command3 = 'gdal_calc.py -A Colorized_summer.tif -B ' + CLDmask + ' --outfile=cloud.tif --calc="A*(B == 0)+1*(B > 0)" --allBands=A --overwrite'
    os.system(command3)
    os.remove('Colorized_summer.tif')    
    
    #--- Change image resolution
    print '--------------------------------------------------------  New resolution  --------------------------------------------------------'
    command4 = 'gdal_translate -outsize 1000 1000 -ot Byte -r bilinear cloud.tif ' + out 
    os.system(command4)
    os.remove('cloud.tif')
    
    return 0
    
    
if __name__ == '__main__':
    
    if len(sys.argv) > 1:
        createColourImage(sys.argv[1],sys.argv[2],sys.argv[3])
    else:
        print 'three arguments needed : image2color CLDmask outPath'     