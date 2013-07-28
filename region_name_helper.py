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


osm_ru_map = {
    'RU-ALT': {'dd': ['Алтайский край'],                    'osm_ru': 'Алтайский край'},
    'RU-AMU': {'dd': ['Амурская область', 'Амурская обл.'], 'osm_ru': 'Амурская область'},
    'RU-AL':  {'dd': ['Республика Алтай'],                  'osm_ru': 'Алтай'},
    'RU-AD':  {'dd': ['Адыгея'],                            'osm_ru': 'Адыгея'},
    'RU-ARK': {'dd': ['Архангельская обл.'],                'osm_ru': 'Архангельская область'},
    'RU-AST': {'dd': ['Астраханская обл.'],                 'osm_ru': 'Астраханская область'},
    'RU-BA':  {'dd': ['Башкортостан'],                      'osm_ru': 'Башкортостан'},
    'RU-BEL': {'dd': ['Белгородская обл.'],                 'osm_ru': 'Белгородская область'},
    'RU-BRY': {'dd': ['Брянская обл.'],                     'osm_ru': 'Брянская область'},
    'RU-BU':  {'dd': ['Бурятия'],                           'osm_ru': 'Бурятия'},
    'RU-CE':  {'dd': ['Чечня'],                             'osm_ru': 'Чеченская республика'},
    'RU-CHE': {'dd': ['Челябинская обл.'],                  'osm_ru': 'Челябинская область'},
    'RU-CHU': {'dd': ['Чукотский АО'],                      'osm_ru': 'Чукотский автономный округ'},
    'RU-CU':  {'dd': ['Чувашия', 'Чувашская Республика'],   'osm_ru': 'Чувашия'},
    'RU-DA':  {'dd': ['Дагестан', 'Республика Дагестан'],   'osm_ru': 'Дагестан'},
    'RU-IN':  {'dd': ['Ингушетия', 'Республика Ингушетия'], 'osm_ru': 'Ингушетия'},
    'RU-IRK': {'dd': ['Иркутская обл.'],                    'osm_ru': 'Иркутская область'},
    'RU-IVA': {'dd': ['Ивановская обл.'],                   'osm_ru': 'Ивановская область'},
    'RU-KAM': {'dd': ['Камчатский край'],                   'osm_ru': 'Камчатский край'},
    'RU-KB':  {'dd': ['Кабардино-Балкария'],                'osm_ru': 'Кабардино-Балкарская республика'},
    'RU-KGN': {'dd': ['Курганская обл.'],                   'osm_ru': 'Курганская область'},
    'RU-KHA': {'dd': ['Хабаровский край'],                  'osm_ru': 'Хабаровский край'},
    'RU-KIR': {'dd': ['Кировская обл.'],                    'osm_ru': 'Кировская область'},
    'RU-KDA': {'dd': ['Краснодарский край'],                'osm_ru': 'Краснодарский край'},
    'RU-KL':  {'dd': ['Калмыкия'],                          'osm_ru': 'Республика Калмыкия'},
    'RU-KC':  {'dd': ['Карачаево-Черкесская республика', 'Карачаево-Черкесия', 'Карачаево-Черкессия'], 'osm_ru': 'Карачаево-Черкесская республика'},
    'RU-KEM': {'dd': ['Кемеровская область', 'Кемеровская обл.'],                                      'osm_ru': 'Кемеровская область'},
    'RU-KGD': {'dd': ['Калининградская область', 'Калининградская обл.'],                              'osm_ru': 'Калининградская область'},
    'RU-KK':  {'dd': ['Хакасия'],                            'osm_ru': 'Республика Хакасия'},
    'RU-KLU': {'dd': ['Калужская область', 'Калужская обл.'],'osm_ru': 'Калужская область'},
    'RU-KO':  {'dd': ['Республика Коми', 'республика Коми'], 'osm_ru': 'Республика Коми'},
    'RU-KOS': {'dd': ['Костромская обл.'],                   'osm_ru': 'Костромская область'},
    'RU-KR':  {'dd': ['Карелия', 'республика Карелия'],      'osm_ru': 'Республика Карелия'},
    'RU-KRS': {'dd': ['Курская обл.'],                       'osm_ru': 'Курская область'},
    'RU-KYA': {'dd': ['Красноярский край'],                  'osm_ru': 'Красноярский край'},
    'RU-LEN': {'dd': ['Ленинградская обл.'],                 'osm_ru': 'Ленинградская область'},
    'RU-LIP': {'dd': ['Липецкая обл.'],                      'osm_ru': 'Липецкая область'},
    'RU-MAG': {'dd': ['Магаданская область', 'Магаданская обл.'], 'osm_ru': 'Магаданская область'},
    'RU-ME':  {'dd': ['республика Марий Эл', 'Марий Эл', 'Республика Марий Эл', 'республикаМарий Эл'], 'osm_ru': 'Марий Эл'},
    'RU-MO':  {'dd': ['Мордовия', 'Республика Мордовия'],    'osm_ru': 'Республика Мордовия'},
    'RU-MOS': {'dd': ['Московская обл.'],                    'osm_ru': 'Московская область'},
    'RU-MOW': {'dd': ['Москва'],                             'osm_ru': 'Москва'},
    'RU-MUR': {'dd': ['Мурманская обл.'],                    'osm_ru': 'Мурманская область'},
    'RU-NGR': {'dd': ['Новгородская обл.'],                  'osm_ru': 'Новгородская область'},
    'RU-NIZ': {'dd': ['Нижегородская обл.'],                 'osm_ru': 'Нижегородская область'},
    'RU-NVS': {'dd': ['Новосибирская обл.'],                 'osm_ru': 'Новосибирская область'},
    'RU-OMS': {'dd': ['Омская область', 'Омская обл.'],      'osm_ru': 'Омская область'},
    'RU-ORE': {'dd': ['Оренбургская обл.'],                  'osm_ru': 'Оренбургская область'},
    'RU-ORL': {'dd': ['Орловская обл.'],                     'osm_ru': 'Орловская область'},
    'RU-PER': {'dd': ['Пермский край'],                      'osm_ru': 'Пермский край'},
    'RU-PNZ': {'dd': ['Пензенская обл.'],                    'osm_ru': 'Пензенская область'},
    'RU-PRI': {'dd': ['Приморский край'],                    'osm_ru': 'Приморский край'},
    'RU-PSK': {'dd': ['Псковская обл.'],                     'osm_ru': 'Псковская область'},
    'RU-ROS': {'dd': ['Ростовская обл.'],                    'osm_ru': 'Ростовская область'},
    'RU-RYA': {'dd': ['Рязанская обл.'],                     'osm_ru': 'Рязанская область'},
    'RU-SA':  {'dd': ['Республика Саха', 'Саха (Якутия)', 'Республика Саха (Якутия)'], 'osm_ru': 'Республика Саха (Якутия)'},
    'RU-SAK': {'dd': ['Сахалинская обл.'],                   'osm_ru': 'Сахалинская область'},
    'RU-SAM': {'dd': ['Самарская обл.'],                     'osm_ru': 'Самарская область'},
    'RU-SAR': {'dd': ['Саратовская обл.'],                   'osm_ru': 'Саратовская область'},
    'RU-SE':  {'dd': ['РСО - Алания', 'Северная Осетия'],    'osm_ru': 'Северная Осетия'},
    'RU-SMO': {'dd': ['Смоленская обл.'],                    'osm_ru': 'Смоленская область'},
    'RU-SPE': {'dd': ['г.Санкт-Петербург'],                  'osm_ru': 'Санкт-Петербург'},
    'RU-STA': {'dd': ['Ставропольский край'],                'osm_ru': 'Ставропольский край'},
    'RU-SVE': {'dd': ['Свердловская обл.'],                  'osm_ru': 'Свердловская область'},
    'RU-TA':  {'dd': ['Татарстан'],                          'osm_ru': 'Татарстан'},
    'RU-TAM': {'dd': ['Тамбовская обл.'],                    'osm_ru': 'Тамбовская область'},
    'RU-TOM': {'dd': ['Томская область', 'Томская обл.'],    'osm_ru': 'Томская область'},
    'RU-TUL': {'dd': ['Тульская обл.'],                      'osm_ru': 'Тульская область'},
    'RU-TY':  {'dd': ['республика Тыва'],                    'osm_ru': 'Тыва'},
    'RU-VOR': {'dd': ['Воронежская обл.'],                   'osm_ru': 'Воронежская область'},
    'RU-YEV': {'dd': ['Еврейская АО'],                       'osm_ru': 'Еврейская автономная область'},
    'RU-VGG': {'dd': ['Волгоградская обл.'],                 'osm_ru': 'Волгоградская область'},
    'RU-UD':  {'dd': ['Удмуртия'],                           'osm_ru': 'Удмуртская республика'},
    'RU-VLG': {'dd': ['Вологодская обл.'],                   'osm_ru': 'Вологодская область'},
    'RU-ULY': {'dd': ['Ульяновская обл.'],                   'osm_ru': 'Ульяновская область'},
    'RU-YAR': {'dd': ['Ярославская обл.'],                   'osm_ru': 'Ярославская область'},
    'RU-TVE': {'dd': ['Тверская обл.'],                      'osm_ru': 'Тверская область'},
    'RU-VLA': {'dd': ['Владимирская обл.', 'Владимирская область'], 'osm_ru': 'Владимирская область'},
    'RU-TYU': {'dd': ['Тюменская обл.'],                            'osm_ru': 'Тюменская область'},
    'RU-ZAB': {'dd': ['Агинский Бурятский АО', 'Читинская обл.'],   'osm_ru': 'Забайкальский край'}
}


