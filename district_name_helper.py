# -*- coding: utf-8 -*-

try:
    from osgeo import ogr, osr,  gdal
except ImportError:
    import ogr, osr,  gdal
    
from os import path 

class DistrictNameHelper():

    def set_district_name(self, sqlite_file):
       
        #set attr for layer
        drv = ogr.GetDriverByName("ESRI Shapefile")
        gdal.ErrorReset()
        data_source = drv.Open(sqlite_file.encode('utf-8'), True)
        if data_source==None:
            self.__show_err("Shape file can't be opened!\n" + unicode(gdal.GetLastErrorMsg(), _message_encoding))
            return
        
        layer = data_source[0]
        
        layer.ResetReading()
        feat = layer.GetNextFeature()
        while feat is not None:
            district_name = feat['district']
            feat.SetField("g_district", district_name)
            if layer.SetFeature(feat) != 0:
                print 'Failed to update feature.'
            feat = layer.GetNextFeature()
        #close DS's
        data_source.Destroy()

    
    
    def __show_err(self,  msg):
        print "Error: " + msg
        