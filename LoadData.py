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
import load_ya_image_params
import load_ya_image

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
        
        self.load_ya_image_params = load_ya_image_params.LoadYaImageParams(self.params)
        self.load_ya_image = load_ya_image.LoadYaImage(self.params)


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
        folder,file_name = os.path.split(self.params.logs_path)

        if not os.path.isdir(folder):
            os.makedirs(folder)
            print(f'created dir - {folder}')
        
        if self.params.log_level.upper() not in logging.getLevelNamesMapping():
            raise(Exception(f'Not correct log level in param value - {self.params.log_level}. Avaliable - {",".join(logging.getLevelNamesMapping().keys())}'))

        logging.basicConfig(
            level=logging.getLevelName(self.params.log_level.upper()),
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
                self.params.ya_image_params_file
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

        if self.params.load_from_zoon:
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

        if self.params.load_images_from_ya:
            df_ya_image_params = self.get_or_action(self.params.ya_image_params_file,
                                                self.load_ya_image_params.start,
                                                df_yandex_data)
            
            self.load_ya_image.start(df_ya_image_params)

        logging.debug(f'DONE')

        end_all = time.time()
        logging.info(f'all time - {end_all - start_all}')

import argparse
def get_arguments():
    parser = argparse.ArgumentParser(
                    prog='parsing restaurants',
                    description='',
                    epilog='')
    
    parser.add_argument('-b', '--base_path',help='Базовый путь для всех файлов, откуда забираются данные для парсинга и куда кладутся вспомогательные и выходные файлы. Если не указано, используйте base_path из params.json. ', default = None)
    parser.add_argument('-p', '--proxy', help='Прокси для всех http-запросов requests. См. proxy в params.json. По умолчанию None', default = None)
    parser.add_argument('-r', '--replace', help='если использовать этот флаг, то все файлы будут удалены перед запуском. По умолчанию false', default = False, action='store_true')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('WARNING','not override params. Start with default params')
    
    args = get_arguments()

    base_path = ''
    if args.base_path is not None:
        base_path = args.base_path
        if not os.path.isdir(base_path):
            raise(Exception(f'folder not exists by path {base_path}'))
    
    path_for_param = os.path.join(base_path,'params.json')
    if not os.path.isfile(path_for_param):
        raise(Exception(f'not found params.json by path = {path_for_param}'))
    
    print(f'{path_for_param=}')
    param = None
    with open(path_for_param,'r', encoding='UTF-8') as f:
        param = Params(**json.load(f))

    if args.proxy is not None:
        param.proxy = args.proxy
    if args.base_path is not None:
        param.base_path = args.base_path

    param.is_replace_file = args.replace
    
    print(f'{args=}')
    ld = LoadData(param)
    ld.start_load()
