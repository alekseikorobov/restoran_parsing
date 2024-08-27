
import os
#os.chdir('C:\work\map_api')
import requests
import urllib.parse as parse
import re
import time
import random
import json
import warnings
import logging
warnings.filterwarnings("ignore")
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.INFO)

from params import Params

#кеш отключил - https://github.com/alekseikorobov/MyCache
#from my_cache import CacheStor, TypeStorage

import requests
from bs4 import BeautifulSoup, NavigableString, PageElement, Tag
import json

import pandas as pd
#from tqdm import tqdm
import common.common as common
#tqdm.pandas()

#кеш отключил
#cache_stor = CacheStor(db_file='data/my.db',type_storage=TypeStorage.IN_DISK,is_debug_log=False)


class LoadYaFeatures:
    def __init__(self, params: Params) -> None:
        self.params = params
        self._driver:WebDriver = None
        self.dict_services = {
            'Услуги и удобства:Круглосуточная стойка регистрации':'Круглосуточная регистрация',
            'Инфраструктура:Парковка':'Парковка',
            'Услуги и удобства:Камера хранения':'Камера хранения',
            'Услуги и удобства:Прачечная':'Прачечная',
            'Питание:Ресторан':'Ресторан',
            'main_info:Завтрак':'Завтрак',
            'Услуги и удобства:Трансфер':'Трансфер',
            'Питание:Бар':'Бар',
            'Бизнес-услуги:Конференц-зал':'Конференц-зал',
            'Услуги и удобства:Возможно проживание с животными':'Проживание с животными',
            'Услуги и удобства:Банкетный зал':'Банкетный зал',
            'Красота и здоровье:Сауна':'Сауна',
            'Спорт и развлечения:Тренажёрный зал':'Тренажёрный зал',
            'Спорт и развлечения:Бассейн':'Бассейн',
            'Красота и здоровье:Spa':'Спа',
            'main_info:Рядом с морем':'Рядом с морем',
            'main_info:Трансфер':'Трансфер',
        }

    @property
    def driver(self) -> WebDriver:
        if self._driver is not None:
            return self._driver 
        self._driver = common.get_global_driver(self.params)

        return self._driver

    def get_heares(self):
        t = r'yandex_api\headers_features.txt'
        heares = {}
        with open(t,'r') as f:
            for line in f.readlines():
                line = line.strip()
                k,v = line.split(':')
                k,v = k.strip(),v.strip()
                heares[k] = v
        return heares


    #@cache_stor.cache(folder='data/yandex_features_html')
    def get_ya_features_html(self,full_url,ya_id:str):
        base_folder=self.params.cache_data_folder
        is_replase =self.params.is_ya_rating_replace_html_request
        
        path = common.get_folder(base_folder.rstrip('/\\') + '/yandex_features','','html')
        full_name = f'{path}/{ya_id}.html'
        html_result = ''
        if is_replase or not common.isfile(full_name):
          # raise(Exception(f'Нельзя скачивать, берем из кеша! {full_url}'))
          # not work:
          # headers = get_heares()
          # res = requests.get(full_url, headers=headers, verify=False, timeout=5)
          # return res.text #return code 403!!!!
          self.driver.get(full_url)
          html_result = self.driver.page_source

          with open(full_name,'w',encoding='UTF-8') as f:
            f.write(html_result)
          logging.debug(f'write to file {full_name=}')
        else:
          with open(full_name,'r',encoding='UTF-8') as f:
            html_result = f.read()
          logging.debug(f'read from file {full_name=}')

        return html_result


    def get_feature_from_html_json(self,html:str,ya_id:str):
        #
        soup = BeautifulSoup(html,"html.parser")
        elements = soup.find(class_='business-features-view')

        curr_title = 'main_info'
        json_result = {curr_title:{}}
        if elements is not None:
            for element in elements:
                if not hasattr(element,'attrs'):
                  continue

                if 'features-cut-view' in element.attrs['class']:
                    all_text = element.find_all(class_='business-features-view__bool-text')

                    json_result[curr_title]['list'] = [common.get_normal_text_from_element(f) for f in all_text]

                elif 'business-features-view__group-title' in element.attrs['class']:
                    el = element.find(class_='business-features-view__group-name')
                    curr_title = common.get_normal_text_from_element(el).strip(' :')
                    json_result[curr_title] = {}
                
                # elif 'business-feature-a11y-group-view' in element.attrs['class']:
                #     el = element.find(class_='business-feature-a11y-group-view__name')
                #     json_result[el.text] = {}

                elif 'business-features-view__cut' in element.attrs['class']:
                    if 'other' not in json_result[curr_title]:
                        json_result[curr_title]['other'] = []
                    valued_content = element.find_all(class_='business-features-view__valued-content')

                    for valued_content_item in valued_content:
                        el = valued_content_item.find(class_='business-features-view__valued-title')
                        el_val = valued_content_item.find(class_='business-features-view__valued-value')
                        json_result[curr_title]['other'].append({
                            common.get_normal_text_from_element(el).strip(' :'):common.get_normal_text_from_element(el_val)
                        })
        return json_result

    def get_feature_from_ya_json(self,ya_link_org:str,ya_id:str):
        try:
            if common.is_nan(ya_link_org): return ya_link_org
            url = f'{ya_link_org}/features/'
            html = self.get_ya_features_html(url,ya_id)
            if '<div class="content-panel-error-view__title">Ничего не найдено.</div>' in html:
              return {}
            json_result = self.get_feature_from_html_json(url, ya_id)
            return json_result
        except Exception as ex:
          print(ya_link_org)
          raise(ex)


    def extract_key(self,p_xpath:str,result):
      notes = p_xpath.split('/')
      element = result
      for node in notes:
        if node[0] == '@': #массив?
          key = node[1:]
          for other in element:
            if key in other:
              return other[key]
        elif node in element: #иначе если это узел, то продолжаем погружаться
          element = element[node]
      return None

    def extract_list(self,p_xpath:str,result): #result:dict|list
      nodes = p_xpath.split('/')
      node = nodes[0]
      resluts = []
      pattern = '^(\*)\-\[(.*)\]$'
      m = re.match(pattern,node)
      exclude_list = []
      if m:
        exclude_list = m.group(2).split(';')
        node = m.group(1)
      
      if node == '*':
        if isinstance(result,dict):
          _p_xpath = '/'.join(nodes[1:])
          for key in result.keys():
            if key in exclude_list:
              continue
            _reslut = self.extract_list(_p_xpath,result[key])
            resluts.extend([f'{key}:{r}' for r in _reslut])
          return resluts
        if isinstance(result,list):
          return result
      elif isinstance(result,dict) and node in result:
        _p_xpath = '/'.join(nodes[1:])
        return self.extract_list(_p_xpath,result[node])
      
      return resluts

    
    def ya_feature_service_selector(self, services:list):
        if common.is_nan(services): return services
        services_result = [self.dict_services[s] for s in services if s in self.dict_services]
        return ','.join(sorted(set(services_result)))

    def get_feature_ya(self,row):
      result = self.get_feature_from_ya_json(row['ya_link_org'],row['ya_id'])

      row['ya_f_price'] = self.extract_key('Прочее/other/@Цена номера:',result)
      row['ya_f_stars'] = self.extract_key('Общая информация об отеле/other/@Количество звёзд:',result)
      row['ya_f_count_num'] = self.extract_key('Общая информация об отеле/other/@Номеров:',result)
      row['ya_f_year_build'] = self.extract_key('Общая информация об отеле/other/@Дата постройки:',result)

      services = self.extract_list('*-[Удобства в номерах]/list/*',result)
      row['ya_f_services'] = ';'.join(services)

      row['ya_f_services_selected'] = self.ya_feature_service_selector(services)
      
      services_num = self.extract_list('Удобства в номерах/list/*',result)
      row['ya_f_services_num'] = ';'.join(services_num)

      return row

    def start(self, df_source:pd.DataFrame) -> pd.DataFrame:
        '''
          На вход должны быть поля:
          - ya_id
          - ya_link_org
        '''

        df_source['ya_id'] = df_source['ya_id'].astype(str)
        df_result = df_source.apply(self.get_feature_ya,axis=1)
        df_result = pd.DataFrame(df_result)
        
        return df_result

# if __name__ == '__main__':

#   list_data = [
#     '1201673884'
#     ,'1200202235'
#     ,'1078681734'
#     ,'1013201420'
#     ,'1118287570'
#   ]
#   #from tqdm import tqdm
#   for ya_id in list_data:
#     url = f'https://yandex.ru/maps/org/novotel/{ya_id}/features/'
#     #url = 'https://yandex.ru/maps/org/radisson_blu_hotel_chelyabinsk/1201673884/features/'
#     json_result = get_feature_from_url_json_str(url)
#     print(f'{ya_id}, {len(json_result)}')
#     # patern = 'Количество звёзд'
#     # # 'Количество звёзд<!-- -->:</span><span class="business-features-view__valued-value">4</span></div>'
#     # a = result_html.find(patern)
#     # if a != -1:
#     #     print(f'{ya_id} {len(result_html)}, {a},{result_html[a:a+98]}')
#     # else:
#     #      print(f'{ya_id} {len(result_html)}, {a}')
