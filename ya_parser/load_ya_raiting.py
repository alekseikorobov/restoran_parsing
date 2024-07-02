import pandas as pd
from tqdm import tqdm
import common.common as common
import common.dict_city as dict_city
import os
import requests
import warnings
warnings.filterwarnings("ignore")
import time,random
from bs4 import BeautifulSoup, NavigableString, PageElement, Tag

def get_random_second():
  time.sleep(random.choice([2,3, 1]))

base_folder = 'data/yandex_r'

def get_folder(city: str, sub_folder: str) -> str:
  path = f'{base_folder}/{city}/{sub_folder}'.rstrip('/')
  if not os.path.isdir(path):
    os.makedirs(path)
  return path



def get_raiting_html(city_name, id:str):

  city_line = dict_city.get_line_by_city_name(city_name, self.params.city_list)
  path = get_folder(city_line.city,'html')
  full_name = f'{path}\\{id}.html'
  result_html = ''
  if not common.isfile(full_name):
    full_url = f'https://yandex.ru/maps-reviews-widget/{id}?size=m&comments'
    #print(f'load from {full_url=}')
    headers = common.get_header_dict_from_txt('ya_parser/headers_raiting.txt')
    res = requests.get(full_url, headers=headers, verify=False, timeout=5)
    with open(full_name,'w',encoding='UTF-8') as f:
      f.write(res.text)
    #print(f'save to {full_name=}')
    get_random_second()
    result_html = res.text
  else:
    #print(f'get from {full_name=}')
    with open(full_name,'r',encoding='UTF-8') as f:
      result_html = f.read()

  return result_html

def parse_html_get_json(html_str:str):
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

def get_json_ya_raiting(city, ya_id):
  html_result = get_raiting_html(city,ya_id)
  json_result = parse_html_get_json(html_result)
  return json_result

def parse_and_get_result(row):
  if common.is_nan(row['ya_id']): return row
  ya_id = str(row['ya_id']).replace('.0','')
  json_result = get_json_ya_raiting(row['location_nm_rus'], ya_id)
  for key in json_result:
    row[key] = json_result[key]

  return row


def start(df_source:pd.DataFrame):
  tqdm.pandas()

  is_ya_cnt_category_match = df_source['ya_cnt_category_match']>0
  ya_is_match_address = df_source['ya_is_match_address']

  df_source = df_source[is_ya_cnt_category_match & ya_is_match_address]

  df_result = df_source.progress_apply(parse_and_get_result,axis=1)
  df_result = pd.DataFrame(df_result)
  return df_result
