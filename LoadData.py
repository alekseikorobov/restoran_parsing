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
from dataclasses import dataclass
import os
import pandas as pd
import sys
import numpy as np


@dataclass
class Params:
    
    #входной фал для поиска
    yandex_data_file: str = 'tables\\tran_yandex_data.xlsx'
    temp_zoon_search_file: str = 'tables\\zoon_search.hd'
    temp_select_best_zoon_search_file: str = 'tables\\zoon_select_best.hd'
    zoon_details_file: str = 'tables\\zoon_details.xlsx'
    trip_search_file: str = 'tables\\trip_search.hd'
    temp_select_best_trip_search_file: str = 'tables\\trip_select_best.hd'
    trip_details_file: str = 'tables\\trip_details.xlsx'
    validate_map_rest_file: str = 'dict\\validate_map_rest.xlsx'
    
    all_trip_search_file: str = 'tables\\all_trip_search.hd'
    all_trip_details_file: str = 'tables\\all_trip_details.hd'
    all_zoon_details_file: str = 'tables\\all_zoon_details.hd'
    all_zoon_search_file: str = 'tables\\all_zoon_search.hd'
    using_all_db = True

    logs_path: str = 'logs/all_logs_20240124.log'
    
    # перезаписать json деталей из html по zoon (если были правки парсинга в zoon_parser\parse_data.py, методе get_details_json)
    zoon_details_replace_json = False


