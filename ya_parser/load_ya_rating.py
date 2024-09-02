import pandas as pd
import common.common as common
import common.dict_city as dict_city
import os
import requests
import warnings
warnings.filterwarnings("ignore")
import time,random
from bs4 import BeautifulSoup, NavigableString, PageElement, Tag
import logging

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from params import Params

class LoadYaRating:
    def __init__(self, params: Params) -> None:
        self.params = params
        self._driver:WebDriver = None

    def get_random_second(self):
        time.sleep(random.choice([2,3, 1]))

    @property
    def driver(self) -> WebDriver:
        if self._driver is not None:
            return self._driver 
        self._driver = common.get_global_driver(self.params)
        
        if self.params.is_ya_using_cookies_rating:
          self._driver.get('https://yandex.ru/maps/')
                            
          cookies_dict = self.params.ya_parser_cookies_features
          for cookie in cookies_dict:
            self._driver.add_cookie(cookie)

        return self._driver
    
    def get_rating_html(self, city_code, id:str, params):

      base_folder=params.cache_data_folder
      proxy = params.proxy
      timeout=params.timeout_load_ya_image_params
      headers=params.ya_parser_headers_rating
      is_replase=params.is_ya_rating_replace_html_request

      http_client = params.ya_parser_http_client
      selenium_browser = params.ya_parser_selenium_browser
      chromedriver_path = params.ya_parser_selenium_chromedriver_path
      proxies = {'http': proxy,'https': proxy}

      logging.debug(f'{headers=}')
      logging.debug(f'{proxy=}')
      logging.debug(f'{timeout=}')
      logging.debug(f'{http_client=}')
      logging.debug(f'{chromedriver_path=}')
      logging.debug(f'{selenium_browser=}')

      path = common.get_folder(base_folder.rstrip('/\\') + '/yandex_r',city_code,'html')
      full_name = f'{path}/{id}.html'
      html_result = ''
      if is_replase or not common.isfile(full_name):
        full_url = f'https://yandex.ru/maps-reviews-widget/{id}?size=m&comments'
        logging.debug(f'load from {full_url=}')

        if http_client == 'requests':
          res = requests.get(full_url, headers=headers, verify=False, proxies=proxies, timeout=timeout)
          html_result = res.text
          self.get_random_second()
        elif http_client == 'selenium':
          self.driver.get(full_url)


          try:
            logging.debug('start wait element from page')
            second_wait = 30
            element = WebDriverWait(self.driver, second_wait).until(
                EC.presence_of_element_located((By.CLASS_NAME, "comment__stars"))
            )
            logging.debug('end wait element from page')
          except Exception as e:
            logging.error('NOT CORRECT PAGE:')
            logging.error(f"{self.driver.page_source}", exc_info=True)
            raise(Exception(e))

          html_result = self.driver.page_source

          all_cookies = self.driver.get_cookies()
          cookies_str = ';'.join(
            [f"{c['name']}={c['value']}"
              for c in all_cookies
            ]
          )
          logging.debug(f'{cookies_str=}')

          if params.log_level_selenium == 'DEBUG':
              self.driver.get_log('browser')
              self.driver.get_log('driver')
              #driver.get_log('client') #error - not found 'client'
              #driver.get_log('server') #error - not found 'server'
        
        if html_result == '':
          raise(Exception('not correct data html is empty!'))
        with open(full_name,'w',encoding='UTF-8') as f:
          f.write(html_result)
        logging.debug(f'write to file {full_name=}')
      else:
        with open(full_name,'r',encoding='UTF-8') as f:
          html_result = f.read()
        logging.debug(f'read from file {full_name=}')

      return html_result

    def parse_html_get_json(self, html_str:str) -> dict:
      result_data = {
        'ya_org_name':'',
        'ya_stars_count':'',
        'ya_rating':'',
        'ya_link_org':'',
      }

      soup = BeautifulSoup(html_str,"html.parser")

      mini_badge_element = soup.find('div',class_='mini-badge')

      if mini_badge_element is not None:
        mini_badge_org_name_element = soup.find('a',class_='mini-badge__org-name')
        if mini_badge_org_name_element is not None:
          result_data['ya_org_name']  = common.get_normal_text_from_element(mini_badge_org_name_element)

        mini_badge_stars_count_element = soup.find('p',class_='mini-badge__stars-count')
        if mini_badge_stars_count_element is not None:
          result_data['ya_stars_count']  = common.get_normal_text_from_element(mini_badge_stars_count_element)

        mini_badge_rating_element = soup.find('a',class_='mini-badge__rating')
        if mini_badge_rating_element is not None:
          result_data['ya_rating']  = common.get_normal_text_from_element(mini_badge_rating_element)

        mini_badge_org_name_element = soup.find('a',class_='mini-badge__org-name')
        if mini_badge_org_name_element is not None and mini_badge_org_name_element.attrs is not None:
          result_data['ya_link_org']  = common.strip_url(mini_badge_org_name_element.attrs['href'], use_exclude = False)

      return result_data

    def get_json_ya_rating(self, city_code, ya_id, params) -> dict:
      html_result = self.get_rating_html(city_code, ya_id,params)
      json_result = self.parse_html_get_json(html_result)
      return json_result


    def parse_and_get_result(self, row):
      if common.is_nan(row['ya_id']): return row
      ya_id = str(row['ya_id']).replace('.0','')
      city_name = row['location_nm_rus']
      city_line = dict_city.get_line_by_city_name(city_name,city_list=self.params.city_list)
      city_code = city_line['city']
      json_result = self.get_json_ya_rating(city_name, ya_id,self.params)
      for key in json_result:
        row[key] = json_result[key]

      return row
    def start(self, df_source:pd.DataFrame) -> pd.DataFrame:
      logging.debug(f'{df_source.columns=}')
      df_result = df_source.apply(self.parse_and_get_result,axis=1)
      df_result = pd.DataFrame(df_result)
      
      return df_result
