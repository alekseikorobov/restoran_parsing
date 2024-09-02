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
import ya_parser.load_ya_rating as load_ya_rating
import ya_parser.load_ya_features as load_ya_features
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

VERSION = '0.2.10'

#версия схемы упаковщика данных в json
#эта версия должна быть согласована с ДАГом, который разбирает данные
SCHEMA_VERSION = '0.2.10'

class LoadData:
    def __init__(self, params: Params,is_test=False) -> None:
        self.params = params


        self.select_best_zoon_search = select_best_zoon_search.SelectBestZoonSearch(self.params)
        self.select_best_trip_search = select_best_trip_search.SelectBestTripSearch(self.params)
        self.load_trip_details = load_trip_details.LoadTripDetails(self.params)
        self.load_trip_search = load_trip_search.LoadTripSearch(self.params)
        self.load_zoon_details = load_zoon_details.LoadZoonDetails(self.params)
        self.load_zoon_search = load_zoon_search.LoadZoonSearch(self.params)
        

        self.load_ya_rating = load_ya_rating.LoadYaRating(self.params)
        self.load_ya_features = load_ya_features.LoadYaFeatures(self.params)

        self.load_ya_image_params = load_ya_image_params.LoadYaImageParams(self.params)
        self.load_ya_image = load_ya_image.LoadYaImage(self.params)

        if not is_test:
            self.config_logging()

        self.columns_ya_for_zoon_search = [
            'ignor_load', 'is_fix', 'is_map', 'location_nm_rus', 'source_id', 'transaction_info','transaction_info_norm', 
            'v_zoon_id', 'ya_status', 'ya_address_n', 'ya_cnt_category_match', 'ya_company_name_norm', 'ya_id', 
            'ya_is_match_address', 'ya_point', 'url_zoon', 'z_query'
        ]
        self.columns_ya_for_trip_search = [
            'ignor_load', 'is_fix', 'is_map', 'location_nm_rus', 'source_id', 'transaction_info','transaction_info_norm', 
            'v_ta_id', 'ya_status', 'ya_address_n', 'ya_cnt_category_match', 'ya_company_name_norm', 
            'ya_id', 'ya_is_match_address', 'ya_point', 'url_ta', 'ta_query'
        ]

    def config_logging(self):
        folder,file_name = os.path.split(self.params.logs_path)

        if not os.path.isdir(folder):
            os.makedirs(folder)
            print(f'created dir - {folder}')
        
        if not isinstance(logging.getLevelName(self.params.log_level.upper()),int):
            raise(Exception(f'Not correct log level in param value - {self.params.log_level}'))

        logging.basicConfig(
            level=logging.getLevelName(self.params.log_level.upper()),
            format="%(asctime)s\t%(filename)s\t%(funcName)s\t[%(levelname)s]\t%(lineno)d\t%(message)s",
            handlers=[
                logging.FileHandler(self.params.logs_path, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

    def df_write(self, df, path_file):
        _,ext = os.path.splitext(path_file)
        if ext == '.pik':
            df.to_pickle(path_file)
        elif ext == '.parquet':
            df.to_parquet(path_file)
        elif ext == '.csv':
            df.to_csv(path_file,index=False)
        elif ext == '.xlsx':
            df.to_excel(path_file,index=False)
        elif ext == '.hd':
            df.to_hdf(path_file,'DATA')
        else:
            raise(Exception(f'not support extention {ext}'))

    def df_read(self, path_file):
        _,ext = os.path.splitext(path_file)
        df_result = None
        if ext == '.pik':
            df_result = pd.read_pickle(path_file)
        elif ext == '.hd':
            df_result = pd.read_hdf(path_file,'DATA')
        elif ext == '.xlsx':
            df_result = pd.read_excel(path_file,engine='openpyxl')
        elif ext == '.csv':
            df_result = pd.read_csv(path_file)
        elif ext == '.parquet':
            df_result = pd.read_parquet(path_file)
        else:
            raise(Exception(f'not support extention {ext} for file {path_file=}'))
        logging.debug(f'{df_result.shape=}, {df_result.columns=}, from file {path_file=}')
        return df_result

    def get_or_action(self, path_file:str, action, *args):
        
        df_input = args[0]
        if isinstance(df_input, pd.DataFrame):
            logging.debug(f'start {action.__self__.__class__}: {df_input.shape=} {df_input.columns=}')
        else:
            logging.debug(f'start {action.__self__.__class__}')

        if common.isfile(path_file):
            df_result = self.df_read(path_file)
            logging.debug(f'{df_result.shape=}, {df_result.columns=}, from file {path_file=}')
            return df_result

        #print(type(args))
        df = action(*args)
        self.df_write(df, path_file)
        logging.debug(f'{df.shape=}, {df.columns}, saved to {path_file=}')
        return df
    
    def start_load(self):
        '''Глобальный перехват ошибок, перехватываются все ошибки, логируются и вызывается raise с той же ошибкой
        '''
        try:
            self.__start_load__()
        except BaseException as ex:
            logging.error(ex)
            raise ex
    
    def get_ip(self, proxy = None):
        try:
            import requests
            res = requests.get('https://ip.me/',verify=False,headers = {
            'content-type':'text/html; charset=UTF-8'
            }, proxies = {'http':proxy,'https':proxy}, timeout=60)
        except BaseException as ex:
            return 'ERROR'
        return res.text

    def check_request(self, url_for_check_request:str, proxy=None):
        try:
            logging.debug(f'Start check_request')
            import requests
            headers = {
                'content-type':'text/html; charset=UTF-8'
            }
            logging.debug(f'{url_for_check_request=}')
            logging.debug(f'{headers=}')
            logging.debug(f'{proxy=}')
            response = requests.get(url_for_check_request,verify=False,headers = headers, proxies = {'http':proxy,'https':proxy}, timeout=60)
            logging.debug(f'{response.headers=}')
            logging.debug(f'{response.text=}')
        except BaseException as ex:
            logging.error(f'ERROR',exc_info=True)

    def show_package(self):
        try:
            from pip._internal.operations import freeze
        except ImportError:
            from pip.operations import freeze
        
        pkgs = freeze.freeze()
        for pkg in pkgs:
            logging.debug(pkg)

    def __start_load__(self):
        
        self.show_package()

        logging.debug(f'Начало обработки')
        using_ip = self.get_ip(self.params.proxy)
        
        if using_ip == 'ERROR':
            logging.warn(f'ip.me with proxy {self.params.proxy} return {using_ip}')
        else:
            logging.debug(f'ip.me with proxy {self.params.proxy} return {using_ip}')


        if self.params.url_for_check_request is not None:
            self.check_request(self.params.url_for_check_request,self.params.proxy)

        start_all = time.time()

        if self.params.is_replace_file:
            for path in [
                self.params.temp_zoon_search_file,
                self.params.temp_trip_search_file,
                self.params.temp_select_best_zoon_search_file,
                self.params.temp_select_best_trip_search_file,
                self.params.zoon_details_file,
                self.params.trip_details_file,
                self.params.ya_image_params_file,
                self.params.ya_rating_file,
                self.params.ya_features_file,
                self.params.result_data_file,
            ]:
                if common.isfile(path):
                    os.remove(path)

        df_yandex_data = pd.read_parquet(self.params.yandex_data_file)
        df_yandex_data['transaction_info_norm'] = df_yandex_data['transaction_info'].apply(common.normalize_company_name)
        df_yandex_data['ya_company_name_norm'] = df_yandex_data['ya_company_name_norm'].apply(common.normalize_company_name)
        df_yandex_data['z_query'] = ''
        df_yandex_data['ta_query'] = ''
        
        logging.debug(f'get df_yandex_data table {df_yandex_data.shape=}')
        
        df_yandex_data['source_id'] = df_yandex_data.index
        control_count = df_yandex_data['source_id'].nunique()

        if self.params.load_from_zoon:
            logging.debug('Start load by zoon')
            df_zoon_search = self.get_or_action(self.params.temp_zoon_search_file,
                                                self.load_zoon_search.start,
                                                df_yandex_data[self.columns_ya_for_zoon_search])

            df_selected = self.get_or_action(self.params.temp_select_best_zoon_search_file,
                                                self.select_best_zoon_search.start,
                                                df_zoon_search)

            df_zoon_details = self.get_or_action(self.params.zoon_details_file,
                                                self.load_zoon_details.start,
                                                df_selected)
        else:
            logging.debug('Skip load by zoon')

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
        
        df_ya_rating = None
        if self.params.load_from_ya or self.params.load_images_from_ya:
            df_ya_rating = self.get_or_action(self.params.ya_rating_file, self.load_ya_rating.start, df_yandex_data)

        if self.params.load_from_ya:
            df_ya_features = self.get_or_action(self.params.ya_features_file, self.load_ya_features.start, df_ya_rating)
        
        if self.params.load_images_from_ya:
            df_ya_image_params = self.get_or_action(self.params.ya_image_params_file,
                                                self.load_ya_image_params.start,
                                                df_ya_rating)
            
            self.load_ya_image.start(df_ya_image_params)

        if self.params.is_packing_data:
            _ = self.get_or_action(self.params.result_data_file,
                                                self.packing_data_to_output,
                                                *(
                                                "ya_id,location_nm_rus,transaction_info", #key
                                                (self.params.yandex_data_file,"ya_id,location_nm_rus,transaction_info"), #input_file
                                                [
                                                    (self.params.ya_rating_file,"ya","ya_org_name,ya_stars_count,ya_rating,ya_link_org"),
                                                    (self.params.ya_features_file,"ya","ya_f_avg_price,ya_f_cuisine"),
                                                ] #output_files
                                                ))


        logging.debug(f'DONE')

        end_all = time.time()
        logging.info(f'all time - {end_all - start_all}')
    
    def packing_data_to_output(self,key,input_file,output_files):
        '''
        output_files - должен иметь формат:
        [
            (<output_file_path-путь к файлу>, <name_field-название корневого элемента>, <cols_str-колонки из исходго файла>)
        ]
        '''
        logging.debug(f'start pack, by {key=}, {input_file=}, {output_files=}')
        key_cols = key.split(',')
        input_file_path,cols_str = input_file
        input_cols = cols_str.split(',')
        df_input = self.df_read(input_file_path)[input_cols]

        logging.debug(f'{df_input.shape=}')
        df_result = df_input
        
        #проходимся по каждому источнику и собираем все поля в записи в json строку.
        for i,output_file in enumerate(output_files):
            output_file_path, name_field, cols_str = output_file
            result_field = f'data_{i}_{name_field}'
            output_cols = cols_str.split(',')
            
            df_output = self.df_read(output_file_path)[[*key_cols,*output_cols]]
            logging.debug(f'{df_output.shape=}')
            df_output_j = df_output[output_cols].to_json(orient='records')
            df_output[result_field] = [json.dumps(j,ensure_ascii=False) for j in json.loads(df_output_j)]
            
            #строки, которые повторяются по ключу, нужно объединить в один массив
            df_output = df_output.groupby(key_cols).apply(self.combine_lines_to_array_str,result_field).reset_index()

            #добавляем полученое json поле в результатирующий DataFrame
            df_result = df_result.merge(df_output[[*key_cols,result_field]],how='inner',on = key_cols)

        #теперь собираем по всем источникам в одни json
        df_result['data'] = df_result.apply(self.combine_json_fields, axis=1)
        
        df_result['schema_version'] = SCHEMA_VERSION
        df_result['update_dttm'] = datetime.datetime.now()
        
        return df_result[[*input_cols,'data','schema_version','update_dttm']]

    def combine_lines_to_array_str(self,row,field_name):
        compact_data = f"[{','.join(row[field_name])}]"
        return pd.Series(data={field_name:compact_data})

    def combine_json_fields(self, row):
        
        #выбираем все поля с data_
        field_data = [d for d in row.keys() if d.startswith('data_') ]
        result_data = {}
        for d_field in field_data:
            name_field = d_field.split('_')[-1]
            index_result = 0
            datas = json.loads(row[d_field])
            
            if name_field in result_data:
                for curr_index, data in enumerate(datas):
                    #если элемента в массиве не существут, тогда создаем новую ячейку,
                    #которую потом будем заполнять
                    if curr_index > len(result_data[name_field]):
                        result_data[name_field].append({})
                    
                    d = result_data[name_field][curr_index]
                    keys = set(d.keys())
                    keys_new = set(data.keys())
                    
                    keys_sec = keys.intersection(set(keys_new))
                    if any(keys_sec):
                        #множества пересекаются
                        logging.warn(f'key already exists in result - {keys_sec}')
                
                    result_data[name_field][curr_index].update(data)
            else:
                result_data[name_field] = datas
            index_result += 1
        
        
        return json.dumps(result_data, ensure_ascii=False)
        

import argparse
def get_arguments():
    parser = argparse.ArgumentParser(
                    prog='parsing restaurants',
                    description='',
                    epilog='')
    
    parser.add_argument('-b', '--base_path',help='Базовый путь для всех файлов, откуда забираются данные для парсинга и куда кладутся вспомогательные и выходные файлы. Если не указано, используйте base_path из params.json. ', default = None)
    parser.add_argument('-p', '--proxy', help='Прокси для всех http-запросов requests. См. proxy в params.json. По умолчанию None', default = None)
    parser.add_argument('-r', '--replace', help='если использовать этот флаг, то все файлы будут удалены перед запуском. По умолчанию false', default = False, action='store_true')
    parser.add_argument('-rr', '--replaceall', help='перезапись абслютно всего, включая зекешированные файлы. По умолчанию false', default = False, action='store_true')

    args = parser.parse_args()
    return args



if __name__ == '__main__':
    print(f'VERSION = {VERSION}')
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

    # if args.replaceall:
    #     param.is_replace_file = True
        
    param.is_ya_param_replace_json_request = args.replaceall
    param.is_ya_param_g_replace_json_request = args.replaceall
    param.is_ya_param_g_replace_html_request = args.replaceall
    param.is_ya_rating_replace_html_request = args.replaceall
    param.zoon_details_replace_json = args.replaceall
    param.is_zoon_search_replace_html_request = args.replaceall
    param.is_zoon_search_replace_json_request = args.replaceall
    
    print(f'{args=}')
    ld = LoadData(param)
    logging.info(f'VERSION = {VERSION}')
    logging.info(f'VERSION = {SCHEMA_VERSION}')
    ld.start_load()
