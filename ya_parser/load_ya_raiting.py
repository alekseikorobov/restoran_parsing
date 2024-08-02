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

def get_random_second():
  time.sleep(random.choice([2,3, 1]))

def get_folder(base_folder, city: str, sub_folder: str) -> str:
  path = f'{base_folder}/yandex_r/{city}/{sub_folder}'.rstrip('/\\')
  if not os.path.isdir(path):
    os.makedirs(path)
  return path

driver:WebDriver = None

def get_driver(proxy=None, browser='chrome',chromedriver_path = None, log_level='info') -> WebDriver:
    global driver
    if driver is not None:
        return driver 
    if browser == 'firefox':
        if proxy is not None:
            logging.warn('proxy not using!')
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        options.add_argument('--marionette')
        driver = webdriver.Firefox(options=options)
    elif browser == 'chrome':
        service = None
        if chromedriver_path is not None:
            if not os.path.isfile(chromedriver_path):
                raise(Exception(f'driver not found from {chromedriver_path=}'))
            service = webdriver.ChromeService(executable_path=chromedriver_path)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        if proxy is not None:
            chrome_options.add_argument(f'--proxy-server={proxy}')
        driver = webdriver.Chrome(options=chrome_options,service=service)
    #log_level

    if not isinstance(logging.getLevelName(log_level.upper()),int):
        raise(Exception(f'Not correct log level in param value - {log_level}'))
    
    level=logging.getLevelName(log_level.upper())

    LOGGER.setLevel(level)

    return driver

def get_raiting_html(city_code, id:str, params):

  base_folder=params.cache_data_folder
  proxy = params.proxy
  timeout=params.timeout_load_ya_image_params
  headers=params.ya_parser_headers_raiting
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

  path = get_folder(base_folder,city_code,'html')
  full_name = f'{path}/{id}.html'
  result_html = ''
  if is_replase or not common.isfile(full_name):
    full_url = f'https://yandex.ru/maps-reviews-widget/{id}?size=m&comments'
    logging.debug(f'load from {full_url=}')

    if http_client == 'requests':
      res = requests.get(full_url, headers=headers, verify=False, proxies=proxies, timeout=timeout)
      result_html = res.text
      get_random_second()
    elif http_client == 'selenium':
      driver = get_driver(proxy=proxy, browser=selenium_browser,chromedriver_path=chromedriver_path,log_level=params.log_level_selenium)
      driver.get(full_url)

      if params.is_ya_using_cookies:
          logging.debug('set parameters cookies')
          if 'Cookie' in headers:
            cookies_str = headers["Cookie"]
            cookies_dict = common.cookies_str_to_dict(cookies_str)
            driver.delete_all_cookies()
            for k,v in cookies_dict.items():
              cookie = {'name':k,'value':v}
              #logging.debug(f'add {cookie=}')
              driver.add_cookie(cookie)
          else:
            logging.warn('in headers (params ya_parser_headers_raiting) not found key by name Cookie')

      try:
        logging.debug('start wait element from page')
        second_wait = 30
        element = WebDriverWait(driver, second_wait).until(
            EC.presence_of_element_located((By.CLASS_NAME, "comment__stars"))
        )
        logging.debug('end wait element from page')
      except Exception as e:
        logging.error('NOT CORRECT PAGE:')
        logging.error(f"{driver.page_source}", exc_info=True)
        raise(Exception(e))

      result_html = driver.page_source

      all_cookies = driver.get_cookies()
      cookies_str = ';'.join(
        [f"{c['name']}={c['value']}"
          for c in all_cookies
        ]
      )
      logging.debug(f'{cookies_str=}')

      if params.log_level_selenium == 'DEBUG':
          driver.get_log('browser')
          driver.get_log('driver')
          #driver.get_log('client') #error - not found 'client'
          #driver.get_log('server') #error - not found 'server'
    
    if result_html == '':
      raise(Exception('not correct data html is empty!'))
    with open(full_name,'w',encoding='UTF-8') as f:
      f.write(result_html)
    logging.debug(f'write to file {full_name=}')
  else:
    with open(full_name,'r',encoding='UTF-8') as f:
      result_html = f.read()
    logging.debug(f'read from file {full_name=}')

  return result_html

def parse_html_get_json(html_str:str) -> dict:
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

def get_json_ya_raiting(city_code, ya_id,params) -> dict:
  html_result = get_raiting_html(city_code, ya_id,params)
  json_result = parse_html_get_json(html_result)
  return json_result
