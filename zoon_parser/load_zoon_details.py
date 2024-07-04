import pandas as pd
import os
import zoon_parser.load_data as load_data
import zoon_parser.parse_data as parse_data
import common.dict_city as dict_city
import logging
from tqdm import tqdm
import common.common as common
import numpy as np
from params import Params
import datetime

tqdm.pandas()

class LoadZoonDetails:
    def __init__(self, params: Params) -> None:
        self.params = params

    
    def get_page_name(self, full_url):
        page_name = ''
        if full_url[0] == '/':
            res = hashlib.sha1(full_url.encode())
            page_name = res.hexdigest()
            full_url = f'https://zoon.ru{full_url}'
        else:
            page_name = full_url.rstrip('/').split('/')[-1]

        if page_name == '':
            raise(Exception('can not define page name by url='+full_url))
        return page_name
    
    def update_all(self, row):
        if row['z_status'] == 'empty':
            return row

        city_name = row['location_nm_rus']
        city_line = dict_city.get_line_by_city_name(city_name, self.params.city_list)
        #print(f'{city_line=}')

        z_source_url = row['z_source_url']
        l_replace_json = self.params.zoon_details_replace_json
        if row['ignor_load'] == 'ZOON':
            z_source_url = row['url_zoon']
            #l_replace_json = True #TODO: временно, только для того чтобы пересчитать id

        if common.is_nan(z_source_url):
            row['z_status'] = 'empty'
            return row
        page_name = self.get_page_name(z_source_url)
        load_data.load_page_if_not_exists(self.params.cache_data_folder, page_name, city_line.city, z_source_url,timeout=self.params.timeout_load_zoon_details,proxy=self.params.proxy)

        new_row = parse_data.get_details_json(self.params.cache_data_folder, page_name, city_line.city, replace = l_replace_json, is_debug_log=self.params.zoon_details_debug_log)
        
        for key in new_row:
            row[key] = new_row[key]

        return row

    def add_info_for_zoon_details(self, df_zoon_details):
        df_zoon_details['z_company_name_norm'] = df_zoon_details.apply(
            lambda row: common.normalize_company_name(common.zoon_name_fix(row['z_name'],self.params.list_replace_type_names), not row['is_map']), axis=1)
        df_zoon_details['z_similarity_name_n'] = df_zoon_details.apply(
            lambda row: common.str_similarity(row['ya_company_name_norm'], row['z_company_name_norm']), axis=1)
        df_zoon_details['z_similarity_name_n_2'] = df_zoon_details.apply(
            lambda row: common.str_similarity2(row['ya_company_name_norm'], row['z_company_name_norm']), axis=1)

        df_zoon_details['actual_date'] = datetime.datetime.now()    
        return df_zoon_details

    def start(self, df_result:pd.DataFrame) -> pd.DataFrame:

        logging.debug(f'start {df_result.columns=}')

        df_result = df_result.progress_apply(self.update_all,axis=1)

        df_result = self.add_info_for_zoon_details(df_result)

        logging.debug(f'{df_result.shape=}, {df_result["source_id"].nunique()=}, {df_result[["ya_id","source_id"]].drop_duplicates().shape=}')
            
        logging.info(f'{df_result.shape=}')
        return pd.DataFrame(df_result)