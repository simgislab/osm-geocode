"""
/***************************************************************************
 RuGeocoder
                                 A QGIS plugin
 Geocode your csv files to shp
                             -------------------
        begin                : 2012-02-20
        copyright            : (C) 2012 by Nikulin Evgeniy
        email                : nikulin.e at gmail
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os
import json
import urllib2
import urllib
import sys
import locale
from multiprocessing.pool import ThreadPool
from multiprocessing import Lock

from progressbar import *

try:
    from osgeo import ogr, osr,  gdal
except ImportError:
    import ogr, osr,  gdal

#global vars
_fs_encoding = sys.getfilesystemencoding()
_message_encoding = locale.getdefaultlocale()[1]



class OsmRuGeocoder():
    url = 'http://openstreetmap.ru/api/search?q='
    _lock = Lock()
    
    def _construct_search_str(self, region, rayon, city, street, house_number):
        search_str = ''
        if region:
            search_str += region +', '
        if rayon:
            search_str += rayon+', '
        if city:
            search_str += city+', '
        if street:
            search_str += street+', '
        if house_number:
            search_str += house_number
        search_str = search_str.rstrip().rstrip(',')
        #print(search_str)
        #import pdb;pdb.set_trace()
        return search_str

    def _search(self, region, rayon, city, street, house_number):
        full_addr = self._construct_search_str(region, rayon, city, street, house_number)
        full_addr = urllib.quote(full_addr)
        if not full_addr:
            #empty address
            return None
        full_url = unicode(self.url) + unicode(full_addr, "utf-8")
                
        f = urllib2.urlopen ( full_url.encode("utf-8") )
        resp_str = unicode( f.read(),  'utf-8')
        resp_json = json.loads(resp_str)
                
        if not resp_json["find"]:
            #0 results
            return None
        else:
            #hm... no way to find right result :( weight, addr_type_it, this_poi????
            #now get first
            res0 = resp_json["matches"][0]
            pt = ogr.Geometry( ogr.wkbPoint ) 
            pt.SetPoint_2D( 0,  float(res0["lon"]), float(res0["lat"] ))
            return pt, res0["display_name"]



    def geocode(self, region, rayon, city, street, house_number):
        #try to search as is
        res = self._search(region, None, city, street, house_number)  #rayon
        if res != None:
            #status check (magic :)
            status = 0
            if not house_number:
        	status = 1
            if not street:
        	status = 2
            if not city:
        	status = 3
            #if not rayon:
        	#status = 4
            return status, res
        
        #try to search street:
        res = self._search(region, None, city, street, None) #rayon
        if res != None:
            #status check (magic :)
            status = 1
            if not street:
        	status = 2
            if not city:
        	status = 3
            #if not rayon:
        	#status = 4
            return status, res
        
        #try to search settlement:
        res = self._search(region, None, city, None, None) #rayon
        if res != None:
            #status check (magic :)
            status = 2
            if not city:
        	status = 3
            #if not rayon:
        	#status = 4
            return status, res
        
        #try to search district:
        res = self._search(region, rayon, None, None, None)
        if res != None:
            #status check (magic :)
            status = 3
            if not rayon:
        	status = 4
            return status, res
        
        #try to search region:
        res = self._search(region, None, None, None, None)
        if res != None:
            return 4, res
        
        #hm. wtf?
        pt = ogr.Geometry( ogr.wkbPoint ) 
        pt.SetPoint_2D( 0, 0, 0)
        return -1, (pt, "Not found")
    
    
    geocode_status = { -1:"Not found", 0:"building", 1:"street", 2:"settlement", 3:"district", 4:"region" }
    
    
    
    #feature processing
    def process_feature(self, feat, layer, results, update_func):
	reg = feat['g_region']
        dist = feat['g_district']
        settl = feat['g_settl']
        street = feat['g_street']
        build = feat['g_building']
            
        res, (point, text) = self.geocode(reg, dist, settl, street, build) # dist
        results.append(res)
        feat.SetField("g_geocoded", text.encode('utf-8'))
        feat.SetField("g_status", self.geocode_status[res])
        feat.SetGeometry(point)
             
        if layer.SetFeature(feat) != 0:
    	    print 'Failed to update feature.'
    	    
    	#update progress bar
    	update_func()
    
    
    #main circle
    def process(self, sqlite_file, thread_count = 1):
        drv = ogr.GetDriverByName("ESRI Shapefile")
        gdal.ErrorReset()
        data_source = drv.Open(sqlite_file.encode('utf-8'), True)
        if data_source==None:
            self.__show_err("Shape file can't be opened!\n" + unicode(gdal.GetLastErrorMsg(), _message_encoding))
            return
        
        layer = data_source[0]
        layer.ResetReading()
        feat = layer.GetNextFeature()
        
        results=[]
        total = len(layer)
            
        features = []
        while feat is not None:
            features.append(feat)
            feat = layer.GetNextFeature()


	#prepare progressbar
	self._p_bar = ProgressBar(widgets = [ Bar('=', '[', ']'), ' ',
					      Percentage(), ' ',
					      ETA()]).start()
	self._p_bar.maxval = len(features)
	
        #start process
        pf =  lambda x: self.process_feature(x, layer, results, self.update_progress)
        pool = ThreadPool(thread_count)
        pool.map(pf, features, 1)
        pool.close()
        pool.join()

	self._p_bar.finish()
        #close DS's
        data_source.Destroy()
	
	#print statistics
	print "\t Results:"
        for status in range(-1,5):
            print str.format("\t\t {0}: {1}/{2}", self.geocode_status[status], results.count(status),total)
        print " "

    def update_progress(self):
	self._lock.acquire()
	self._p_bar.update(self._p_bar.currval+1)
	self._lock.release()