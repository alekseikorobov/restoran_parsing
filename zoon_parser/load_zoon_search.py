import pandas as pd
import os
import numpy as np
import zoon_parser.load_data as lbyd
import common.dict_city as dict_city
import importlib
importlib.reload(lbyd)
from tqdm import tqdm
import zoon_parser.parse_data as parse_data
from geopy.distance import geodesic as GD 
import common.common as common
import logging
import json
from params import Params

base_folder = f'{os.path.abspath("")}/data/zoon'

class LoadZoonSearch:
    def __init__(self, params: Params) -> None:
        self.params = params


    #print(os.path.abspath(''))

    def get_normalization_list(self, array:list):
        
        min_dist = min(array)
        max_dist = max(array)
        delta = max_dist - min_dist
        if delta == 0:delta = 1

        for i in range(len(array)):
            array[i] = (array[i] - min_dist) / delta
        return array

    def get_standart_list(self, array:list):
        
        mean = np.mean(array)
        std = np.std(array)
        delta = std
        if std == 0: delta = 1

        for i in range(len(array)):
            array[i] = (array[i] - mean) / delta
        return array

    def replace_key(self, key:str):
        return (f'z_{key}' if not key.startswith('z_') else key).replace('zoon_url','source_url')



    def get_z_query(self, city_name,ya_point):
        
        if common.is_nan(ya_point): return ''

        city_line = dict_city.get_line_by_city_name(city_name, self.params.city_list)
        point = ya_point.split(',')
        zoom = 18
        return f"{city_line.city}_{zoom}_{point[1]}_{point[0]}"

    def parse_search_data(self, df_process):
        #is_cnt_category_match = df['ya_cnt_category_match'] > 0
        #is_match_address = (df['ya_is_match_address'] == True)
        #df_process = df[is_cnt_category_match & is_match_address & is_ya_status]
        json_list_result = []
        for i, row in tqdm(df_process.iterrows(), total=df_process.shape[0]):

            if row['ya_status'] in ['not_match_a','not_match_cat','not_match_n05','not_match_other']:
                row['z_status'] = 'empty'
                json_list_result.append(row)
                continue
            if row['ya_is_match_address'] == False:
                row['z_status'] = 'empty'
                json_list_result.append(row)
                continue
            if row['ya_cnt_category_match'] == 0:
                row['z_status'] = 'empty'
                json_list_result.append(row)
                continue
            if row['ignor_load'] == 'ZOON':
                row['z_status'] = 'ignore'
                json_list_result.append(row)
                continue
            
            url_zoon = row['url_zoon']
            if not (str(url_zoon) == str(np.nan) or url_zoon == '' or url_zoon is None):
                row['z_source_url'] = url_zoon
                row['z_source_url_n'] = common.normalize_z_source_url(row['z_source_url'])
                row['z_status'] = 'new_by_fix'
                json_list_result.append(row)
                continue
            else:
                row['z_source_url'] = None
                row['z_source_url_n'] = None
            
            city_name = row['location_nm_rus']
            city_line = dict_city.get_line_by_city_name(city_name, self.params.city_list)
            
            point = row['ya_point'].split(',')
            zoom=18
            row['z_query'] = self.get_z_query(row['location_nm_rus'],row['ya_point'])
            page_name = f'{zoom}_{point[1]}_{point[0]}.json'
            path = common.get_folder(base_folder, city_line.city,'search_p_json',None)
            full_name = f'{path}/{page_name}'

            l2_ya, l1_ya = map(float,row['ya_point'].split(','))

            if not common.isfile(full_name):
                lbyd.save_json_by_search_page(city_line,(l1_ya,l2_ya), replace=False,timeout=self.params.timeout_load_zoon_search)

            with open(full_name,'r',encoding='utf-8') as f:
                json_result_list = json.load(f)
                json_result_list = [
                    {self.replace_key(key):item[key] for key in item } 
                    for item in json_result_list
                ]
            row['z_path_source'] = full_name
            if len(json_result_list) == 0:
                row['z_status'] = 'empty'
                json_list_result.append(row)
            else:
                for json_result_item in json_result_list:
                    row['z_status'] = 'new'
                    for key in json_result_item:
                        if key == 'z_path_source': continue
                        row[key] = json_result_item[key]

                    row['z_address_n'] = common.replace_address_by_city(row['location_nm_rus'], row['z_address'], self.params.city_list,self.params.list_replace_stop_word_adress)
                    row['z_count_search'] = len(json_result_list)

                    row['z_dist'] = None
                    if row['z_lat'] != '':
                        #print(line['z_lat'],line['z_lon'])
                        l1_z,l2_z = float(row['z_lat']),float(row['z_lon'])
                        m = GD((l1_z,l2_z), (l1_ya,l2_ya)).m
                        row['z_dist'] = m

                    json_list_result.append(row.copy())

        df_result = pd.DataFrame(json_list_result)
        return df_result

    def start(self, df:pd.DataFrame)->pd.DataFrame:
        logging.debug('start match zoon search and yandex data')
        logging.info(f'get {df.shape=}')
        df_result = self.parse_search_data(df)
        logging.debug(f'{df_result["z_status"].value_counts()=}')
        logging.info(f'resutl {df_result.shape=}')
        #df_result.to_excel(to_path, index=False)
        #logging.debug(f'saved to {to_path=}')
        return df_result


if __name__ == "__main__":
    #start()
    pass
