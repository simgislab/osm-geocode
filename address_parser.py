# -*- coding: utf-8 -*-
import sys
import locale
from os import path 

try:
    from osgeo import ogr, osr,  gdal
except ImportError:
    import ogr, osr,  gdal

#global vars
_fs_encoding = sys.getfilesystemencoding()
_message_encoding = locale.getdefaultlocale()[1]


class AddressParser():

    def parse(self, sqlite_file):
       
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
            addr = feat['addr_v']

            if not addr:
                feat = layer.GetNextFeature()
                continue

            addr = unicode(addr,"utf-8").replace(u'п.','').replace(u'с.','').replace(u'г.','').strip()
            addr = addr.replace(u'ул.','').replace(u'пр.','').replace(u'пр-т','').replace(u'пер.','').strip()
            addr = addr.replace(u'д.','').replace(u'дом','').strip()
            
            feat.SetField("g_addr", addr.encode('utf-8'))
            if layer.SetFeature(feat) != 0:
                print 'Failed to update feature.'
            feat = layer.GetNextFeature()
        #close DS's
        data_source.Destroy()

    
    
    def __show_err(self,  msg):
        print "Error: " + msg
        