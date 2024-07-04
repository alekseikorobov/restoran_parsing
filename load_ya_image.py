
# см как алгоритм - "C:\Users\aakorobov\Documents\work\Weekly\2023\docs\Алгоритм получения фоток из Яндекс по организациям.md"

import pandas as pd
import common.dict_city as dict_city
import common.common as common
import ya_parser.load_ya_raiting as load_ya_raiting
import random
from bs4 import BeautifulSoup, NavigableString, PageElement, Tag
import json
import base64
import requests
import numpy as np
from tqdm import tqdm
from functools import partial
tqdm.pandas()
import warnings
warnings.filterwarnings("ignore")
import logging
import time
import os

from params import Params

class LoadYaImage:
    def __init__(self, params: Params) -> None:
        self.params = params

    def get_random_second(self):
      time.sleep(random.choice([1,2])) #,3,4

    def load_image(self, row):
      image_url = row['image_url']
      if common.is_nan(image_url): return row
      tag_id = row['tag_id']
      # if common.is_nan(tag_id): tag_id = 'other'
      city_name = row['city_name']
      ya_id = str(row['ya_id']).replace('.0','')
      #image_id = row['image_id'].replace('urn:yandex:sprav:photo:','')
      image_id = common.get_id_from_ya_image_url(image_url)

      logging.debug(f"{city_name=},{ya_id=}")

      image_folder = self.params.ya_images_folder.rstrip('/\\')
      if not os.path.isdir(image_folder):
        os.makedirs(image_folder)

      full_name = f'{image_folder}/{ya_id}_{image_id}.jpg'
      
      row['path_image'] = full_name
      proxies = {'http':self.params.proxy,'https':self.params.proxy}
      if not os.path.isfile(full_name):
        logging.debug(f'load - {full_name}')
        response = requests.get(image_url,verify=False, proxies=proxies, timeout=self.params.timeout_load_ya_image)
        if response.status_code == 200:
          img_data = response.content
          with open(full_name, 'wb') as handler:
              handler.write(img_data)
        elif response.status_code == 404:
          logging.warn(f'IMAGE NOT EXISTS - {image_url}')
        else:
          raise(Exception(f'not load - {response.status_code}, {response.text}'))
        self.get_random_second()
      else:
        logging.debug(f'image already exists - {full_name}')

      return row

    def start(self, df):
      #df['tag_id'].fillna('other',inplace=True)
      df['ya_id'] = df['ya_id'].astype(str)
      is_interior = df['tag_id']=='Interior'

      # качаем только по топ 10
      df = df[df['image_url'].notna() & is_interior]
      
      df['i'] = df.index
      grouped = df.groupby(['ya_id'])
      logging.debug(f'{self.params.top_load_ya_image=}')
      df_to_load = grouped.apply(lambda x: x.nlargest(self.params.top_load_ya_image, 'i'))

      logging.debug(f'start load - {df_to_load.shape}')
      df_result = df_to_load.progress_apply(self.load_image, axis=1)

      logging.debug(f'full data - {df_result.shape=}')
      return logging
      #df_result.to_excel(path_to, index=False)
