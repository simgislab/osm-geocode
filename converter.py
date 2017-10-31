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
    import ogr, osr, gdal

#global vars
_fs_encoding = sys.getfilesystemencoding()
_message_encoding = locale.getdefaultlocale()[1]


class Converter():

    def processing(self, csv_file, shape_file):
        #prepare output data source
        drv = ogr.GetDriverByName("SQLite")
        #check output datasource exists
        if path.exists(shape_file):
            drv.DeleteDataSource(shape_file.encode('utf-8'))

        #create output sqlite file
        gdal.ErrorReset()
        output_data_source = drv.CreateDataSource(shape_file.encode('utf-8'))
        if output_data_source is None:
            self.__show_err("Output sqlite file can't be created!\n" +
                            unicode(gdal.GetLastErrorMsg(), _message_encoding))
            return
        
        #setup fast writing
        sql_lyr = output_data_source.ExecuteSQL('PRAGMA journal_mode=OFF')
        if sql_lyr is not None:
            output_data_source.ReleaseResultSet(sql_lyr)
        sql_lyr = output_data_source.ExecuteSQL('PRAGMA synchronous=0')
        if sql_lyr is not None:
            output_data_source.ReleaseResultSet(sql_lyr)
        sql_lyr = output_data_source.ExecuteSQL('PRAGMA cache_size=100000')
        if sql_lyr is not None:
            output_data_source.ReleaseResultSet(sql_lyr)
        #gdal.SetConfigOption('OGR_SQLITE_SYNCHRONOUS', 'OFF')

        wgs_sr = osr.SpatialReference()
        wgs_sr.ImportFromEPSG(4326)

        layer_name = path.splitext(path.basename(shape_file))[0]
        output_layer = output_data_source.CreateLayer(layer_name.encode('utf-8'), srs=wgs_sr, geom_type=ogr.wkbPoint)

        #copy fields
        input_data_source = ogr.Open(csv_file.encode('utf-8'))
        csv_layer = input_data_source[0]

        csv_feat_defs = csv_layer.GetLayerDefn()
        for i in range(csv_feat_defs.GetFieldCount()):
            field_def = csv_feat_defs.GetFieldDefn(i)
            if field_def.GetType() == ogr.OFTString:
                field_def.SetWidth(255)
            if output_layer.CreateField(field_def) != 0:
                self.__show_err("Unable to create a field %s!" % field_def.GetNameRef())
                return

        #add geocoder additional fields
        if not self.add_additional_fields(output_layer):
            return

        in_feat = csv_layer.GetNextFeature()
        while in_feat is not None:
            out_feat = ogr.Feature(output_layer.GetLayerDefn())
            #copy fields
            res = out_feat.SetFrom(in_feat)
            if res != 0:
                self.__show_err("Unable to construct the feature!")
                return
            #set geom
            pt = ogr.Geometry(ogr.wkbPoint)
            pt.SetPoint_2D(0, 0, 0)
            out_feat.SetGeometry(pt)
            #add to layer
            if output_layer.CreateFeature(out_feat) != 0:
                self.__show_err("Failed to create feature in SHP file!")
                return
            in_feat = csv_layer.GetNextFeature()
        
        #close DS's
        output_data_source = None
        input_data_source = None

    def add_additional_fields(self,  output_layer):
        out_defs = output_layer.GetLayerDefn()
        if out_defs.GetFieldIndex("g_region") < 0:
            if not self.__add_field(output_layer, "g_region", ogr.OFTString,  255):
                return False
        if out_defs.GetFieldIndex("g_addr") < 0:
            if not self.__add_field(output_layer, "g_addr", ogr.OFTString,  255):
                return False
        if out_defs.GetFieldIndex("g_geocoded") < 0:
            if not self.__add_field(output_layer, "g_geocoded", ogr.OFTString,  255):
                return False
        if out_defs.GetFieldIndex("g_status") < 0:
            if not self.__add_field(output_layer, "g_status", ogr.OFTString,  100):
                return False
        if out_defs.GetFieldIndex("g_osm_id") < 0:
            if not self.__add_field(output_layer, "g_osm_id", ogr.OFTInteger,  100):
                return False
        return True

    def __add_field(self,  layer, field_name,   field_type=ogr.OFTString,  field_len=None):
        field_def = ogr.FieldDefn(field_name, field_type)
        if field_len:
            field_def.SetWidth(field_len)
        if layer.CreateField(field_def) != 0:
            self.__show_err("Unable to create a field %s!" % field_def.GetNameRef())
            return False
        else:
            return True
            
    def __show_err(self,  msg):
        print "Error: " + msg
