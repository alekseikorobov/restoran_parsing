
# см как алгоритм - "docs\Алгоритм получения фоток из Яндекс по организациям.md"


import pandas as pd
import common.dict_city as dict_city
import common.common as common
import ya_parser.load_ya_rating as load_ya_rating
import random
from bs4 import BeautifulSoup, NavigableString, PageElement, Tag
import json
import base64
import requests
import numpy as np
import warnings
warnings.filterwarnings("ignore")
import logging
import os
import time
from params import Params

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class LoadYaImageParams:
    def __init__(self, params: Params) -> None:
        self.params = params
        self._driver:WebDriver = None

    def get_driver(self, params) -> WebDriver:
        if self._driver is not None:
            return self._driver 

        proxy = params.proxy
        browser = params.zoon_parser_selenium_browser
        chromedriver_path = params.zoon_parser_selenium_chromedriver_path
        log_level = params.log_level_selenium
        param_headless = params.ya_parser_selenium_browser_param_headless

        if browser == 'firefox':
            if proxy is not None:
                logging.warn('proxy not using!')
            options = webdriver.FirefoxOptions()
            if param_headless:
              options.add_argument("--headless")
            options.add_argument('--marionette')
            self._driver = webdriver.Firefox(options=options)
        elif browser == 'chrome':
            service = None
            if chromedriver_path is not None:
                if not os.path.isfile(chromedriver_path):
                    raise(Exception(f'driver not found from {chromedriver_path=}'))
                service = webdriver.ChromeService(executable_path=chromedriver_path)
            chrome_options = webdriver.ChromeOptions()
            if param_headless:
              chrome_options.add_argument("--headless")
            if proxy is not None:
                chrome_options.add_argument(f'--proxy-server={proxy}')
            self._driver = webdriver.Chrome(options=chrome_options,service=service)
        #log_level

        if not isinstance(logging.getLevelName(log_level.upper()),int):
            raise(Exception(f'Not correct log level in param value - {log_level}'))
        
        level=logging.getLevelName(log_level.upper())

        LOGGER.setLevel(level)

        return self._driver

    def get_random_second(self):
      time.sleep(random.choice([1,2])) #,3,4


    def get_gallery_html_by_org(self, url, city_code, ya_id):
      path = common.get_folder(self.params.cache_data_folder.rstrip('/\\') + '/yandex_r', city_code,'gallery_html')
      full_name = f'{path}/{ya_id}.html'
      html_result = ''
      if self.params.is_ya_param_g_replace_html_request or not os.path.isfile(full_name):
        headers = self.params.ya_parser_headers_gallery
        
        proxies = {'http':self.params.proxy,'https':self.params.proxy}
        http_client = self.params.ya_parser_http_client
        timeout = self.params.timeout_load_ya_image_params
        
        logging.debug(f'{url=}')
        logging.debug(f'{headers=}')
        logging.debug(f'{proxies=}')
        logging.debug(f'{http_client=}')
        logging.debug(f'{timeout=}')

        if http_client == 'requests':
          if self.params.is_ya_using_cookies_gallery:
            headers['Cookie'] = '; '.join(
              [f"{c['name']}={c['value']}" for c in self.params.ya_parser_cookies_features]
            )
          response = requests.get(url,headers=headers, verify=False, proxies=proxies, timeout=timeout)
          if response.status_code == 200:
            html_result = response.text
            logging.debug(f'{response.headers=}')
            self.get_random_second()
          else:
            raise(Exception(f'not get - {response.status_code}, {response.text}, {response.headers}'))
        elif http_client == 'selenium':
            driver = self.get_driver(self.params)
            driver.get(url)
            
            if False and self.params.is_ya_using_cookies_gallery:
              # проставление cookies сейчас работает не корректно
              # чтобы работало корректно, нужно переделать согласоно описанию в docs/request_selenium_with_cookies.md
              logging.debug('set parameters cookies')
              cookies_str = headers["Cookie"]
              cookies_dict = common.cookies_str_to_dict(cookies_str)
              driver.delete_all_cookies()
              for k,v in cookies_dict.items():
                cookie = {'name':k,'value':v}
                #logging.debug(f'add {cookie=}')
                driver.add_cookie(cookie)
              driver.refresh()

            try:
                logging.debug('start wait element from page')
                second_wait = 30#60
                element = WebDriverWait(driver, second_wait).until(
                    EC.presence_of_element_located((By.ID, "end-of-page"))
                )
                logging.debug('end wait element from page')
            except TimeoutException as e:
                logging.error('NOT CORRECT PAGE:')
                logging.error(f"{driver.page_source}", exc_info=True)
                raise(Exception(e))

            html_result = driver.page_source

            if hasattr(driver,'requests'):
              #DEBUG if using https://pypi.org/project/selenium-wire/
              for req in driver.requests:
                logging.debug(f'{request.url=}')
                logging.debug(f'{request.headers=}')
                logging.debug(f'{request.response.headers=}')
            
            all_cookies = driver.get_cookies()
            cookies_str = ';'.join(
              [f"{c['name']}={c['value']}"
                for c in all_cookies
              ]
            )
            logging.debug(f'{cookies_str=}')

            if self.params.log_level_selenium == 'DEBUG':
                driver.get_log('browser')
                driver.get_log('driver')
                #driver.get_log('client') #error - not found 'client'
                #driver.get_log('server') #error - not found 'server'

        if 'Please confirm that you and not a robot are sending requests' in html_result:
          raise(Exception('need capcha. Update - parameter headers_gallery'))
        
        
        with open(full_name,'w',encoding='UTF-8') as f:
          f.write(html_result)
          logging.debug(f'save to {full_name=}')
            
      else:
        logging.debug(f'get from {full_name=}')
        with open(full_name,'r',encoding='UTF-8') as f:
          html_result = f.read()
      return html_result

    def get_full_json_from_gallery(self, html_str):
      soup = BeautifulSoup(html_str,"html.parser")
      state_view_element = soup.find(class_ = 'state-view')
      if state_view_element is None:
        raise(Exception('not found script element by class state-view'))
      text = state_view_element.get_text(' ')
      json_result = json.loads(text)
      return json_result

    def get_param_from_gallery(self, url,city_code, ya_id):
      path = common.get_folder(self.params.cache_data_folder.rstrip('/\\') + '/yandex_r', city_code, 'gallery_param_json')
      full_name = f'{path}/{ya_id}.json'
      json_result = None
      system_links = []
      session_id = None
      if self.params.is_ya_param_g_replace_json_request or not os.path.isfile(full_name):
        html_result = self.get_gallery_html_by_org(url,city_code, ya_id)
        if html_result == '':
          logging.warning('not exists html')
          return session_id, system_links
        json_result  = self.get_full_json_from_gallery(html_result)
        logging.debug(f'write - {full_name}')
        with open(full_name,'w',encoding='UTF-8') as f:
          f.write(json.dumps(json_result))
      else:
        logging.debug(f'read - {full_name}')
        with open(full_name,'r',encoding='UTF-8') as f:
          json_result = json.load(f)

      if 'photos' in json_result['stack'][0]['results']['items'][0]:
        system_links = [item['urlTemplate'] for item in json_result['stack'][0]['results']['items'][0]['photos']['items']]
        session_id = json_result['config']['counters']['analytics']['sessionId']

      return session_id, system_links

    def get_new_csrf_token(self):
      url = 'https://yandex.ru/maps/api/photos/getByBusinessId?ajax=1'
      logging.debug(f'load {url}')
      headers = self.params.ya_parser_headers_token
      proxies = {'http':self.params.proxy,'https':self.params.proxy}
      response = requests.get(url,headers=headers, verify=False, proxies=proxies, timeout=self.params.timeout_load_ya_image_params)
      result_json = response.json()
      self.get_random_second()
      if result_json is None:
        raise(Exception('return empty'))
      if 'type' in result_json and result_json['type'] == 'captcha':
        logging.debug(result_json)
        raise(Exception('need capcha'))
      return result_json['csrfToken']

    def convert_url_to_fixed_top(self, system_links):

      result = []
      for system_link in system_links:
        message_bytes = system_link.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        result.append(base64_message)
      return ','.join(result)

    def rshift(self, val, n): return val>>n if val >= 0 else (val+0x100000000)>>n

    def get_check_sum(self, param_str):
      # магическая функция для контрольной суммы из js яндекса:
      # return t ? String(function(e) {
      #     for (var t = e.length, n = 5381, r = 0; r < t; r++)
      #         n = 33 * n ^ e.charCodeAt(r);
      #     return n >>> 0
      # }(t)) : ""

      n = 5381
      for x in param_str:
          n = np.int32(33 * n) ^ ord(x)
      return self.rshift(n, 0)

    def get_gallery_json(self, full_params):
      url = f'https://yandex.ru/maps/api/photos/getByBusinessId?{full_params}'
      logging.debug(f'load {url}')
      headers = self.params.ya_parser_headers_token
      proxies = {'http':self.params.proxy,'https':self.params.proxy}
      response = requests.get(url,headers=headers, verify=False, proxies=proxies, timeout=self.params.timeout_load_ya_image_params)
      result_json = response.json()
      self.get_random_second()
      if result_json is None:
        raise(Exception('return empty'))
      return result_json

    def get_full_params(self, session_id, system_links, ya_id):
        csrf_token = self.get_new_csrf_token()
        #csrf_token='8b770403c4f3e9cbd454f707f549581cf4bae0e7:1699435665'
        csrf_token_q = requests.utils.quote(csrf_token)
        logging.debug(f'{csrf_token=}')

        fixed_top = self.convert_url_to_fixed_top(system_links)
        fixed_top_q = requests.utils.quote(fixed_top)

        param_str = f"ajax=1&csrfToken={csrf_token_q}&fixed_top={fixed_top_q}&id={ya_id}&lang=ru_RU&sessionId={session_id}"

        param_s = self.get_check_sum(param_str)

        full_params = f'{param_str}&s={param_s}'
        return full_params

    def load_param_image_by_id(self, city_name, ya_id, ya_link_org):
      logging.debug(f'start {city_name=} {ya_id=}')

      city_line = dict_city.get_line_by_city_name(city_name,city_list=self.params.city_list)
      city_code = city_line['city']
      path = common.get_folder(self.params.cache_data_folder.rstrip('/\\') + '/yandex_r', city_code, 'gallery_json')
      full_name = f'{path}/{ya_id}.json'
      json_result = None
      if self.params.is_ya_param_replace_json_request or not os.path.isfile(full_name):
        if ya_link_org == '' or ya_link_org is None:
          raise(Exception(f'link not correct by id {ya_id}'))
        ya_link_org_gallery = ya_link_org.strip('/') + '/gallery/'
        logging.debug(f'get param from {ya_link_org_gallery=}')
        session_id, system_links = self.get_param_from_gallery(ya_link_org_gallery,city_code, ya_id)
        if session_id is None or len(system_links) == 0:
          logging.warning(f'NOT PHOTO BY {ya_id=}')
          return
        logging.debug(f'{session_id=} {len(system_links)=}')
        
        full_params = self.get_full_params(session_id, system_links, ya_id)
        
        json_result = self.get_gallery_json(full_params)
        logging.debug(f'write {len(json_result)=} - {full_name=}')

        if 'type' in json_result and json_result['type'] == 'captcha':
          logging.debug(json_result)
          raise(Exception('need capcha'))
        
        if 'csrfToken' in json_result:
          raise(Exception('need update csrfToken'))

        with open(full_name,'w',encoding='UTF-8') as f:
          json.dump(json_result,f, ensure_ascii=False)
      else:
        logging.debug(f'read - {full_name}')
        with open(full_name,'r',encoding='UTF-8') as f:
          json_result = json.load(f)
      logging.debug(f'{len(json_result)=}')

      return json_result

    def get_obj_iterator(self, json_result,ya_id,city_name):
      if json_result is None:
        data_json = {
          'ya_id':ya_id,
          'city_name':city_name,
          'tag_id':None,
          'tag_name':None,
          'image_url':None,
          'image_w':None,
          'image_h':None,
          'image_id':None,
        }
        yield data_json
      elif 'data' not in json_result:
        raise(Exception(f'not param data in json_result {json_result=}'))
      else:
        for item in json_result['data']:
          data_json = {
            'ya_id':ya_id,
            'city_name':city_name,
            'tag_id':None,
            'tag_name':None,
            'image_url':None,
            'image_w':None,
            'image_h':None,
            'image_id':None,
          }
          if 'tags' in item and len(item['tags'])>0:
            for tag in item['tags']:
              data_json['tag_id'] = tag['id']
              data_json['tag_name'] = str(tag['name'])
              data_json['image_url'] = item.get('url',None)
              data_json['image_w'] = item.get('width',None)
              data_json['image_h'] = item.get('height',None)
              data_json['image_id'] = item.get('id',None)
          else:
            data_json['image_url'] = item.get('url',None)
            data_json['image_w'] = item.get('width',None)
            data_json['image_h'] = item.get('height',None)
            data_json['image_id'] = item.get('id',None)
          yield data_json

    def start(self, df):
      data_json_list = []

      for i, row in df.iterrows():
        city_name = row['location_nm_rus']
        ya_id = str(row['ya_id']).replace('.0','')
        ya_link_org = row['ya_link_org']
        logging.debug(f"{city_name=},{ya_id=}")
        json_result = self.load_param_image_by_id(city_name, ya_id, ya_link_org)

        for data_json in self.get_obj_iterator(json_result, ya_id, city_name):
          data_json_list.append(data_json)
        
      df_result = pd.DataFrame(data_json_list)
      return df_result
