
import pandas as pd
import numpy as np
import os
import json
import ta_parser.load_data as load_data
import importlib
importlib.reload(load_data)
import common.dict_city as dict_city
from tqdm import tqdm
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
import logging
import datetime

from params import Params

class LoadTripDetails:
    def __init__(self, params: Params) -> None:
        self.params = params

    def replace_str(self,text):
        try:
            if type(text) != str or text is None or str(text) == str(np.nan): 
                return text
            return ILLEGAL_CHARACTERS_RE.sub(r'',text)
        except Exception as ex:
            print(text)
            raise(ex)
        
    def update_all(self,row):
        if row['ta_status'] not in ['new','new_by_fix']:
            return row
        if row['ta_status_m'] == 'all_not_match': return row

        if row['ta_status'] == 'new_by_fix':
            # если идем по фиксированной ссылке, то нужно получить location_id из этой страницы
            row['ta_location_id'] = load_data.get_location_id_from_url(row['ta_link'])

        location_id = row['ta_location_id']
        if location_id is None or str(location_id) == str(np.nan): return row

        city_name = row['location_nm_rus']
        city_line = dict_city.get_line_by_city_name(city_name, self.params.city_list)
        city = city_line.city
        full_name = load_data.get_full_name_by_details_json(self.params.cache_data_folder,city_line.city,location_id)
        if not common.isfile(full_name):
            full_url = f"https://www.tripadvisor.ru/{row['ta_link'].strip('/')}"
            load_data.get_html_details_and_parse(self.params.cache_data_folder, city, full_url, location_id,replace_json=False,timeout=self.params.timeout_load_trip_details,proxy=self.params.proxy)
        try:
            row_new = load_data.parse_page_details_from_json(full_name, int(location_id))
        except Exception as ex:
            logging.error(full_name + location_id,exc_info=True)
            raise(ex)

        for key in row_new:
            row[key] = row_new[key]
        return row

    def start(self, df_result:pd.DataFrame) -> pd.DataFrame:
        tqdm.pandas()
        logging.debug('start')
        logging.info(f'{df_result.shape=}')

        df_result = df_result.progress_apply(self.update_all,axis=1)

        df_result = pd.DataFrame(df_result)

        for col,typ in zip(df_result.columns, df_result.dtypes):
            if typ =='object':
                df_result[col] = df_result[col].apply(self.replace_str)

        df_result['actual_date'] = datetime.datetime.now()

        logging.info(f'{df_result.shape=}')

        return df_result
