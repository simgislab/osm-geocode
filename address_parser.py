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

try:
    from osgeo import ogr, osr,  gdal
except ImportError:
    import ogr, osr, gdal

#global vars
_fs_encoding = sys.getfilesystemencoding()
_message_encoding = locale.getdefaultlocale()[1]


class AddressParser():

    def parse(self, sqlite_file):
       
        drv = ogr.GetDriverByName("SQLite")
        gdal.ErrorReset()
        data_source = drv.Open(sqlite_file.encode('utf-8'), True)
        if data_source is None:
            self.__show_err("SQLite file can't be opened!\n" + unicode(gdal.GetLastErrorMsg(), _message_encoding))
            return
        
        #setup fast writing
        data_source.ExecuteSQL('PRAGMA journal_mode=OFF')
        data_source.ExecuteSQL('PRAGMA synchronous=0')
        data_source.ExecuteSQL('PRAGMA cache_size=100000')

        layer = data_source[0]
        all_feats = []
        layer.ResetReading()
        feat = layer.GetNextFeature()
        while feat is not None:
            all_feats.append(feat)
            feat = layer.GetNextFeature()
        
        for feat in all_feats:
            addr = feat['addr_v']
            if not addr:
                continue
            addr = unicode(addr, 'utf-8').replace(u'п.', '').replace(u'с.', '').replace(u'г.', '').strip()
            addr = addr.replace(u'ул.', '').replace(u'пр.', '').replace(u'пр-т', '').replace(u'пер.', '').strip()
            addr = addr.replace(u'д.', '').replace(u'дом', '').strip()

            feat.SetField("g_addr", addr.encode('utf-8'))
            if layer.SetFeature(feat) != 0:
                print 'Failed to update feature.'
        #close DS's
        data_source.Destroy()

    def __show_err(self,  msg):
        print "Error: " + msg
