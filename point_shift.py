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
import math

try:
    from osgeo import ogr, osr,  gdal
except ImportError:
    import ogr, osr, gdal

#global vars
_fs_encoding = sys.getfilesystemencoding()
_message_encoding = locale.getdefaultlocale()[1]


class PointShift():
    
    def shift(self, sqlite_file, shift_rad=0.00015, rotate=False):
        drv = ogr.GetDriverByName('SQLite')
        gdal.ErrorReset()
        data_source = drv.Open(sqlite_file.encode('utf-8'), True)
        if data_source is None:
            self.__show_err('SQLite file can\'t be opened!\n' + unicode(gdal.GetLastErrorMsg(), _message_encoding))
            return
        
        #setup fast writing
        data_source.ExecuteSQL('PRAGMA journal_mode=OFF')
        data_source.ExecuteSQL('PRAGMA synchronous=0')
        data_source.ExecuteSQL('PRAGMA cache_size=100000')
        
        layer = data_source[0]
        
        d = dict()
        layer.ResetReading()
        feat = layer.GetNextFeature()
        while feat is not None:
            #add geom to dict 
            geom = feat.GetGeometryRef()
            wkt = str(geom.ExportToWkt())
            if wkt not in d:
                d[wkt] = [feat]  # [feat.GetFID()]
            else:
                d[wkt].append(feat)  # (feat.GetFID())
            feat = layer.GetNextFeature()
        
        #shift
        for k, v in d.iteritems():
            feat_count = len(v)
            if feat_count == 1:
                continue                
            else:
                #define params
                full_perimeter = 2 * math.pi
                angle_step = full_perimeter / feat_count
                if feat_count == 2 and rotate:
                    current_angle = math.pi / 2
                else:
                    current_angle = 0
                #change geometry
                for feat in v:
                    sin_curr_angle = math.sin(current_angle)
                    cos_curr_angle = math.cos(current_angle)
                    dx = shift_rad * sin_curr_angle
                    dy = shift_rad * cos_curr_angle
                    
                    geom = feat.GetGeometryRef()
                    new_geom = ogr.Geometry(ogr.wkbPoint)
                    new_geom.SetPoint(0, geom.GetX() + dx, geom.GetY() + dy)

                    feat.SetGeometry(new_geom)
                    if layer.SetFeature(feat) != 0:
                        print 'Failed to update feature.'
                    
                    current_angle += angle_step 

        #close DS's
        data_source.Destroy()

    def __show_err(self,  msg):
        print 'Error: ' + msg
