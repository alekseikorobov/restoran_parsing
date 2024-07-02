import requests
import warnings
import random
import time
import os
import re
import json
from bs4 import BeautifulSoup
import common
import logging
warnings.filterwarnings("ignore")

## ПОЛУЧЕНИЕ M[ID] ПО КАЖДОМУ ТИПУ


def get_random_second():
    return random.choice([2,3,4, 1])

def get_html_type_all(city:str):
    full_url = 'https://zoon.ru/msk/restaurants/type/'
    full_name = 'data/msk/type_all.html'
    html_result = ''
    if not common.isfile(full_name):
        logging.debug(f'load {full_url=}')
        headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
            ,'Accept-Encoding':'gzip, deflate, br'
            ,'Accept-Language':'en-US,en;q=0.9,ru;q=0.8'
            ,'Cookie':'locale=ru_RU; AATestGlobal=variation; anon_id=20230920095826SWst.2ddd; _ga=GA1.2.1291800659.1695193108; _gid=GA1.2.1223008631.1695193108; _ym_uid=1695193108677982975; _ym_d=1695193108; city=msk; sid=71ca6e30650be67c6d0da965512048; _ym_isad=2; _ga_KK9RGD935B=GS1.2.1695283729.7.1.1695284684.30.0.0'
            ,'Sec-Ch-Ua':'"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"'
            ,'Sec-Ch-Ua-Mobile':'?0'
            ,'Sec-Ch-Ua-Platform':'"Windows"'
            ,'Sec-Fetch-Dest':'document'
            ,'Sec-Fetch-Mode':'navigate'
            ,'Sec-Fetch-Site':'none'
            ,'Sec-Fetch-User':'?1'
            ,'Upgrade-Insecure-Requests':'1'
            ,'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
        }
        res = requests.get(full_url,headers=headers,verify=False)
        with open(full_name, 'w', encoding='utf') as f:
            f.write(res.text)
        time.sleep(get_random_second())
    
    with open(full_name,'r',encoding='utf') as f:
        html_result = f.read()

    logging.debug(f'{len(html_result)=}')

    return html_result

def get_type_as_json(html_result):
    soup = BeautifulSoup(html_result,"html.parser")
    hub_list_elements = soup.find_all(class_='hub-list js-hub-list') #hub-list-title
    logging.debug(f'find hub-list {len(hub_list_elements)=}')
    result_list = []
    for hub_list_element in hub_list_elements:
        sub_hub_list_elements = hub_list_element.find_all(class_='z-text--default')
        logging.debug(f'find sub - hub-list {len(sub_hub_list_elements)=}')
        for sub_hub_list_element in sub_hub_list_elements:
            #пропускаем заголовки
            if 'z-text--bold' in sub_hub_list_element.attrs['class']:
                continue
            if sub_hub_list_element.name == 'a':
                result_list.append({
                    'type_url':sub_hub_list_element.attrs['href'],
                    'type_name':sub_hub_list_element.text.strip()
                })
    return result_list

def get_result_type_list(html_result):
    full_name = 'data/msk/type_all.json'
    if not common.isfile(full_name):
        logging.debug('Start parse html_result')
        result_type_list = get_type_as_json(html_result)
        logging.debug(f'get - {len(result_type_list)=}')
        with open(full_name, 'w', encoding='utf') as f:
            json.dump(result_type_list,f, ensure_ascii=False)
    else:
        logging.debug(f'json {full_name=} already exists')

    with open(full_name, 'r', encoding='utf') as f:
        result_type_list = json.load(f)

    logging.debug(f'load - {len(result_type_list)=}')
    return result_type_list

def get_html_by_one_type(city,type_json):
    full_url = type_json['type_url']
    type_name = type_json['type_name']
    folder = common.get_folder(city,'type_list',None)
    full_name = f'{folder}/type_{type_name}.html'
    logging.debug(f'get_html_by_one_type by {type_name=} {full_url=}')
    html_result = ''
    if not common.isfile(full_name):
        headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
            ,'Accept-Encoding':'gzip, deflate, br'
            ,'Accept-Language':'en-US,en;q=0.9,ru;q=0.8'
            ,'Cookie':'locale=ru_RU; AATestGlobal=variation; anon_id=20230920095826SWst.2ddd; _ga=GA1.2.1291800659.1695193108; _gid=GA1.2.1223008631.1695193108; _ym_uid=1695193108677982975; _ym_d=1695193108; city=msk; sid=71ca6e30650be67c6d0da965512048; _ym_isad=2; _ga_KK9RGD935B=GS1.2.1695283729.7.1.1695284684.30.0.0'
            ,'Sec-Ch-Ua':'"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"'
            ,'Sec-Ch-Ua-Mobile':'?0'
            ,'Sec-Ch-Ua-Platform':'"Windows"'
            ,'Sec-Fetch-Dest':'document'
            ,'Sec-Fetch-Mode':'navigate'
            ,'Sec-Fetch-Site':'none'
            ,'Sec-Fetch-User':'?1'
            ,'Upgrade-Insecure-Requests':'1'
            ,'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
        }
        logging.debug(f'load {full_url=} to {full_name=}')
        res = requests.get(full_url,headers=headers,verify=False)
        with open(full_name, 'w', encoding='utf') as f:
            f.write(res.text)
        time.sleep(get_random_second())
    with open(full_name,'r',encoding='utf') as f:
        html_result = f.read()

    return html_result

def get_mid_from_type_html(html_result:str):
    patern = '\"key\"\:\"m\[(.*?)\]\"'
    res = re.search(patern,html_result)
    if res is None:
        logging.debug(f'Not found key[m] from html {len(html_result)}=')
        return ''
    return res.group(1)

def get_result_with_mid_type_list(result_type_list):
    full_name = 'data/msk/type_all_with_mid.json'
    if not common.isfile(full_name):
        for type_json in result_type_list:
            html_result = get_html_by_one_type('city',type_json)
            mid = get_mid_from_type_html(html_result)
            type_json['mid'] = mid
        with open(full_name, 'w', encoding='utf') as f:
            json.dump(result_type_list,f, ensure_ascii=False)

    else:
        logging.debug(f'json {full_name=} already exists')
    # with open(full_name, 'r', encoding='utf') as f:
    #     result_type_list = json.load(f)

    # print(f'load - {len(result_type_list)=}')
    # return result_type_list

def start_load():
    logging.debug('Start load')
    html_result = get_html_type_all('')
    result_type_list = get_result_type_list(html_result)
    get_result_with_mid_type_list(result_type_list)
    logging.debug('done')


if __name__ == '__main__':
    start_load()

