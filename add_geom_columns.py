# -*- coding: utf-8 -*-
"""
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
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


class GeomColumnsExtractor():
    latColumnName = 'lat'
    lonColumnName = 'lon'

    def extract_columns(self, sqlite_file):
       
        drv = ogr.GetDriverByName("SQLite")
        gdal.ErrorReset()
        data_source = drv.Open(sqlite_file.encode('utf-8'), True)
        if data_source==None:
            self.__show_err("SQLite file can't be opened!\n" + unicode(gdal.GetLastErrorMsg(), _message_encoding))
            return
        
        #setup fast writing
        data_source.ExecuteSQL('PRAGMA journal_mode=OFF')
        data_source.ExecuteSQL('PRAGMA synchronous=0')
        data_source.ExecuteSQL('PRAGMA cache_size=100000')

        
        layer = data_source[0]
        
        #add fields
        out_defs = layer.GetLayerDefn()
        if out_defs.GetFieldIndex(self.latColumnName) < 0:
            if not self.__add_field(layer, self.latColumnName, ogr.OFTReal):
                self.__show_err( self.tr("Unable to create a field %1!").arg(self.latColumnName))
                return
        if out_defs.GetFieldIndex(self.lonColumnName) < 0:
            if not self.__add_field(layer, self.lonColumnName, ogr.OFTReal):
                self.__show_err( self.tr("Unable to create a field %1!").arg(self.lonColumnName))
                return
        
        all_feats = []
        layer.ResetReading()
        feat = layer.GetNextFeature()
        while feat is not None:
            all_feats.append(feat)
            feat = layer.GetNextFeature()
        
        for feat in all_feats:
            geom = feat.GetGeometryRef()
            feat.SetField(self.lonColumnName, geom.GetX())
            feat.SetField(self.latColumnName, geom.GetY())
            
            if layer.SetFeature(feat) != 0:
                print 'Failed to update feature.'
            
        #close DS's
        data_source.Destroy()
        
    def __add_field(self,  layer, field_name,   field_type=ogr.OFTString,  field_len=None):
        field_def = ogr.FieldDefn(field_name, field_type)
        if field_len:
            field_def.SetWidth(field_len)
        if layer.CreateField (field_def) != 0:
            self.__show_err( self.tr("Unable to create a field %1!").arg(field_def.GetNameRef()))
            return False
        else:
            return True
    
    def __show_err(self,  msg):
        print "Error: " + msg
        