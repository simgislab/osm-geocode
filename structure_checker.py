import sys
import locale

try:
    from osgeo import ogr, osr,  gdal
except ImportError:
    import ogr, osr,  gdal

#global vars
_fs_encoding = sys.getfilesystemencoding()
_message_encoding = locale.getdefaultlocale()[1]

    
class DataStructureChecker():
    req_fields = ['tik',  'uik',  'addr_v', 'tik_id']
    
    def check_csv_exists(self, csv_file_path):
        input_data_source = ogr.Open(csv_file_path.encode('utf-8'))
        if not input_data_source:
            print 'Input source can\'t be opened: ' + unicode(gdal.GetLastErrorMsg(), _message_encoding)
        
        csv_layer = input_data_source[0]
        if not csv_layer:
            print 'Input source can\'t be opened: ' + unicode(gdal.GetLastErrorMsg(), _message_encoding)
        return True

    
    def check_tik_ids(self, csv_file_path):
        input_data_source = ogr.Open(csv_file_path.encode('utf-8'))
        csv_layer = input_data_source[0]

        tik_ids = {}
        in_feat = csv_layer.GetNextFeature()
        while in_feat is not None:
            id = in_feat['tik_id']
            name = in_feat['tik']
            if not id:
                    print '\t Invalid tik ids! Found null id. name = %s' % (name)
                    return False
            
            if tik_ids.has_key(id):
                if tik_ids[id] != name:
                    print '\t Invalid tik ids! Found: id = %s, name = %s and id = %s, name = %s' % (id, tik_ids[id], id, name)
                    return False
            else:
                tik_ids[id] = name
            in_feat = csv_layer.GetNextFeature()
        
        return True

        
    def check(self, csv_file_path):
        input_data_source = ogr.Open(csv_file_path.encode('utf-8'))
        csv_layer = input_data_source[0]

        csv_feat_defs = csv_layer.GetLayerDefn()
        
        field_names = []
        for i in range(csv_feat_defs.GetFieldCount()):
            field_def = csv_feat_defs.GetFieldDefn(i)
            field_names.append(field_def.GetName().lower())
         
        for req in self.req_fields:
            if req not in field_names:
                print '\t Invalid input data structure! Field %s not found!' % req
                return False
        
        return True