class RegionNameHelper():
    @staticmethod
    def region_code_exists(region_code):
        return osm_ru_map.has_key(region_code)
    
    @staticmethod
    def get_region_list():
        all_codes = ''
        codes = osm_ru_map.keys()
        codes.sort()
        for code in codes:
            all_codes += code+'\t '+osm_ru_map[code]['osm_ru']+'\n'
        return all_codes
    
    @staticmethod
    def get_region_codes():
        return osm_ru_map.keys()
    

    def set_region_name(self, sqlite_file, region_code):
        #get region name
        reg_name = osm_ru_map[region_code]['osm_ru']
        #self._get_region_name_by_code(sqlite_file)
        
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

        #wtf??? if not readin - very slow        
        layer.ResetReading()
        all_feats = []
        feat = layer.GetNextFeature()
        while feat is not None:
           all_feats.append(feat)
           feat = layer.GetNextFeature()
        
        #while feat is not None:
        for feat in all_feats:
            feat.SetField("g_region", reg_name)
            #print feat['uik'] 
            if layer.SetFeature(feat) != 0:
                print 'Failed to update feature: uik=' + feat['uik']
            #layer.SetNextByIndex(feat.GetFID())
            #feat = layer.GetNextFeature()
       
        #close DS's
        data_source.Destroy()

    
    def _get_region_name_by_code(self, sqlite_file):
        layer_name = path.splitext(path.basename(sqlite_file))[0]
        return osm_ru_map[layer_name.upper()]['osm_ru']
        
    
    def __show_err(self,  msg):
        print "Error: " + msg
        