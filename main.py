#!/usr/bin/python
import sys
import glob
import os
import argparse

from converter import Converter
from region_name_helper import RegionNameHelper 
from district_name_helper import DistrictNameHelper
from address_parser import AddressParser
from osm_ru_geocoder import OsmRuGeocoder

def argparser_prepare():
    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        max_help_position = 35
        
    parser = argparse.ArgumentParser(description='Process and geocode UIC tables',   
                    formatter_class=PrettyFormatter)
    parser.add_argument('source',  type=str, 
                    help='file or directory path for processing')
    parser.add_argument('-t','--threads', type=int, default=1, 
                    help='geocoding threads count')
    parser.epilog ='''Samples:
                 %(prog)s /home/someuser/moscow.csv
                 %(prog)s -t 3 /home/someuser/all_uics/
                 ''' % {'prog':parser.prog}
    return parser

def process_file(csv_file, thread_count):
    #create instances 
    conv = Converter()
    region_helper = RegionNameHelper()
    district_helper = DistrictNameHelper()
    addr_parser = AddressParser()
    geocoder = OsmRuGeocoder()
    
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
    geocoder.process(shape_path, thread_count = thread_count)


def main(args):
    #parse args
    parser = argparser_prepare()
    args = parser.parse_args()
    
    #get source type
    if os.path.isfile(args.source):
        args.sorce_type = 'file'
    if os.path.isdir(args.source):
        args.sorce_type = 'dir'

    #processing
    if args.sorce_type == 'file':
        process_file(args.source, args.threads)
    else:
        os.chdir(args.source)
        csv_files = glob.glob("*.csv")
        for csv_file in csv_files:
            process_file(csv_file, args.threads)

if __name__=="__main__":
    args = sys.argv[ 1: ]
    main(args)