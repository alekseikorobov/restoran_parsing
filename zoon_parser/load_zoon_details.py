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

tqdm.pandas()

class LoadZoonDetails:
    def __init__(self, params: Params) -> None:
        self.params = params

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

        load_data.load_page_if_not_exists(city_line.city ,z_source_url,timeout=self.params.timeout_load_zoon_details)
        new_row = parse_data.get_details_json(city_line.city,z_source_url, replace = l_replace_json, is_debug_log=self.params.zoon_details_debug_log)
        
        for key in new_row:
            row[key] = new_row[key]

        return row

    def start(self, df_result:pd.DataFrame) -> pd.DataFrame:

        logging.debug(f'start {df_result.columns=}')

        df_result = df_result.progress_apply(self.update_all,axis=1)

        logging.info(f'{df_result.shape=}')
        return pd.DataFrame(df_result)