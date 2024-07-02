
#%%
import os
import glob
from tqdm import tqdm
import pandas as pd
import json
import common.common as common
from geopy.distance import geodesic as GD 
import ta_parser.load_data as ta_load_data
import importlib
importlib.reload(ta_load_data)
#%%
#def collect_all_file_to_one_db():
#df_all_trip_details = pd.read_hdf('tables/all_trip_details.hd','DATA')
df_all_trip_details = None
#df_all_trip_details.shape
#%%

#left_base_path = 'C:\\work\\map_api\\'

base_path = r'C:\work\map_api\data_ta\*\details_json\*.json'

#base_path.replace(left_base_path,'').replace('\\','/')

df_result = pd.DataFrame()
json_list_result = []
i = 0
max_i = 5
for full_name in tqdm(glob.glob(base_path)):
    i+=1
    #if i > max_i: break
    #print(full_name)
    file_name = full_name.split('\\')[-1]
    city_code = full_name.split('\\')[-3]
    file_name_w_ex = file_name.replace('.json','')

    location_id = int(file_name_w_ex)
    
    row = ta_load_data.parse_page_details_from_json(full_name, location_id)

    json_list_result.append(row)
    
df_result = pd.DataFrame(json_list_result)
#df_result
print(f'{df_result.shape=}')
if type(df_all_trip_details) == pd.DataFrame:
    df_result = pd.concat([df_all_trip_details, df_result],ignore_index=True).drop_duplicates()
print(df_result.shape)
print(df_result.columns)
print('saving...')
df_result.to_hdf('tables\\all_trip_details_new.hd','DATA')
df_result.info()

# if __name__ == '__main__':
#     collect_all_file_to_one_db()

#%%
df_result.columns
#%%
df_result['ta_location_id'].value_counts(dropna=False)
