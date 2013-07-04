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
            addr = "Москва, " + feat['addr_v']
            #print(feat['uik'])
            
            if not addr:
                feat = layer.GetNextFeature()
                continue
            
            comp = addr.split(',')
            
            if len(comp)<1:
                feat = layer.GetNextFeature()
                continue
            
            #remove index
            if comp[0].strip().isdigit():
                comp.remove(comp[0])
           
            #remove region
            if len(comp)>0:
                c = unicode(comp[0],"utf-8").lower().strip()
                exclude = [u'башкортостан', u'адыгея', u'татарстан', u'карачаево-черкесия', 
                           u'кабардино-балкария', u'удмуртия', u'чечня', u'северная осетия']
                if c.count(u'область') or c.count(u'обл.') or c.count(u'край') or c.count(u'республика') or c.count(u' ао') or (c in exclude):
                    comp.remove(comp[0])
                 
            #remove district
            if len(comp)>0:
                c = unicode(comp[0],"utf-8").strip().lower()
                exclude = []
                if c.count(u'район') or c.count(u'р-н') or (c in exclude):
                    comp.remove(comp[0])
            
            #set settlement
            if len(comp)>0:
                settl = unicode(comp[0],"utf-8").replace(u'п.','').replace(u'с.','').replace(u'г.','').strip()
                feat.SetField("g_settl", settl.encode("utf-8"))
                comp.remove(comp[0])
            
            #set street
            if len(comp)>0:
                street = unicode(comp[0],"utf-8").replace(u'ул.','').replace(u'пр.','').replace(u'пр-т','').replace(u'пер.','').strip()
                feat.SetField("g_street", street.encode('utf-8'))
                comp.remove(comp[0])
            
            #set building
            if len(comp)>0:
                build = unicode(comp[0],"utf-8").replace(u'д.','').strip()
                feat.SetField("g_building", build.encode('utf-8'))
                comp.remove(comp[0])

            
            if layer.SetFeature(feat) != 0:
                print 'Failed to update feature.'
            feat = layer.GetNextFeature()
        #close DS's
        data_source.Destroy()

    
    
    def __show_err(self,  msg):
        print "Error: " + msg
        