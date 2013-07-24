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
from structure_checker import DataStructureChecker

def argparser_prepare():
    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        max_help_position = 35
        
    parser = argparse.ArgumentParser(description='Process and geocode UIC tables',   
                    formatter_class=PrettyFormatter)
    parser.add_argument('source',  type=str, 
                    help='file or directory path for processing')
    parser.add_argument('-t','--threads', type=int, default=1, 
                    help='geocoding threads count')
    parser.add_argument('-r','--region', type=str, default='RU-MOW',  
                    help='code of region')
    parser.epilog ='''Samples:
                 %(prog)s /home/someuser/moscow.csv
                 %(prog)s -t 3 /home/someuser/all_uics/
                 %(prog)s -t 5 -r RU-SPE /home/someuser/saint-pet.csv
                 ''' % {'prog':parser.prog}
    return parser

def process_file(csv_file, thread_count, region_code):
    #create instances 
    conv = Converter()
    checker = DataStructureChecker()
    region_helper = RegionNameHelper()
    district_helper = DistrictNameHelper()
    addr_parser = AddressParser()
    geocoder = OsmRuGeocoder()
    
    print "Process " + csv_file + ": "
    shape_path = csv_file.replace('.csv','.shp')
    print "\t Check input data structure..."
    if not checker.check(csv_file):
            return
    print "\t Check tik ids..."
    if not checker.check_tik_ids(csv_file):
            return
    print "\t Check uik ids..."
    if not checker.check_uik_ids(csv_file):
            return
    print "\t Check uik addr_v..."
    if not checker.check_addr_v(csv_file):
            return
    print "\t Convert to shapefile..."
    conv.processing(csv_file, shape_path)
    print "\t Set region name..."
    region_helper.set_region_name(shape_path, region_code)
    print "\t Parse address..."
    addr_parser.parse(shape_path)
    print "\t Geocode..."
    geocoder.process(shape_path, thread_count = thread_count)


def main():
    #parse args
    parser = argparser_prepare()
    args = parser.parse_args()
    
    #check args 
    if args.region not in RegionNameHelper.get_region_codes():
        print "Invalid argument value! Region code not in list:\n"+RegionNameHelper.get_region_list()
        return 0
    
    #get source type
    args.source_type = ''
    if os.path.isfile(args.source):
        args.source_type = 'file'
    if os.path.isdir(args.source):
        args.source_type = 'dir'

    #processing
    if not args.source_type:
        print 'Incompatible source type!'
        return
    if args.source_type == 'file':
        process_file(args.source, args.threads, args.region)
    if args.source_type == 'dir':
        os.chdir(args.source)
        csv_files = glob.glob("*.csv")
        for csv_file in csv_files:
            process_file(csv_file, args.threads, args.region)

if __name__=="__main__":
    main()
