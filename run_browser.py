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

from string import Template

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

test_url_dict = {
  '1':'https://yandex.ru/maps/org/boho_chic/1004067747/features/',
  '2':'https://yandex.ru/maps/org/svoya_kompaniya/1094622728/gallery/'
}

# 1094622728 - ok
# 1004067747 - error
# 1051904212 - ok

import json
_load_ya_features = load_ya_features.LoadYaFeatures({})

headers = None

def get_random_second():
    time.sleep(random.choice([2,1]))

http_client = 'selenium'

available_commands = ['help','save','set','go','map','home','exit','del','html','run','req','test']

def cookies_dict_by_params(params):
  cookies_dict = None
  if params[0] == 'fp':
    if len(params) != 2:
      if len(params) == 1:
        params.append('params.json')
      else:
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
  
  time_stamp = common.from_date_to_unix_timestamp(common.get_now(10))
  time_stamp_year = common.from_date_to_unix_timestamp(common.get_now(365))
  expiry = time_stamp_year #1759513924
  time_stamp_short = time_stamp
  time_stamp_old = 1724953924
  time_stamp_full_old = 1724953924650
  print(f'{time_stamp=}')
  print(f'{time_stamp_old=}')
  
  time_stamp_full = time_stamp*1000
  ## обновление с учетом подстановки
  rep = ['_Session_id']
  #'Session_id','L','zen_session_id','domain_sid','sessionid2','ymex']

  for cookie in cookies_dict:
    _time_stamp_full = time_stamp_full
    _time_stamp_short = time_stamp_short
    if cookie['name'] not in rep:
      _time_stamp_full = time_stamp_full_old
      _time_stamp_short = time_stamp_old
    cookie['value'] = Template(cookie['value']).substitute({
      'time_stamp_full': _time_stamp_full,
      'time_stamp_short': _time_stamp_short,
    })
    cookie['expiry'] = expiry
    
  return cookies_dict

args = [
  'run',
  'set fp',
  'go',
  'req fp'
]

if http_client == 'selenium':
    selected_type = '1'
    while True:
      i = ''
      if len(args)>0:
        i = args.pop(0)
      else:
        i = input('>')
      if i.strip() == '': continue
      i += ' '
      i,params = [a.strip() for a in i.split(' ',1)]
      params = [_p.strip() for _p in params.split('=',1)]
      
      print(f'{i=}, {params=}')
      if i == 'help':
        print('тут должна быть справка, но долго писать, поэтому смотри код')
        print(f'вот все команды {available_commands}')
      elif i == 'test':
          if params[0] == '':
            print(f'нужен хотя бы один параметр, доступные параметры {test_url_dict.keys()}')
            continue
          result_url = test_url_dict.get(params[0],None)
          if result_url is None:
            print(f'неверный параметр {params[0]}, доступные параметры {test_url_dict.keys()}')
            continue
          selected_type = params[0]
          print(f'выбран для теста {test_url_dict[selected_type]=}')
            
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
          driver.get(test_url_dict[selected_type])
          html_result = driver.page_source
          if selected_type == '1':
            status = _load_ya_features.check_html_features(html_result)
            print(f'{status=}')
          else:
            if not 'orgpage-header-view__header' in html_result:
              print('not found orgpage-header-view__header')
            else:
              print('OK! found orgpage-header-view__header')
          
            # if 'passport.yandex.ru' in html_result:
            #   print('need pass')
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
        
        res = requests.get(test_url_dict[selected_type], headers=headers, verify=False, timeout=5)
        #get_random_second()
        print(res.status_code)
        html_result = res.text
        if selected_type == '1': #features
          status = _load_ya_features.check_html_features(html_result)
          print(f'{status=}')
        else:          
          if not 'orgpage-header-view__header' in html_result:
            print('not found orgpage-header-view__header')
          else:
            print('OK! found orgpage-header-view__header')
          
          if 'passport.yandex.ru' in html_result:
            print('need pass')

      elif i == 'del':        
        driver.delete_all_cookies()
        print('delete all cookies')
      else:
        print(f'Ошибка ввода команды, доступны следующие команды: {available_commands}')
print('done')