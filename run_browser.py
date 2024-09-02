import os
import common.common as common
import time
import ya_parser.load_ya_features as load_ya_features
import requests
import datetime
from params import Params

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time,random

class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)
driver = None

#ya_id = '1094622728'
#ya_id = '1004067747'
ya_id = '44285147668'

#full_url = f'https://yandex.ru/maps/org/svoya_kompaniya/{ya_id}/?tab=features'
#full_url = f'https://yandex.ru/maps/org/svoya_kompaniya/{ya_id}/features/'
#full_url = 'https://yandex.ru/maps/org/svoya_kompaniya/1094622728/'
full_url = 'https://yandex.ru/maps/org/boho_chic/1004067747/'

full_url_g = 'https://yandex.ru/maps/org/svoya_kompaniya/1094622728/gallery/'

# 1094622728 - ok
# 1004067747 - error
# 1051904212 - ok

import json
_load_ya_features = load_ya_features.LoadYaFeatures({})

headers = None

def get_random_second():
    time.sleep(random.choice([2,1]))

http_client = 'selenium'

available_commands = ['help','save','set','go','map','home','exit','del','html','run','req']

def cookies_dict_by_params(params):
  cookies_dict = None
  if params[0] == 'fp':
    if len(params) != 2:
      raise(AttributeError(f'not correct params {params=}'))
    if not os.path.isfile(params[1]):
      raise(AttributeError(f'file not exists from params {params[1]=}'))
    path_for_param = params[1]
    param = None
    with open(path_for_param,'r', encoding='UTF-8') as f:
        param = Params(**json.load(f))
    cookies_dict = param.ya_parser_cookies_features
    print(f'set cookies from {path_for_param}')
  elif params[0] == 'f':
    if len(params) != 2:
      raise(AttributeError(f'not correct params {params=}'))
    if not os.path.isfile(params[1]):
      raise(AttributeError(f'file not exists from params {params[1]=}'))
    cookies_dict = json.load(open(params[1],'r'))
    print(f'set cookies from {params[1]=}')
  elif params[0] == 'p': #установка куки из параметров params.py
    p = Params()
    cookies_dict = p.ya_parser_cookies_features
    print(f'set cookies from params.py')
  else:
    file_name = f'session_{params[0]}.json'
    cookies_dict = json.load(open(file_name,'r'))
    print(f'set cookies from file {file_name}')
  return cookies_dict

if http_client == 'selenium':    
    while True:
      i = input('>')
      if i.strip() == '': continue
      i += ' '
      i,params = [a.strip() for a in i.split(' ',1)]
      params = [_p.strip() for _p in params.split('=',1)]
      
      print(f'{i=}, {params=}')
      if i == 'help':
        print('тут должна быть справка, но долго писать, поэтому смотри код')
        print(f'вот все команды {available_commands}')
      elif i == 'run':
        interaction = params[0] == '0'
        driver = common.get_global_driver(Struct( **{
          'proxy':None,
          'ya_parser_selenium_browser':'chrome',
          'ya_parser_selenium_chromedriver_path':None, #"c:/work/restoran_to_dadm/lib/chromedriver-win64-126.0.6478.182/chromedriver.exe"
          'log_level_selenium':'INFO',
          'ya_parser_selenium_browser_param_headless':interaction,
        }))
        driver.get('https://yandex.ru/maps/')
      elif i == 'save':
        file_name = f'session_{params}.json'
        json.dump(driver.get_cookies(),open(file_name,'w'))
        print(f'cookies saved to {file_name}')
      elif i == 'html':
          html_result = driver.page_source
          file_name = 'test.html'
          if params[0] != '':
            file_name = params[0]
          with open(file_name,'w',encoding='UTF-8') as f:
            f.write(html_result)
          print(f'html page save to {file_name=}')
      elif i == 'set':
        if params[0] != '' and params[0] in ['1','2','p','f','fp']:
          cookies_dict = cookies_dict_by_params(params)
          for cookie in cookies_dict:
            driver.add_cookie(cookie)
        else:
          print('not set cookies')
      elif i == 'go':
        if params[0] == '':
          driver.get(full_url)
          html_result = driver.page_source
          status = _load_ya_features.check_html_features(html_result)
          print(f'{status=}')
        elif params[0] == 'g':
          driver.get(full_url_g)
          html_result = driver.page_source
      elif i == 'map':
        driver.get('https://yandex.ru/maps')
      elif i == 'home':
        driver.get('https://yandex.ru')
      elif i == 'exit':
        if driver is not None:
          driver.quit()
        break
      elif i == 'req':
        p = Params()
        headers = p.ya_parser_headers_features
        
        if params[0] != '' and params[0] in ['1','2','p','f','fp']:
          cookies_dict = cookies_dict_by_params(params)
          headers['Cookie'] = '; '.join(
            [f"{c['name']}={c['value']}" for c in cookies_dict]
          )
        else:
          print('not set cookies')
        
        res = requests.get(full_url_g, headers=headers, verify=False, timeout=5)
        #get_random_second()
        print(res.status_code)
        html_result = res.text
        if not 'orgpage-header-view__header' in html_result:
          print('not found orgpage-header-view__header')
        else:
          print('OK! found orgpage-header-view__header')
        
        if 'passport.yandex.ru' in html_result:
          print('need pass')
        # status = _load_ya_features.check_html_features(html_result)

        # print(f'{status.value=}')
        
      elif i == 'del':        
        driver.delete_all_cookies()
        print('delete all cookies')
      else:
        print(f'Ошибка ввода команды, доступны следующие команды: {available_commands}')
print('done')