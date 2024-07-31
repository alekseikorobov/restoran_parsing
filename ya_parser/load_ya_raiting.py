import pandas as pd
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

def get_folder(base_folder, city: str, sub_folder: str) -> str:
  path = f'{base_folder}/yandex_r/{city}/{sub_folder}'.rstrip('/\\')
  if not os.path.isdir(path):
    os.makedirs(path)
  return path


def get_raiting_html(base_folder, city_code, id:str, proxy = None,timeout=5,headers = None,is_replase=False):
  path = get_folder(base_folder,city_code,'html')
  full_name = f'{path}/{id}.html'
  result_html = ''
  if is_replase or not common.isfile(full_name):
    full_url = f'https://yandex.ru/maps-reviews-widget/{id}?size=m&comments'
    #print(f'load from {full_url=}')
    proxies = {'http': proxy,'https': proxy}
    res = requests.get(full_url, headers=headers, verify=False, proxies=proxies, timeout=timeout)
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

def get_json_ya_raiting(base_folder, city_code, ya_id, proxy = None, timeout=5,headers=None,is_replase=False) -> dict:
  html_result = get_raiting_html(base_folder, city_code, ya_id, proxy=proxy, timeout=timeout,headers=headers,is_replase=is_replase)
  json_result = parse_html_get_json(html_result)
  return json_result
