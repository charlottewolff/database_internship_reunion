import os, sys
from osgeo import gdal, ogr
import numpy as np
import os, os.path, optparse,sys
import shutil


def buffer(infile,outfile,erosion,dilatation):
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
    

def maskSen2cor(image,bande,out):
    """create the mask to apply on the ndvi image"""
    # Image reading  
    Image  = gdal.Open(image)
    geoTransform = Image.GetGeoTransform()
    projection = Image.GetProjection()
    Band   = Image.GetRasterBand(1) 
    NoData = Band.GetNoDataValue()


    nBands = Image.RasterCount      
    nRows  = Image.RasterYSize      
    nCols  = Image.RasterXSize      
    dType  = Band.DataType          

    # Mean and standart deviation computation 
    print '########### Mean and standart deviation computation ###########'
    pix = []  
    for ThisRow in range(nRows):
        ThisLine = Band.ReadAsArray(0,ThisRow,nCols,1)
        for ThisCol in range(nCols):
            pix.append(ThisLine[0].item(ThisCol))
    pixArray = np.asarray(pix)
    mean = np.mean(pixArray)
    stdDev = np.std(pixArray)
    print 'Mean = ',mean 
    print 'Standart deviation = ',stdDev

    # Image normalization --> values between -1 and 1
    print '########### Normalization ###########'
    exp1 = '"(im1b1-' + str(mean) + ")/" + str(stdDev) + '"'
    command1 = 'otbcli_BandMath -il ' + image + " -out norm.tif -exp " + exp1
    os.system(command1)
    
    # Values =-1 or 1
    command2 = 'otbcli_BandMath -il norm.tif -out norm01.tif -exp "im1b1 > 0 ? 99 : -99"'
    os.system(command2)
    os.remove('norm.tif')
    
    # Raster to vector
    print '########### Raster ---> Vector ###########'
    command3 = 'gdal_polygonize.py norm01.tif -f "ESRI Shapefile" vectors.shp'
    os.system(command3)
    os.remove('norm01.tif')
    
    # Cloud-free polygons removal
    print '########### Cloud-free pixel removal ###########'
    command4 = 'ogr2ogr tampon.shp vectors.shp -where "DN > 0"'
    os.system(command4)
    os.remove('vectors.shp')
    os.remove('vectors.prj')
    os.remove('vectors.dbf')
    os.remove('vectors.shx') 
    
    # Erosion & dilatation
    #print '########### Erosion and dilatation ###########'
    #buffer('vectorsFilter.shp', 'tampon.shp', -20,100)
    #os.remove('vectorsFilter.shp')
    #os.remove('vectorsFilter.prj')
    #os.remove('vectorsFilter.dbf')
    #os.remove('vectorsFilter.shx')
    
    # to WGS84
    print '########### Shapefile in WGS84 ###########'
    command5 = 'ogr2ogr -f "ESRI Shapefile" tampon_wgs84.shp tampon.shp -t_srs EPSG:4326'
    os.system(command5)
    os.remove('tampon.shp')
    os.remove('tampon.prj')
    os.remove('tampon.dbf')
    os.remove('tampon.shx')
    
    # Create out .tif file
    print '########### .tif file ###########'    
    command6 = 'gdalwarp -ot Float32 -t_srs EPSG:4326 -r near -of GTiff -co COMPRESS=DEFLATE -co PREDICTOR=1 -co ZLEVEL=6 ' + bande + ' wgs84.tif'
    os.system(command6)    
    command7 = 'otbcli_BandMath -il wgs84.tif -out ' + out + ' -exp "im1b1 > 0 ? 0 : 0"'
    os.system(command7)
    os.remove('wgs84.tif')
    
    # Rasterization
    print  '########### Vector ---> Raster ###########'
    command8 = 'gdal_rasterize -a DN -l tampon_wgs84 tampon_wgs84.shp ' + out
    os.system(command8)
    os.remove('tampon_wgs84.shp')
    os.remove('tampon_wgs84.prj')
    os.remove('tampon_wgs84.dbf')
    os.remove('tampon_wgs84.shx')
    return 0

    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        maskSen2cor(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print 'No argument'   
    
    
#maskSen2cor("L2A_T39LUG_20170312T070231_CLD_20m.jp2",'masque/tampon.tif')