class LoadData:
    def __init__(self, params: Params) -> None:
        self.params = params
        self.config_logging()

        self.all_source = {
            'df_zoon_all_search': pd.DataFrame(columns=['z_query','z_source_url_n']),
            'df_trip_all_search': pd.DataFrame(columns=['ta_query']),
            'df_trip_all_details': pd.DataFrame(columns=['ta_location_id','ta_cuisine']),
            'df_zoon_all_details': pd.DataFrame(columns=['z_id','z_source_url_n']),
        }
        self.all_source_file = {
            'df_zoon_all_search': self.params.all_zoon_search_file,
            'df_trip_all_search': self.params.all_trip_search_file,
            'df_trip_all_details': self.params.all_trip_details_file,
            'df_zoon_all_details': self.params.all_zoon_details_file,
        }

        for key_file in self.all_source_file:
            if os.path.isfile(self.all_source_file[key_file]):
                self.all_source[key_file] = pd.read_hdf(self.all_source_file[key_file], 'DATA')

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

        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s\t%(filename)s\t%(funcName)s\t[%(levelname)s]\t%(lineno)d\t%(message)s",
            handlers=[
                logging.FileHandler(self.params.logs_path, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

    def verify_df_valid(self, df_valid):
        df_valid['v_ta_id'] = df_valid['v_ta_id'].apply(np.round).astype('Int64')
        df_valid_d = df_valid[df_valid[['city_nm', 'restaurant_nm']].duplicated()]
        if len(df_valid_d) > 0:
            message = f'Excists dublicate! {df_valid_d[["city_nm","restaurant_nm"]]}'
            raise (Exception(message))

    def save_to_df_source(self, df_trip_search: pd.DataFrame, key_source: str, check_duble_field=None):
        df_all = pd.concat(
            [df_trip_search, self.all_source[key_source]], ignore_index=True)
        if check_duble_field is not None:
            v = df_all[check_duble_field].value_counts()
            if len(v[v > 1]) > 0:
                columns = df_all.columns
                for i, row in df_all[df_all[check_duble_field].isin(v[v > 1].index)].head(10).sort_values(check_duble_field).iterrows():
                    vals = ', '.join([str(row[col])[0:50] for col in columns])
                    logging.warning(f'{i}, {vals}')
                ls = v[v > 1].index
                raise (
                    Exception(f'Exists duplicate by filed {check_duble_field} values - {ls}'))
        df_all.to_hdf(self.all_source_file[key_source], 'DATA')
        logging.debug(f'save to {self.all_source_file[key_source]}')

    def get_from_df_source(self, df_left: pd.DataFrame, key_source: str, on=['source_id', 'ya_id'], use_validate=False) -> pd.DataFrame:
        '''
        получение данных из общей базы по указанному источнику, результат долежен быть такой: 
        слева (df_left) список новых записей на получение данных
        справа список всех записей за всё время
        выбираются соответствующие записи для каждой левой строчки из правой таблицы.
        то что не найдено, пойдет на обработку для получения из внешних исчточник
        то что найдено, обогащаются пустые поля из левой таблицы

        в базе источника по заданному ключу если это id, тогда должна быть только одна запись,
        для такой валидации поставлен параметр validate='many_to_one'
        '''
        validate = 'many_to_one' if use_validate else 'many_to_many'
        df_source = self.all_source[key_source]

        for on_item in on:
            if on_item not in df_source.columns:
                print(df_source.columns)
                raise (Exception(f'not exists column {on_item} in df_source'))
            if on_item not in df_left.columns:
                raise (Exception(f'not exists column {on_item} in df_left'))

        df_res = df_left.merge(df_source, how='left', on=on, suffixes=(
            None, '____y'), indicator=True, validate=validate)
        double_cols = [col for col in df_res.columns if '____y' in col]
        for col in double_cols:
            col_old = col.replace('____y', '')
            df_res[col_old].fillna(df_res[col], inplace=True)
        df_res.drop(columns=double_cols, inplace=True)
        return df_res.drop_duplicates()

    def get_df_trip_details_by_db(self, df_selected: pd.DataFrame):
        df_trip_details_old = self.get_from_df_source(df_selected, 'df_trip_all_details', on=['ta_location_id'], use_validate=True)
        logging.debug(f'{df_trip_details_old.shape=}')
        df_to_load = df_trip_details_old[df_trip_details_old['_merge']== 'left_only']
        df_to_load.drop(columns='_merge', inplace=True)
        df_all_not_match = df_to_load[(df_to_load['ta_status_m'] == 'all_not_match')
                                      | ~(df_to_load['ta_status'].isin(['new']))]

        df_to_load = df_to_load[~df_to_load.index.isin(df_all_not_match.index)]

        logging.debug(f'{df_to_load.shape=}')
        df_trip_details_new = pd.DataFrame()
        if len(df_to_load) > 0:
            df_trip_details_new = load_trip_details.start(df_to_load)
            cols = [
                'ta_similarity_title_with_tran2', 'ta_similarity_title_with_tran', 'ta_similarity_title2', 'ta_similarity_title', 
                'ta_similarity_address', 'ta_status', 'ta_status_m', 'ta_name_n', 'ta_query', 'ta_path_source'
            ]

            all_ta_field = [col for col in df_trip_details_new.columns if col.startswith('ta_') and col not in cols]
            logging.debug(df_trip_details_new['ta_status_m'].value_counts())
            logging.debug(df_trip_details_new['ta_status'].value_counts())
            logging.debug((df_trip_details_new['ta_status'] + '_' + df_trip_details_new['ta_status_m']).value_counts())
            # сохраняем только те записи, которые точно были скачены
            df_to_save = df_trip_details_new[(df_trip_details_new['ta_status_m'] != 'all_not_match')
                                             & (df_trip_details_new['ta_status'].isin(['new']))][all_ta_field].drop_duplicates()
            logging.debug(f'{df_to_save.shape=}')
            self.save_to_df_source(df_to_save, 'df_trip_all_details', check_duble_field='ta_location_id')

        df_trip_details = pd.concat([df_trip_details_old[df_trip_details_old['_merge'] == 'both'], df_trip_details_new, df_all_not_match])
        df_trip_details.drop(columns='_merge', inplace=True)
        logging.debug(f'{df_trip_details.shape=}')
        logging.debug(f'{df_trip_details["source_id"].nunique()=}')
        return df_trip_details

    def get_df_zoon_details_by_db(self, df_selected: pd.DataFrame, control_count: int, zoon_details_replace_json):
        # выяснилось что в качестве ключа использовать z_id использовать нельзя, так как есть дубликаты
        # поэтому в качестве уникального ключа используем ссылку on=['z_source_url']

        df_zoon_details_old = self.get_from_df_source(df_selected, 'df_zoon_all_details', on=['z_source_url_n'], use_validate=True)
        
        logging.debug(f'{df_zoon_details_old.shape=}')

        df_to_load = df_zoon_details_old[df_zoon_details_old['_merge'] == 'left_only']
        df_to_load.drop(columns='_merge', inplace=True)
        df_all_not_match = df_to_load[(df_to_load['z_status'].isin(['empty']))
                                      | (df_to_load['z_source_url'].isna())
                                      | (df_to_load['ignor_load'] == 'ZOON')
                                      ]
        df_to_load = df_to_load[~df_to_load.index.isin(df_all_not_match.index)]

        logging.debug(f'{df_to_load.shape=}')
        df_zoon_details_new = pd.DataFrame()
        if len(df_to_load) > 0:
            df_zoon_details_new = load_zoon_details.start(df_to_load, control_count, replace_json=zoon_details_replace_json, is_debug_log=False)
            # print(f'{df_zoon_details_new.columns=}')
            cols_to_save = [
                'z_name',
                'z_type_organization', 'z_kitchens', 'z_all_param', 'z_address_2',
                'z_hours',
                'z_price',
                'z_url',
                'z_id', 'z_source_path',
                'z_source_url',
                'z_source_url_n',
                'z_rating_value_2',
                'z_phone_2',
            ]
            # сохраняем только те записи, которые точно были скачены
            condition = (df_zoon_details_new['z_status'].isin(['empty'])) \
                | (df_zoon_details_new['z_source_url'].isna())\
                | (df_zoon_details_new['ignor_load'] == 'ZOON')
            df_to_save = df_zoon_details_new[~condition][cols_to_save].drop_duplicates()
            logging.debug(f'{df_to_save.shape=}')
            self.save_to_df_source(df_to_save, 'df_zoon_all_details', check_duble_field='z_source_url_n')
        df_zoon_details = pd.concat([df_zoon_details_old[df_zoon_details_old['_merge'] == 'both'], df_zoon_details_new, df_all_not_match])
        df_zoon_details.drop(columns='_merge', inplace=True)
        logging.debug(f'{df_zoon_details.shape=}')
        logging.debug(f'{df_zoon_details["source_id"].nunique()=}')
        return df_zoon_details

    def add_info_for_source(self, df_source: pd.DataFrame):
        df_source['transaction_info_new'] = df_source['transaction_info'].apply(common.normalize_transaction_name)
        return df_source

    def get_df_trip_search_by_db(self, df_yandex_data: pd.DataFrame):
        df_yandex_data['ta_query'] = df_yandex_data.apply(lambda row: ta_load_data.get_trip_query_pretty(
            ta_load_data.get_trip_query(row['location_nm_rus'], row['ya_company_name'])), axis=1)

        df_by_url = df_yandex_data[self.columns_ya_for_trip_search][df_yandex_data['url_ta'].notna()].drop_duplicates()
        if len(df_by_url) > 0:
            df_by_url['ta_status'] = 'new_by_fix'
            df_by_url['ta_link'] = df_by_url['url_ta']
            df_by_url['ta_location_id'] = df_by_url['ta_link'].apply(
                lambda url: ta_load_data.get_location_id_from_url(url))
            df_yandex_data = df_yandex_data[df_yandex_data['url_ta'].isna()]

        df_trip_search_old = self.get_from_df_source(
            df_yandex_data[self.columns_ya_for_trip_search], 'df_trip_all_search', on=['ta_query'])

        df_to_load = df_trip_search_old[df_trip_search_old['_merge']
                                        == 'left_only']
        df_to_load.drop(columns='_merge', inplace=True)

        is_not_ya_status = df_to_load['ya_status'].isin(
            ['not_match_a', 'not_match_cat', 'not_match_n05', 'not_match_other'])
        is_match_address = df_to_load['ya_is_match_address'] == False
        is_not_cnt_category_match = df_to_load['ya_cnt_category_match'] == 0
        # is_ya_not_address = df_to_load['ta_status'] == 'ya_not_address'
        # is_by_url_ta = df_to_load['url_ta'].notna()

        df_all_not_match = df_to_load[is_not_ya_status |
                                      is_match_address | is_not_cnt_category_match]
        df_all_not_match['ta_status'] = 'not_match'
        df_to_load = df_to_load[~df_to_load.index.isin(df_all_not_match.index)]
        logging.debug(f'{df_to_load.shape=}')
        df_trip_search_new = pd.DataFrame(columns=['source_id'])
        if len(df_to_load) > 0:
            columnWs_save = ['ta_location_id', 'ta_status', 'ta_name', 'ta_link',
                             'ta_type_org', 'ta_address', 'ta_address_n', 'ta_query']
            df_trip_search_new = load_trip_search.start(df_to_load)
            logging.debug(f'{df_trip_search_new.shape=}')
            self.save_to_df_source(
                df_trip_search_new[columnWs_save].drop_duplicates(), 'df_trip_all_search')
        df_trip_search = pd.concat([df_trip_search_old[df_trip_search_old['_merge']
                                   == 'both'], df_trip_search_new, df_all_not_match, df_by_url])
        df_trip_search.drop(columns='_merge', inplace=True)
        logging.debug(
            f'{df_trip_search.shape=}, {df_trip_search["source_id"].nunique()=}')
        return df_trip_search

    def get_df_zoon_search_by_db(self, df_yandex_data: pd.DataFrame):
        '''оптимизация для получения данных из zoon, если есть общий файл всего скаченного, то выбирается только то что нужно скачать 
        '''
        df_yandex_data['z_query'] = df_yandex_data.apply(
            lambda row: load_zoon_search.get_z_query(row['location_nm_rus'], row['ya_point']), axis=1)
        df_by_url = df_yandex_data[self.columns_ya_for_zoon_search][df_yandex_data['url_zoon'].notna()].drop_duplicates()
        if len(df_by_url) > 0:
            df_by_url['z_status'] = 'new_by_fix'
            df_by_url['z_source_url'] = df_by_url['url_zoon']
            df_by_url['z_source_url_n'] = df_by_url.apply(
                lambda row: common.normalize_z_source_url(row['z_source_url']), axis=1)
            df_yandex_data = df_yandex_data[df_yandex_data['url_zoon'].isna(
            )]

        df_zoon_search_old = self.get_from_df_source(
            df_yandex_data[self.columns_ya_for_zoon_search], 'df_zoon_all_search', on=['z_query'])
        logging.debug(f'{df_zoon_search_old.shape=}')

        df_to_load = df_zoon_search_old[df_zoon_search_old['_merge']== 'left_only']

        df_to_load.drop(columns='_merge', inplace=True)

        is_not_ya_status = df_to_load['ya_status'].isin(
            ['not_match_a', 'not_match_cat', 'not_match_n05', 'not_match_other'])
        is_match_address = df_to_load['ya_is_match_address'] == False
        is_not_cnt_category_match = df_to_load['ya_cnt_category_match'] == 0
        is_ignor_load = df_to_load['ignor_load'] == 'ZOON'
        df_all_not_match = df_to_load[is_not_ya_status |
                                      is_match_address | is_not_cnt_category_match | is_ignor_load]
        df_all_not_match['z_status'] = 'empty'

        df_to_load = df_to_load[~df_to_load.index.isin(df_all_not_match.index)]

        logging.debug(f'{df_to_load.shape=}')
        df_zoon_search_new = pd.DataFrame()
        if len(df_to_load) > 0:
            columns_save = ['z_status', 'z_title', 'z_source_url', 'z_source_url_n', 'z_lon',
                            'z_lat', 'z_id', 'z_object_id', 'z_ev_label', 'z_features',
                            'z_rating_value', 'z_worktimes', 'z_address', 'z_phone',
                            'z_path_source', 'z_address_n', 'z_count_search', 'z_dist', 'z_query']
            df_zoon_search_new = load_zoon_search.start(df_to_load)
            logging.debug(f'{df_zoon_search_new.shape=}')
            self.save_to_df_source(
                df_zoon_search_new[columns_save].drop_duplicates(), 'df_zoon_all_search')
        df_zoon_search = pd.concat([df_zoon_search_old[df_zoon_search_old['_merge']
                                   == 'both'], df_zoon_search_new, df_all_not_match, df_by_url])
        df_zoon_search.drop(columns='_merge', inplace=True)
        logging.debug(
            f'{df_zoon_search.shape=}, {df_zoon_search["source_id"].nunique()=}, {df_zoon_search[["ya_id","source_id"]].drop_duplicates().shape=}')

        logging.debug(
            f'{df_zoon_search["z_status"].value_counts(dropna=False)}')
        return df_zoon_search

    def add_info_for_zoon_details(self, df_zoon_details):
        df_zoon_details['z_company_name_norm'] = df_zoon_details.apply(
            lambda row: common.normalize_company_name(common.zoon_name_fix(row['z_name']), not row['is_map']), axis=1)
        df_zoon_details['z_similarity_name_n'] = df_zoon_details.apply(
            lambda row: common.str_similarity(row['ya_company_name_norm'], row['z_company_name_norm']), axis=1)
        df_zoon_details['z_similarity_name_n_2'] = df_zoon_details.apply(
            lambda row: common.str_similarity2(row['ya_company_name_norm'], row['z_company_name_norm']), axis=1)
        return df_zoon_details

    def start_load(self, is_replace_file=False):
        # описание размерности (на вход) [записей, полей] -> (на выход) [записей, полей]

        start_all = time.time()
        if is_replace_file:
            for path in [
                self.params.temp_zoon_search_file,
                self.params.temp_select_best_zoon_search_file,
                self.params.zoon_details_file,
                self.params.trip_search_file,
                self.params.temp_select_best_trip_search_file,
                self.params.trip_details_file,
            ]:
                if os.path.isfile(path):
                    os.remove(path)

        df_valid = pd.read_excel(self.params.validate_map_rest_file, sheet_name='Sheet1')
        logging.debug(f'get validate table {df_valid.shape=}')
        self.verify_df_valid(df_valid)

        
        df_yandex_data = None
        df_zoon_search = None
        df_trip_search = None
        

        is_delete_temp_file = False

        #df_yandex_data = pd.read_hdf(self.params.yandex_data_file, 'DATA')
        df_yandex_data = pd.read_excel(self.params.yandex_data_file)
        df_yandex_data['transaction_info_norm'] = df_yandex_data['transaction_info_new'].apply(common.normalize_company_name)
        df_yandex_data['ya_company_name_norm'] = df_yandex_data['ya_company_name_norm'].apply(common.normalize_company_name)
        logging.debug(f'get df_yandex_data table {df_yandex_data.shape=}')

        control_count = df_yandex_data['source_id'].nunique()

        if os.path.isfile(self.params.temp_zoon_search_file):
            df_zoon_search = pd.read_hdf(self.params.temp_zoon_search_file, 'DATA')

        if not os.path.isfile(self.params.zoon_details_file):
            if not os.path.isfile(self.params.temp_zoon_search_file):
                start = time.time()

                if self.params.using_all_db:
                    df_zoon_search = self.get_df_zoon_search_by_db(df_yandex_data)
                else:
                    df_yandex_data['z_query'] = ''
                    df_zoon_search = load_zoon_search.start(df_yandex_data[self.columns_ya_for_zoon_search])
                df_zoon_search.to_hdf(self.params.temp_zoon_search_file, 'DATA')
                end = time.time()
                logging.info(f'load_zoon_search - {end - start}')

            start = time.time()

            df_selected = None
            if os.path.isfile(self.params.temp_select_best_zoon_search_file):
                df_selected = pd.read_hdf(self.params.temp_select_best_zoon_search_file, 'DATA')
            else:
                df_selected = select_best_zoon_search.start(df_zoon_search, control_count)
                df_selected.to_hdf(self.params.temp_select_best_zoon_search_file, 'DATA')

            if type(df_selected) != pd.DataFrame:
                raise (Exception(f'df_selected is not df'))

            df_zoon_details = None
            if self.params.using_all_db:
                df_zoon_details = self.get_df_zoon_details_by_db(df_selected, control_count, self.params.zoon_details_replace_json)
            else:
                df_zoon_details = load_zoon_details.start(df_selected, control_count, self.params.zoon_details_replace_json)

            df_zoon_details = self.add_info_for_zoon_details(df_zoon_details)

            logging.debug(
                f'{df_zoon_details.shape=}, {df_zoon_details["source_id"].nunique()=}, {df_zoon_details[["ya_id","source_id"]].drop_duplicates().shape=}')
            df_zoon_details.to_excel(self.params.zoon_details_file,index=False)
            end = time.time()
            logging.info(f'load_zoon_details - {end - start}')

            if is_delete_temp_file:
                os.remove(self.params.temp_zoon_search_file)

        if not os.path.isfile(self.params.trip_search_file):
            start = time.time()
            if self.params.using_all_db:
                df_trip_search = self.get_df_trip_search_by_db(df_yandex_data)
            else:
                df_yandex_data['ta_query'] = ''
                df_trip_search = load_trip_search.start(df_yandex_data[self.columns_ya_for_trip_search])

            df_trip_search.to_hdf(self.params.trip_search_file, 'DATA')

            end = time.time()
            logging.info(f'load_trip_search - {end - start}')
        else:
            df_trip_search = pd.read_hdf(self.params.trip_search_file, 'DATA')


        if not os.path.isfile(self.params.trip_details_file):
            start = time.time()

            df_selected = None
            if os.path.isfile(self.params.temp_select_best_trip_search_file):
                df_selected = pd.read_hdf(self.params.temp_select_best_trip_search_file, 'DATA')
            else:
                df_selected = select_best_trip_search.start(df_trip_search)
                df_selected.to_hdf(self.params.temp_select_best_trip_search_file, 'DATA')
            
            df_trip_details = None
            if self.params.using_all_db:
                df_trip_details = self.get_df_trip_details_by_db(df_selected)
            else:
                df_trip_details = load_trip_details.start(df_selected)

            df_trip_details.to_excel(self.params.trip_details_file, index=False)
                    
            end = time.time()
            logging.info(f'load_trip_details - {end - start}')

        logging.debug(f'DONE')

        end_all = time.time()
        logging.info(f'all time - {end_all - start_all}')

if __name__ == '__main__':
    ld = LoadData(Params())
    print(sys.argv)
    if len(sys.argv) == 1:
        is_replace_file = False
    else:
        is_replace_file = True if sys.argv[1] == '1' else False
    print(f'{is_replace_file=}')
    ld.start_load(is_replace_file)
