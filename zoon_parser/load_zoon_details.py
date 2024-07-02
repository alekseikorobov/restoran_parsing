import pandas as pd
import os
import zoon_parser.load_data as load_data
import zoon_parser.parse_data as parse_data
import common.dict_city as dict_city
import logging
# import importlib
# importlib.reload(load_data)
# importlib.reload(parse_data)
from tqdm import tqdm
import common.common as common
import numpy as np

tqdm.pandas()


def update_all(row):
    if row['z_status'] == 'empty':
        return row

    city_name = row['location_nm_rus']
    city_line = dict_city.get_line_by_city_name(city_name)
    #print(f'{city_line=}')

    z_source_url = row['z_source_url']
    l_replace_json = _replace_json
    if row['ignor_load'] == 'ZOON':
        z_source_url = row['url_zoon']
        #l_replace_json = True #TODO: временно, только для того чтобы пересчитать id

    if common.is_nan(z_source_url):
        row['z_status'] = 'empty'
        return row

    load_data.load_page_if_not_exists(city_line['city'] ,z_source_url)
    new_row = parse_data.get_details_json(city_line['city'],z_source_url, replace = l_replace_json,is_debug_log=_is_debug_log)
    for key in new_row:
        row[key] = new_row[key]

    # z_id_new = row['z_id']
    # хотелось сделать проверку на соответствие ключа страницы поиска и деталей
    # но оказывается так делать бессмыслено 
    # так как на странице поиска по одной и той же ссылке могут быть два id o_O
    # if z_id_from_search is not None and z_id_from_search != '':
    #     if z_id_new is None or z_id_new == '':
    #         raise(Exception(f'cannot get ID from zoon page - {z_source_url}'))
    #     if z_id_from_search != z_id_new:
    #         raise(Exception(f'excepted ID {z_id_from_search} from search page different actual ID {z_id_new} from page {z_source_url},source json = {row["z_source_path"]}'))

    return row
_replace_json = False
_is_debug_log = False
def start(df_result:pd.DataFrame, control_count:int, replace_json = False, is_debug_log = False) -> pd.DataFrame:
    global _replace_json,_is_debug_log
    _replace_json = replace_json
    _is_debug_log = is_debug_log
    logging.debug(f'start {df_result.columns=}')

    df_result = df_result.progress_apply(update_all,axis=1)

    #df_result = pd.DataFrame(df_result)

    #так как теперь не всегда вызывается, поэтому приходится выносить на уровень выше
    # df_result['z_company_name_norm']  = df_result.apply(lambda row:common.normalize_company_name(common.zoon_name_fix(row['z_name']), not row['is_map']),axis=1)
    # df_result['z_similarity_name_n']  = df_result.apply(lambda row:common.str_similarity(row['ya_company_name_norm'],row['z_company_name_norm']),axis=1)
    # df_result['z_similarity_name_n_2']  = df_result.apply(lambda row:common.str_similarity2(row['ya_company_name_norm'],row['z_company_name_norm']),axis=1)

    #fact_count = df_result['source_id'].nunique()
    #assert fact_count == control_count, f'not correct count {fact_count} {control_count}'

    logging.info(f'{df_result.shape=}')
    return pd.DataFrame(df_result)