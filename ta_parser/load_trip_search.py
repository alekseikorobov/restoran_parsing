
import pandas as pd
import os
import numpy as np
import ta_parser.load_data as lbyd
import common.dict_city as dict_city
import common.my_language_ru_pack as my_language_ru_pack
import importlib
importlib.reload(lbyd)
from tqdm import tqdm
from geopy.distance import geodesic as GD 
import common.common as common
importlib.reload(common)
import logging
import json
import glob
from params import Params

class LoadTripSearch:
    def __init__(self, params: Params) -> None:
        self.max_error = 3
        self.curr_error = 0
        self.params = params

    def revert_address(self, text):
        if text == '': return ''
        if text is None: return None
        if str(text) == str(np.nan): return text

        return ','.join(text.split(',')[::-1])

    def parse_search_data(self, df_process):
        json_list_result = []
        for i, row in tqdm(df_process.iterrows(), total=df_process.shape[0]):

            if row['ya_status'] in ['not_match_a','not_match_cat','not_match_n05','not_match_other']:
                row['ta_status'] = 'ya_not_match'
                json_list_result.append(row)
                continue
            if row['ya_is_match_address'] == False:
                row['ta_status'] = 'ya_not_match'
                json_list_result.append(row)
                continue
            if row['ya_cnt_category_match'] == 0:
                row['ta_status'] = 'ya_not_match'
                json_list_result.append(row)
                continue

            address = row['ya_address_n']

            if str(address) == str(np.nan) or address == '' or address is None:
                row['ta_status'] = 'ya_not_address'
                json_list_result.append(row)
                continue
            
            if 'url_ta' in row:
                url_ta = row['url_ta']
                if not (str(url_ta) == str(np.nan) or url_ta == '' or url_ta is None):
                    row['ta_link'] = url_ta
                    row['ta_status'] = 'new_by_fix'
                    json_list_result.append(row)
                    continue

            city_name = row['location_nm_rus']
            city_line = dict_city.get_line_by_city_name(city_name, self.params.city_list)

            query = lbyd.get_trip_query(city_name, row['ya_company_name']) 
            row['ta_query'] = lbyd.get_trip_query_pretty(query)
            full_name_param = lbyd.get_full_name_by_query_json(self.params.cache_data_folder, city_line.city, query, page_offset=0)
            row['ta_path_source'] = full_name_param
            if not common.isfile(full_name_param):
                try:
                    lbyd.save_json_by_search_page(base_folder, city_line.city, query,timeout=self.params.timeout_load_trip_search,proxy=self.params.proxy)
                    self.curr_error = 0
                except Exception as ex:
                    self.curr_error += 1
                    logging.error(f'{self.curr_error=}, {full_name_param=}', exc_info=True)
                    if self.curr_error > self.max_error:
                        raise(Exception('break load from trip! more error!'))

            full_name_list = full_name_param.replace('.json','*.json')
            #print(f'{full_name=}')
            row['ta_status'] = 'new'

            files = glob.glob(full_name_list)

            if len(files) > 0:
                obj_orgs = []
                try:
                    for full_name in files:
                        with open(full_name,'r',encoding='utf-8') as f:
                            obj_orgs.extend(json.load(f))
                    #logging.debug(f'{len(obj_orgs)=}')
                    if len(obj_orgs) == 0:
                        row['ta_status']  = 'not_data'
                        json_list_result.append(row)
                    else:
                        for res_obj in obj_orgs:
                            #res_obj = get_best_from_result(row, obj_orgs)
                            for key in res_obj:
                                new_key = key
                                if not new_key.startswith('ta_'):
                                    new_key = 'ta_' + new_key
                                row[new_key] = res_obj[key]

                            row['ta_location_id'] = int(row['ta_location_id'])
                            row['ta_address'] = self.revert_address(row['ta_address'])
                            row['ta_address_n'] = common.replace_address_by_city(row['location_nm_rus'], row['ta_address'], self.params.city_list,self.params.list_replace_stop_word_adress)
                            json_list_result.append(row.copy())

                except Exception as ex:
                    print(ex)
                    row['ta_status']  = f'error_{str(ex)}'
            else:
                row['ta_status']  = 'not_found_file'
                json_list_result.append(row)

        df_result = pd.DataFrame(json_list_result)
        return df_result

    def start(self, df:pd.DataFrame) -> pd.DataFrame:
        logging.debug('start match trip search and yandex data')
 
        logging.info(f"{df.shape=}")

        logging.debug(f'get {df.shape=}')

        df_result = self.parse_search_data(df)

        logging.debug(f"{df_result['ta_status'].value_counts()=}")

        logging.info(f'{df_result.shape=}')

        logging.debug(f"{df_result['source_id'].nunique()=}")

        return df_result

