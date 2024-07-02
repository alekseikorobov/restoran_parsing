

import os
import glob
from tqdm import tqdm
import pandas as pd
import json
import common.common as common
from geopy.distance import geodesic as GD 
import load_trip_search

def collect_all_file_to_one_db():
    df_all_trip_search = None #pd.read_hdf('tables/all_trip_search.hd','DATA')
    
    base_path1 = r'C:\work\map_api\data_ta\*\search_json\*.json'

    df_result = pd.DataFrame()
    json_list_result = []
    i = 0
    max_i = 10
    for full_name in tqdm(glob.glob(base_path1)):
        i+=1
        #if i > max_i: break
        #print(full_name)
        file_name = full_name.split('\\')[-1]
        city_code = full_name.split('\\')[-3]
        file_name_w_ex = file_name.replace('.json','')
        ta_query = ''
        if '_' in file_name_w_ex:
            ta_query = file_name_w_ex[0:file_name_w_ex.rfind('_')] # ta_query соответствует результату метода  get_trip_query_pretty
        else:
            ta_query = file_name_w_ex
        #z,l1,l2 = file_name_w_ex.split('_')
        #l1_ya, l2_ya = float(l1),float(l2)
        with open(full_name,'r',encoding='utf-8') as f:
            obj_orgs = json.load(f)
            if len(obj_orgs) == 0:
                row = {}
                row['ta_query'] = ta_query
                row['ta_status']  = 'not_data'
                row['ta_path_source'] = full_name
                json_list_result.append(row)
            else:
                for res_obj in obj_orgs:
                    row = {}
                    row['ta_query'] = ta_query
                    row['ta_status']  = 'new'
                    row['ta_path_source'] = full_name
                    #res_obj = get_best_from_result(row, obj_orgs)
                    for key in res_obj:
                        new_key = key
                        if not new_key.startswith('ta_'):
                            new_key = 'ta_' + new_key
                        row[new_key] = res_obj[key]

                    row['ta_location_id'] = int(row['ta_location_id'])
                    row['ta_address'] = load_trip_search.revert_address(row['ta_address'])
                    row['ta_address_n'] = common.replace_address_by_city_code(city_code, row['ta_address'])
                    json_list_result.append(row.copy())
        
    df_result = pd.DataFrame(json_list_result)
    #df_result
    if type(df_all_trip_search) == pd.DataFrame:
        df_result = pd.concat([df_all_trip_search, df_result],ignore_index=True).drop_duplicates()
    print(df_result.shape)
    print(df_result.columns)
    print('saving...')
    df_result.to_hdf('tables\\all_trip_search_new.hd','DATA')
    df_result.info()

if __name__ == '__main__':
    collect_all_file_to_one_db()