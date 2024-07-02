
# см как алгоритм - "C:\Users\aakorobov\Documents\work\Weekly\2023\docs\Алгоритм получения фоток из Яндекс по организациям.md"

import asyncio
import aiofiles
import aiofiles.os
import pandas as pd
import common.dict_city as dict_city
import common.common as common
import ya_parser.load_ya_raiting as load_ya_raiting
import aiohttp
import random
from bs4 import BeautifulSoup, NavigableString, PageElement, Tag
import json
import base64
import requests
import numpy as np
from tqdm import tqdm

tqdm.pandas()
import warnings
warnings.filterwarnings("ignore")
import logging
import time

logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s\t%(filename)s\t%(funcName)s\t[%(levelname)s]\t%(lineno)d\t%(message)s",
            handlers=[
                logging.FileHandler('logs/all_logs_20231108.log',encoding='utf-8'),
                logging.StreamHandler()
            ]
        )


def get_random_second():
  time.sleep(random.choice([1,2])) #,3,4



import os
def load_image(row):
  image_url = row['image_url']
  if common.is_nan(image_url): return row
  tag_id = row['tag_id']
  # if common.is_nan(tag_id): tag_id = 'other'
  city_name = row['city_name']
  ya_id = str(row['ya_id']).replace('.0','')
  image_id = row['image_id'].replace('urn:yandex:sprav:photo:','')

  logging.debug(f"{city_name=},{ya_id=}")

  city_line = dict_city.get_line_by_city_name(city_name,[])
  path = load_ya_raiting.get_folder(city_line.city,f'gallery_images/{tag_id}')
  full_name = f'{path}\\{ya_id}_{image_id}.jpg'
  
  row['path_image'] = full_name

  if not os.path.isfile(full_name):
    logging.debug(f'load - {full_name}')
    response = requests.get(image_url)
    if response.status_code == 200:
      img_data = response.content
      with open(full_name, 'wb') as handler:
          handler.write(img_data)
    elif response.status_code == 404:
      logging.warn(f'IMAGE NOT EXISTS - {image_url}')
    else:
      raise(Exception(f'not load - {response.status_code}, {response.text}'))
    get_random_second()

  return row

async def main():

  path_from = r'tables\all_link_image_ya.xlsx'
  path_to = r'tables\all_link_image_ya_with_path.xlsx'
  df = pd.read_excel(path_from,sheet_name='Sheet1')
  #df['tag_id'].fillna('other',inplace=True)
  df['ya_id'] = df['ya_id'].astype(str)
  is_interior = df['tag_id']=='Interior'

  # качаем только по топ 10
  df = df[df['image_url'].notna() & is_interior]
  
  df['i'] = df.index
  grouped = df.groupby(['ya_id'])

  df_to_load = grouped.apply(lambda x: x.nlargest(10, 'i'))

  logging.debug(f'start load - {df_to_load.shape}')

  df_result = df_to_load.progress_apply(load_image,axis=1)

  logging.debug(f'full data - {df_result.shape=}')
  df_result.to_excel(path_to, index=False)
  
asyncio.run(main())