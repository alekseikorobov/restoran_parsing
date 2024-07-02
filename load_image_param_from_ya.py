
# см как алгоритм - "docs\Алгоритм получения фоток из Яндекс по организациям.md"

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
import warnings
warnings.filterwarnings("ignore")
import logging
import os

logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s\t%(filename)s\t%(funcName)s\t[%(levelname)s]\t%(lineno)d\t%(message)s",
            handlers=[
                logging.FileHandler('logs/all_logs_20231108.log',encoding='utf-8'),
                logging.StreamHandler()
            ]
        )


async def get_random_second():
  await asyncio.sleep(random.choice([1,2])) #,3,4

async def get_gallery_html_by_org(url, city_name, ya_id):
  city_line = dict_city.get_line_by_city_name(city_name)
  city_code = city_line['city']
  path = load_ya_raiting.get_folder(city_code,'gallery_html')
  full_name = f'{path}\\{ya_id}.html'
  result_html = ''
  if not await aiofiles.os.path.isfile(full_name):
    headers = common.get_header_dict_from_txt('ya_parser/headers_gallery.txt')
    async with aiohttp.ClientSession() as session:
      logging.debug(f'load {url}')
      async with session.get(url,headers=headers, verify_ssl=False, timeout=5) as response:
        if response.status == 200:
          result_html = await response.text()
          if 'Please confirm that you and not a robot are sending requests' in result_html:
            raise(Exception('need capcha. Update - ya_parser/headers_gallery.txt'))
          async with aiofiles.open(full_name,'w',encoding='UTF-8') as f:
            await f.write(result_html)
            logging.debug(f'save to {full_name=}')
        else:
          logging.warning(f'get {response.status=} skip save')
        await get_random_second()
  else:
    logging.debug(f'get from {full_name=}')
    async with aiofiles.open(full_name,'r',encoding='UTF-8') as f:
      result_html = await f.read()
  return result_html

async def get_full_json_from_gallery(html_str):
  soup = BeautifulSoup(html_str,"html.parser")
  state_view_element = soup.find(class_ = 'state-view')
  if state_view_element is None:
    raise(Exception('not found script element by class state-view'))
  text = state_view_element.get_text(' ')
  json_result = json.loads(text)
  return json_result

async def get_param_from_gallery(url,city_name, ya_id):
  city_line = dict_city.get_line_by_city_name(city_name)
  city_code = city_line['city']
  path = load_ya_raiting.get_folder(city_code,'gallery_param_json')
  full_name = f'{path}\\{ya_id}.json'
  json_result = None
  system_links = []
  session_id = None
  if not await aiofiles.os.path.isfile(full_name):
    result_html = await get_gallery_html_by_org(url,city_name, ya_id)
    if result_html == '':
      logging.warning('not exists html')
      return session_id, system_links
    json_result  = await get_full_json_from_gallery(result_html)
    logging.debug(f'write - {full_name}')
    async with aiofiles.open(full_name,'w',encoding='UTF-8') as f:
      await f.write(json.dumps(json_result))
  else:
    logging.debug(f'read - {full_name}')
    async with aiofiles.open(full_name,'r',encoding='UTF-8') as f:
      json_result = json.loads(await f.read())

  if 'photos' in json_result['stack'][0]['results']['items'][0]:
    system_links = [item['urlTemplate'] for item in json_result['stack'][0]['results']['items'][0]['photos']['items']]
    session_id = json_result['config']['counters']['analytics']['sessionId']

  return session_id, system_links

async def get_new_csrf_token():
  url = 'https://yandex.ru/maps/api/photos/getByBusinessId?ajax=1'
  async with aiohttp.ClientSession() as session:
    logging.debug(f'load {url}')
    headers = common.get_header_dict_from_txt('ya_parser/headers_token.txt')
    async with session.get(url,headers=headers, verify_ssl=False, timeout=5) as response:
      result_json = await response.json()
      await get_random_second()
      if result_json is None:
        raise(Exception('return empty'))
  if 'type' in result_json and result_json['type'] == 'captcha':
    logging.debug(result_json)
    raise(Exception('need capcha'))
  return result_json['csrfToken']

def convert_url_to_fixed_top(system_links):

  result = []
  for system_link in system_links:
    message_bytes = system_link.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    result.append(base64_message)
  return ','.join(result)

def rshift(val, n): return val>>n if val >= 0 else (val+0x100000000)>>n

