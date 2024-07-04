# задача класса объеденить все процессы в один
'''
* запускаем по всем компаниям скачивание из яндекса. Из файла tables\\to_search.csv скриптом - to_search_yandex.py результат записывается в to_search.xlsx
* запускаем поиск из zoon со страницы поиска load_from_zoon_by_ya_data.py, получаем список html

* запускаем скрипт получения json с полями из страниц html результатов поиска parse_from_zoon_search.py - сохраняем результат в json файлы

* запускаем скрипт match_data_ya_and_zoon_search.py сопоставление zoon и яндекса результат записываем в match_zoon_ya.xlsx
* запускаем скрипт load_from_zoon_details_by_match_ya.py скачивание деталей по компаниям
* запускаем скрипт parse_from_zoon_details_by_match_ya.py для парсинга деталей, результат записываем в match_zoon_ya_with_details.xlsx
'''
import logging
import common.common as common

import ta_parser.load_data as ta_load_data
import zoon_parser.select_best_zoon_search as select_best_zoon_search
import ta_parser.select_best_trip_search as select_best_trip_search
import time
import ta_parser.load_trip_details as load_trip_details
import ta_parser.load_trip_search as load_trip_search
import zoon_parser.load_zoon_details as load_zoon_details
import zoon_parser.load_zoon_search as load_zoon_search

import os
import pandas as pd
import sys
import numpy as np
import json
from params import Params
import datetime
from string import Template

class LoadData:
    def __init__(self, params: Params) -> None:
        self.params = params


        self.select_best_zoon_search = select_best_zoon_search.SelectBestZoonSearch(self.params)
        self.select_best_trip_search = select_best_trip_search.SelectBestTripSearch(self.params)
        self.load_trip_details = load_trip_details.LoadTripDetails(self.params)
        self.load_trip_search = load_trip_search.LoadTripSearch(self.params)
        self.load_zoon_details = load_zoon_details.LoadZoonDetails(self.params)
        self.load_zoon_search = load_zoon_search.LoadZoonSearch(self.params)


        self.config_logging()

        self.columns_ya_for_zoon_search = [
            'ignor_load', 'is_fix', 'is_map', 'location_nm_rus', 'source_id', 'transaction_info', 'transaction_info_new','transaction_info_norm', 
            'v_zoon_id', 'ya_status', 'ya_address_n', 'ya_cnt_category_match', 'ya_company_name', 'ya_company_name_norm', 'ya_id', 
            'ya_is_match_address', 'ya_point', 'url_zoon', 'z_query'
        ]
        self.columns_ya_for_trip_search = [
            'ignor_load', 'is_fix', 'is_map', 'location_nm_rus', 'source_id', 'transaction_info', 'transaction_info_new','transaction_info_norm', 
            'v_ta_id', 'ya_status', 'ya_address_n', 'ya_cnt_category_match', 'ya_company_name', 'ya_company_name_norm', 
            'ya_id', 'ya_is_match_address', 'ya_point', 'url_ta', 'ta_query'
        ]

    def config_logging(self):
        self.params.logs_path = Template(self.params.logs_path).substitute({
            'date_now':f'{datetime.datetime.now():%Y%m%d}' #format yyyymmdd
        })
        folder,file_name = os.path.split(self.params.logs_path)

        if not os.path.isdir(folder):
            os.makedirs(folder)
            print(f'created dir - {folder}')

        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s\t%(filename)s\t%(funcName)s\t[%(levelname)s]\t%(lineno)d\t%(message)s",
            handlers=[
                logging.FileHandler(self.params.logs_path, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )


    def get_or_action(self, path_file:str, action, *args):
        _,ext = os.path.splitext(path_file)
        if common.isfile(path_file):
            if ext == '.pik':
                return pd.read_pickle(path_file)
            elif ext == '.hd':
                return pd.read_hdf(path_file,'DATA')
            elif ext == '.xlsx':
                return pd.read_excel(path_file)
            elif ext == '.parquet':
                return pd.read_parquet(path_file)
            else:
                raise(Exception(f'not support extention {ext}'))
        #print(type(args))
        df = action(*args)
        if ext == '.pik':
            df.to_pickle(path_file)
        elif ext == '.parquet':
            df.to_parquet(path_file)
        elif ext == '.xlsx':
            df.to_excel(path_file,index=False)
        elif ext == '.hd':
            df.to_hdf(path_file,'DATA')
        else:
            raise(Exception(f'not support extention {ext}'))
        return df
    
    def start_load(self):
        '''Глобальный перехват ошибок, перехватываются все ошибки, логируются и вызывается raise с той же ошибкой
        '''
        try:
            self.__start_load__()
        except BaseException as ex:
            logging.error(ex)
            raise ex
    
    def __start_load__(self):
        start_all = time.time()
        if self.params.is_replace_file:
            for path in [
                self.params.temp_zoon_search_file,
                self.params.temp_trip_search_file,
                self.params.temp_select_best_zoon_search_file,
                self.params.temp_select_best_trip_search_file,
                self.params.zoon_details_file,
                self.params.trip_details_file,
            ]:
                if common.isfile(path):
                    os.remove(path)

        df_yandex_data = pd.read_parquet(self.params.yandex_data_file)
        df_yandex_data['transaction_info_norm'] = df_yandex_data['transaction_info_new'].apply(common.normalize_company_name)
        df_yandex_data['ya_company_name_norm'] = df_yandex_data['ya_company_name_norm'].apply(common.normalize_company_name)
        df_yandex_data['z_query'] = ''
        df_yandex_data['ta_query'] = ''
        
        logging.debug(f'get df_yandex_data table {df_yandex_data.shape=}')

        control_count = df_yandex_data['source_id'].nunique()

        df_zoon_search = self.get_or_action(self.params.temp_zoon_search_file,
                                             self.load_zoon_search.start,
                                             df_yandex_data[self.columns_ya_for_zoon_search])

        df_selected = self.get_or_action(self.params.temp_select_best_zoon_search_file,
                                             self.select_best_zoon_search.start,
                                             df_zoon_search)

        df_zoon_details = self.get_or_action(self.params.zoon_details_file,
                                             self.load_zoon_details.start,
                                             df_selected)

        if self.params.load_from_trip:
            df_trip_search = self.get_or_action(self.params.temp_trip_search_file,
                                             self.load_trip_search.start,
                                             df_yandex_data[self.columns_ya_for_trip_search])

            df_selected = self.get_or_action(self.params.temp_select_best_trip_search_file,
                                                self.select_best_trip_search.start,
                                                df_trip_search)
            
            df_trip_details = self.get_or_action(self.params.trip_details_file,
                                                self.load_trip_details.start,
                                                df_selected)

        logging.debug(f'DONE')

        end_all = time.time()
        logging.info(f'all time - {end_all - start_all}')

if __name__ == '__main__':
    print(sys.argv)
    param = Params()
    with open('params.json','r',encoding='UTF-8') as f:
        param = json.load(f, object_hook=lambda d: Params(**d))
        print(type(param))
    
    if len(sys.argv) == 1:
        param.is_replace_file = False
    else:
        param.is_replace_file = True if sys.argv[1] == '1' else False
    ld = LoadData(param)
    
    ld.start_load()
