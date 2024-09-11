
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
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.remote_connection import LOGGER

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

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

from enum import Enum


class StatusCheckHtml(Enum):
    OK = 'OK'
    ERROR_CAPCHA = 'Требуется ввод капчи'
    ERROR_AUTORITY = 'Ошибка авторизации' #Авторизация не удалась
    ERROR_403 = 'Ошибка авторизации 403'
    EMPTY = ''

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

    def get_random_second(self):
        time.sleep(random.choice([2,3, 1]))
        
    @property
    def driver(self) -> WebDriver:
        if self._driver is not None:
            return self._driver 
        self._driver = common.get_global_driver(self.params)
        
        if self.params.is_ya_using_cookies_feature:
          self._driver.get('https://yandex.ru/maps/')
                            
          cookies_dict = self.params.ya_parser_cookies_features
          for cookie in cookies_dict:
            self._driver.add_cookie(cookie)
            
        return self._driver

    def get_headers_from_line(self, line:str):
        
        if line is None or line.strip() == '':
          return None,None
        
        if ':' not in line:
            raise(AttributeError(f'not exits : {line=}'))
        left_index = line.find(':')
        k,v = line[0:left_index].strip(),line[left_index+1:].strip()
        if k == '': k = None
        if v == '': v = None
        return k,v
            
    def get_headers_from_lines(self, lines:list):
        headers = {}
        for line in lines:
            k,v = self.get_headers_from_line(line)
            if k is None or v is None:
              continue
            if k in headers:
              raise(AttributeError(f'key {k} already exists in dict'))
            headers[k] = v
        return headers

    def get_headers(self):
        t = 'ya_parser/headers_features.txt'
        with open(t,'r') as f:
            lines = [l.strip() for l in f.readlines()]
            return self.get_headers_from_lines(lines)

    
    def get_ya_features_html_src(self, full_url):
        '''Получение html по ссылке из источника (без кеша)
        '''
        # raise(Exception(f'Нельзя скачивать, берем из кеша! {full_url}'))
        # not work:
        # headers = get_headers()
        # res = requests.get(full_url, headers=headers, verify=False, timeout=5)
        # return res.text #return code 403!!!!
        
        proxy=self.params.proxy
        timeout=self.params.timeout_load_ya_image_params
        headers=self.params.ya_parser_headers_features
        http_client = self.params.ya_parser_http_client
        proxies = {'http': proxy,'https': proxy}
        logging.debug(f'load from url - {full_url}')
        logging.debug(f'{headers=}')
        logging.debug(f'{proxy=}')
        logging.debug(f'{timeout=}')
        logging.debug(f'{http_client=}')
        
        html_result = ''
        if http_client == 'requests':
            if self.params.is_ya_using_cookies_feature:
              
                ya_parser_cookies_features = common.get_cookies_fix_time(self.params.ya_parser_cookies_features,
                                                                         self.params.is_ya_cookies_feature_fix_time)
              
                headers['Cookie'] = '; '.join(
                  [f"{c['name']}={c['value']}" for c in ya_parser_cookies_features]
                )
                logging.debug(f"{headers['Cookie']=}")
            res = requests.get(full_url, headers=headers, verify=False, proxies=proxies, timeout=timeout)
            if res.status_code == 200:
              html_result = res.text
              logging.debug(f'{res.headers=}')
              self.get_random_second()
            else:
              raise(Exception(f'not get - {res.status_code}, {res.text}, {res.headers}'))
        elif http_client == 'selenium':
            self.driver.get(full_url)
            try:
              logging.debug('start wait element from page')
              second_wait = 30
              element = WebDriverWait(self.driver, second_wait).until(
                  EC.presence_of_element_located((By.CLASS_NAME, "business-card-view__main-wrapper"))
              )
              logging.debug('end wait element from page')
            except Exception as e:
              logging.error('NOT CORRECT PAGE:')
              logging.error(f"{self.driver.page_source}", exc_info=True)
              raise(Exception(e))
            
            html_result = self.driver.page_source
            
            if params.log_level_selenium == 'DEBUG':
              self.driver.get_log('browser')
              self.driver.get_log('driver')
              
            self.get_random_second()
        
        if html_result == '':
          raise(Exception('not correct data html is empty!'))
        
        return html_result
      


    #@cache_stor.cache(folder='data/yandex_features_html')
    def get_ya_features_html(self,full_url,ya_id:str):
        base_folder=self.params.cache_data_folder
        is_replase =self.params.is_ya_rating_replace_html_request
        
        path = common.get_folder(base_folder.rstrip('/\\') + '/yandex_features','','html')
        full_name = f'{path}/{ya_id}.html'
        html_result = ''
        if is_replase or not common.isfile(full_name):
          
          html_result = self.get_ya_features_html_src(full_url)
          
          with open(full_name,'w',encoding='UTF-8') as f:
            f.write(html_result)
          logging.debug(f'write to file {full_name=}')
        else:
          with open(full_name,'r',encoding='UTF-8') as f:
            html_result = f.read()
          logging.debug(f'read from file {full_name=}')

        return html_result


    def get_feature_from_html_json(self,html:str,ya_id:str):
        logging.debug('get_feature_from_html_json')
        soup = BeautifulSoup(html,"html.parser")
        elements = soup.find(class_='business-features-view')

        curr_title = 'main_info'
        json_result = {curr_title:{}}
        if elements is None:
          logging.warn(f'element by business-features-view is null')
          return json_result
        for element in elements:
            if not hasattr(element,'attrs'):
              logging.warn(f'element has not contains attribute attrs {element=}. Skip element')
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
          
        logging.debug(f'{len(json_result)=}')
        return json_result

    def check_html_features(self, html_str:str)->StatusCheckHtml:
        if '<div class="content-panel-error-view__title">Ничего не найдено.</div>' in html_str:
          return StatusCheckHtml.EMPTY
        
        if 'Подтвердите, что запросы отправляли вы, а не робот' in html_str or 'checkcaptcha' in html_str:
          return StatusCheckHtml.ERROR_CAPCHA
        
        if '<title>Авторизация</title>' in html_str and 'Авторизация не' in html_str:
          return StatusCheckHtml.ERROR_AUTORITY

        if 'Access to&nbsp;our service has been temporarily blocked.' in html_str:
          return StatusCheckHtml.ERROR_403
                
        return StatusCheckHtml.OK
      
    
    
    def get_feature_from_ya_json(self,ya_link_org:str,ya_id:str):
        try:
            if common.is_nan(ya_link_org):
              logging.warn(f'by {ya_id=} ya_link_org is null') 
              return ya_link_org
            url = f'{ya_link_org}/features/'
            html = self.get_ya_features_html(url,ya_id)
            
            status = self.check_html_features(html)
            logging.debug(f'check_html_features - {status}')
            
            if status in [StatusCheckHtml.ERROR_CAPCHA,
                          StatusCheckHtml.ERROR_AUTORITY,
                          StatusCheckHtml.ERROR_403]:
              raise(Exception(status.value))
            
            if status == StatusCheckHtml.EMPTY:
              return {}
            if status == StatusCheckHtml.OK:
              json_result = self.get_feature_from_html_json(html, ya_id)
              return json_result
        except Exception as ex:
          print(ya_link_org)
          raise(ex)


    def extract_key(self,p_xpath:str,result):
      #logging.debug(f'{p_xpath=},{type(result)=}')
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

    def get_feature_ya_hotel(self,row):
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
    
    def get_feature_ya_rest(self,row):
      result = self.get_feature_from_ya_json(row['ya_link_org'],row['ya_id'])
      
      row['ya_f_avg_price'] = None
      row['ya_f_cuisine'] = None

      if not common.is_nan(result):
        row['ya_f_avg_price'] = self.extract_key("Цены/other/@Средний счёт", result)
        row['ya_f_cuisine'] = self.extract_key("Общая информация/other/@Кухня", result)
      
      return row

    def start(self, df_source:pd.DataFrame) -> pd.DataFrame:
        '''
          На вход должны быть поля:
          - ya_id
          - ya_link_org
        '''

        df_source['ya_id'] = df_source['ya_id'].astype(str)
        df_result = df_source.apply(self.get_feature_ya_rest,axis=1)
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
#     # a = html_result.find(patern)
#     # if a != -1:
#     #     print(f'{ya_id} {len(html_result)}, {a},{html_result[a:a+98]}')
#     # else:
#     #      print(f'{ya_id} {len(html_result)}, {a}')