def get_check_sum(param_str):
  # магическая функция для контрольной суммы из js яндекса:
  # return t ? String(function(e) {
  #     for (var t = e.length, n = 5381, r = 0; r < t; r++)
  #         n = 33 * n ^ e.charCodeAt(r);
  #     return n >>> 0
  # }(t)) : ""

  n = 5381
  for x in param_str:
      n = np.int32(33 * n) ^ ord(x)
  return rshift(n, 0)

async def get_gallery_json(full_params):
  url = f'https://yandex.ru/maps/api/photos/getByBusinessId?{full_params}'
  async with aiohttp.ClientSession() as session:
    logging.debug(f'load {url}')
    headers = common.get_header_dict_from_txt('ya_parser/headers_token.txt')
    async with session.get(url,headers=headers, verify_ssl=False, timeout=5) as response:
      result_json = await response.json()
      await get_random_second()
      if result_json is None:
        raise(Exception('return empty'))
  return result_json

async def get_full_params(session_id, system_links, ya_id):
    csrf_token = await get_new_csrf_token()
    #csrf_token='8b770403c4f3e9cbd454f707f549581cf4bae0e7:1699435665'
    csrf_token_q = requests.utils.quote(csrf_token)
    logging.debug(f'{csrf_token=}')

    fixed_top = convert_url_to_fixed_top(system_links)
    fixed_top_q = requests.utils.quote(fixed_top)

    param_str = f"ajax=1&csrfToken={csrf_token_q}&fixed_top={fixed_top_q}&id={ya_id}&lang=ru_RU&sessionId={session_id}"

    param_s = get_check_sum(param_str)

    full_params = f'{param_str}&s={param_s}'
    return full_params

async def load_param_image_by_id(city_name, ya_id):
  logging.debug(f'start {city_name=} {ya_id=}')

  city_line = dict_city.get_line_by_city_name(city_name)
  city_code = city_line['city']
  path = load_ya_raiting.get_folder(city_code,'gallery_json')
  full_name = f'{path}\\{ya_id}.json'
  json_result = None
  if not await aiofiles.os.path.isfile(full_name):
    json_result = load_ya_raiting.get_json_ya_raiting(city_name, ya_id)
    ya_link_org = json_result['ya_link_org']
    if ya_link_org == '' or ya_link_org is None:
      raise(Exception(f'link not correct by id {ya_id}'))
    
    logging.debug(f'get {ya_link_org=}')
    ya_link_org_gallery = ya_link_org.strip('/') + '/gallery/'
    logging.debug(f'get param from {ya_link_org_gallery=}')
    session_id, system_links = await get_param_from_gallery(ya_link_org_gallery,city_name, ya_id)
    if session_id is None or len(system_links) == 0:
      logging.warning(f'NOT PHOTO BY {ya_id=}')
      return
    logging.debug(f'{session_id=} {len(system_links)=}')
    
    full_params = await get_full_params(session_id, system_links, ya_id)
    
    json_result = await get_gallery_json(full_params)
    logging.debug(f'write {len(json_result)=} - {full_name=}')

    if 'type' in json_result and json_result['type'] == 'captcha':
      logging.debug(json_result)
      raise(Exception('need capcha'))
    
    if 'csrfToken' in json_result:
      raise(Exception('need update csrfToken'))

    async with aiofiles.open(full_name,'w',encoding='UTF-8') as f:
      await f.write(json.dumps(json_result, ensure_ascii=False))
  else:
    logging.debug(f'read - {full_name}')
    async with aiofiles.open(full_name,'r',encoding='UTF-8') as f:
      json_result = json.loads(await f.read())
  logging.debug(f'{len(json_result)=}')

  return json_result

def get_obj_iterator(json_result,ya_id,city_name):
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

async def main():
  path_from = r"tables\tran_yandex_data.xlsx"
  path_to = r'tables\all_link_image_ya.xlsx'
  df = pd.read_excel(path_from)
  df['ya_id'] = df['ya_id'].astype(str)

  data_json_list = []
  for i, row in tqdm(df.iterrows(),total=df.shape[0]):
    city_name = row['location_nm_rus']
    ya_id = str(row['ya_id']).replace('.0','')
    logging.debug(f"{city_name=},{ya_id=}")
    json_result = await load_param_image_by_id(city_name, ya_id)

    for data_json in get_obj_iterator(json_result,ya_id,city_name):
      data_json_list.append(data_json)
    
  df_result = pd.DataFrame(data_json_list)
  logging.debug(f'full data - {df_result.shape=}')
  df_result.to_excel(path_to, index=False)
  
asyncio.run(main())