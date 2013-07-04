#!/usr/bin/python

from converter import Converter
from region_name_helper import RegionNameHelper 
from district_name_helper import DistrictNameHelper
from address_parser import AddressParser
from osm_ru_geocoder import OsmRuGeocoder

import sys
import glob
import os



def main(args):
    if len(args)<1:
        print "Need dir with csv files!!!"
        return -1
    
    conv = Converter()
    region_helper = RegionNameHelper()
    district_helper = DistrictNameHelper()
    addr_parser = AddressParser()
    geocoder = OsmRuGeocoder()
    
    wd = args[0]
    os.chdir(wd)
    csv_files = glob.glob("*.csv")
    for csv_file in csv_files:
        print "Process " + csv_file + ": "
        shape_path = csv_file.replace('.csv','.shp')
        print "\t Convert to shapefile..."
        conv.processing(csv_file, shape_path)
        print "\t Set region name..."
        region_helper.set_region_name(shape_path)
        #print "\t Set district name..."
        #district_helper.set_district_name(shape_path)
        print "\t Parse address..."
        addr_parser.parse(shape_path)
        print "\t Geocode..."
        geocoder.process(shape_path, thread_count = 5)

if __name__=="__main__":
    args = sys.argv[ 1: ]
    main(args)