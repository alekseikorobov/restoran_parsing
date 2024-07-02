
import os
#os.chdir('C:\work\map_api')
import requests
import urllib.parse as parse
import re
import common.common as common
import zoon_parser.parse_data as parse_data
import time
import random
import zoon_parser.map_dict as map_dict
import json
import warnings
import logging
warnings.filterwarnings("ignore")
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.INFO)

# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s [%(levelname)s] %(message)s",
#     handlers=[
#         logging.FileHandler("logs/load_data.log",encoding='utf-8'),
#         logging.StreamHandler()
#     ]
# )

def get_random_second():
    time.sleep(random.choice([2,3,4, 1]))


import hashlib

base_folder = f'{os.path.abspath("")}/data/zoon'

def load_page_if_not_exists(city: str, full_url:str,replace=False):
    path = common.get_folder(base_folder, city, 'pages', is_page = True)
    page_name = ''
    if full_url[0] == '/':
        res = hashlib.sha1(full_url.encode())
        page_name = res.hexdigest()
        full_url = f'https://zoon.ru{full_url}'
    else:
        #page_name = 'kafe_lelo_na_prospekte_vernadskogo'
        page_name = full_url.rstrip('/').split('/')[-1]
    
    if page_name == '':
        raise(Exception('can not define page name by url='+full_url))
    full_name = f'{path}/{page_name}'
    if not replace and os.path.isfile(full_name):
        #logging.debug(f'ready load {full_name=}')
        return

    headers = common.get_header_dict_from_txt('zoon_parser/headers.txt')
    headers['Cookie'] = get_cookies('zoon_parser/cookie_for_details.txt')
    
    logging.debug(f'request {full_url=}')
    res = requests.get(full_url,headers=headers,verify=False)
    if res.status_code == 512:
        raise(Exception('can not load data'))
    
    with open(full_name, 'w', encoding='utf-8') as f:
        f.write(res.text)
    get_random_second()



def get_types():
    page_name = 'types.json'

    #page_name = 'kafe_lelo_na_prospekte_vernadskogo'
    path = common.get_folder(base_folder,'msk','add_info',None)
    full_name = f'{path}/{page_name}'
    logging.debug(f'{full_name=}')
    if os.path.isfile(full_name):
        #logging.debug(f'ready load {full_name=}')
        return

    headers = {
        # ,"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        # , "Accept-Encoding":"gzip, deflate, br"
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36", "Cookie": "locale=ru_RU; AATestGlobal=variation; anon_id=20230920095826SWst.2ddd; _ga=GA1.2.1291800659.1695193108; _gid=GA1.2.1223008631.1695193108; _ym_uid=1695193108677982975; _ym_d=1695193108; _ym_isad=2; sid=d02f3aa4650ab90d9feea242783596; city=msk; _ga_KK9RGD935B=GS1.2.1695204276.4.1.1695204590.23.0.0", 'Sec-Ch-Ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"', 'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2OTUyMDE1NTAsImV4cCI6MTY5NTI4Nzk1MCwidHlwZSI6MH0.R-QDRRteUJAAF5DZz7ZsAqtxGPvg4akN8LvSd1FvynI'
    }
    full_url = 'https://zoon.ru/json-rpc/v1/'
    logging.debug(f'request {full_url=}')
    data = [{"jsonrpc": "2.0", "id": 0, "method": "catalogFilter.list",
             "params":
             {
                 "city": "msk", "category": "restaurants", "sort_field": "photorating", "sort_order": "desc",
                 "show_geo_location": True, "network": False}}]
    # data = [
    #     {"jsonrpc": "2.0", "id": 0, "method": "catalogFilter.list", "params":
    #      {"city": "msk", "category": "restaurants", "sort_field": "photorating",
    #       "sort_order": "desc", 
    #       "m": {"4f84a6c93c72dddc66000019": "1"},
    #       "show_geo_location": True, "network": False}}]
    res = requests.post(full_url, json=data, headers=headers)
    with open(full_name, 'w', encoding='utf') as f:
        json.dump(res.json(), f, ensure_ascii=False)

    get_random_second()
#get_types()


def pretty_file_name(filename:str):
    return re.sub(r'[\\/*?:"<>|]',"_", filename)
               
def get_cookies(file_path):
    if not os.path.isfile(file_path):
        raise(Exception(f'file not found {file_path=}'))
    cooks = ''
    with open(file_path,'r') as f:
        cooks = f.read()
    return cooks

def get_search_text(search_text):
    split_text = search_text.split(' ')
    if len(split_text)>4:
        #logging.warning(f'Входной запрос имеет {len(split_text)} токенов, максимальное 5')
        search_text = ' '.join(split_text[0:4])
        logging.warning(f'Входная строка обрезана до "{search_text}" ')
    return search_text.lower()

driver:WebDriver|None = None
is_driver = True

def get_driver() -> WebDriver:
    global driver
    if driver is None:
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
    return driver

def save_json_by_search_page(city_line:dict,point:tuple,replace=False):
    zoom=18
    page_name = f'{zoom}_{point[0]}_{point[1]}.json'
    path = common.get_folder(base_folder, city_line['city'],'search_p_json',None)
    full_name = f'{path}/{page_name}'
    if replace or not os.path.isfile(full_name):
        html_result = get_html_by_point_search_company(city_line,point,zoom)
        result_orgs = parse_data.get_items(html_result)
        with open(full_name,'w', encoding='utf') as f:
            json.dump(result_orgs,f, ensure_ascii=False)
        logging.debug(f'write result to file {full_name=}')
    else:
        logging.debug(f'already exists {full_name=}')

def get_html_by_point_search_company(city_line:dict, point:tuple, zoom:int):

    page_name = f'{zoom}_{point[0]}_{point[1]}.json'
    path = common.get_folder(base_folder, city_line['city'],'search_p',None)
    full_name = f'{path}/{page_name}'

    #logging.debug(f'{full_name=}')
    if not os.path.isfile(full_name):
        headers = common.get_header_dict_from_txt('zoon_parser/headers_for_search_by_p.txt')
        base_url = ''
        if city_line['is_domain'] == True:
            base_url = f"https://{city_line['city']}.zoon.ru"
        else:
            base_url = f"https://zoon.ru/{city_line['city']}"
        headers['Origin'] = base_url
        headers['Referer'] = base_url

        full_url = f'{base_url}/json-rpc/v1/'
        full_url = f'{base_url}/restaurants/?action=listJson&type=service'
        #logging.debug(f'request {full_url=}')

        bounds = common.get_rectangle_bounds(point)
        logging.debug(f'{full_url=}')
        data = f'need%5B%5D=items&page=1&search_query_form=1&bounds%5B%5D={bounds[0][1]}&bounds%5B%5D={bounds[0][0]}&bounds%5B%5D={bounds[1][1]}&bounds%5B%5D={bounds[1][0]}'
        res = requests.post(full_url, data=data, headers=headers)
        
        logging.debug(f'{res.status_code=}')

        if res.status_code == 200:
            res_json = ''
            is_error = False
            with open(full_name, 'w',encoding='UTF-8') as f:
                try:
                    res_json = res.json()
                except Exception as ex:
                    is_error=True
                    logging.error(full_name,exc_info=True)
                if not is_error:
                    json.dump(res_json, f, ensure_ascii=False)
            if is_error and os.path.isfile(full_name):
                # в некоторых случаях вместо json файла (в котором находится html), приходит сразу html с данными
                #  тогда идет проверка что полученый текст начиается с тега html и возвращаем эти данные 
                if '<html' in res.text:
                    logging.warn(f'delete file {full_name}')
                    os.remove(full_name)
                    return res.text
                else:
                    raise(Exception(f'not correct data by {full_name=}'))
            get_random_second()
        else:
            logging.error(f'{res.text=}')
            raise(Exception(f'{res.text=}'))

    html = parse_data.get_html_from_json_file(full_name)

    return html

def get_html_by_point_search_company_old(city_line:dict,point:tuple,zoom:int):
    #https://zoon.ru/msk/restaurants/?search_query_form=1&center%5B%5D=55.75223851173203&center%5B%5D=37.2281057496209&zoom=18
    page_name = f'{zoom}_{point[0]}_{point[1]}.html'
    path = common.get_folder(base_folder, city_line['city'],'search_p',None)
    full_name = f'{path}/{page_name}'
    
    html_result = ''

    if not os.path.isfile(full_name):
        driver = get_driver()
        base_url = ''
        if city_line['is_domain'] == True:
            base_url = f"https://{city_line['city']}.zoon.ru"
        else:
            base_url = f"https://zoon.ru/{city_line['city']}"

        full_url = f'{base_url}/restaurants/?search_query_form=1&center%5B%5D={point[0]}&center%5B%5D={point[0]}&zoom={zoom}'

        if is_driver:
            driver.get(full_url)
            html_result = driver.page_source
        else:
            headers = common.get_header_dict_from_txt('zoon_parser/headers.txt')
            headers['Cookie'] = get_cookies('zoon_parser/cookie_for_search.txt')
    
            res = requests.get(full_url,headers=headers,verify=False)
            if res.status_code == 512:
                raise(Exception('can not load data'))

        if 'Zoon.ru для вас недоступен, к сожалению' in html_result:
            raise(Exception('can not load data!'))
        with open(full_name, 'w', encoding='utf-8') as f:
            f.write(html_result)
        get_random_second()
    else:
        #logging.debug(f'ready load {full_name=}')    
        with open(full_name, 'r', encoding='utf-8') as f:
            html_result = f.read()
        if 'Zoon.ru для вас недоступен, к сожалению' in html_result:
            raise(Exception('can not load data!'))
        
    logging.debug(f'{len(html_result)=}')
    return html_result

def get_html_by_search_company(city:str, search_text:str,replace=False,load=True):
    driver = get_driver()
    html_result = ''    
    
    search_text = get_search_text(search_text)

    page_name = f'{pretty_file_name(search_text)}.html'
    path = common.get_folder(base_folder, city,'search',None)
    full_name = f'{path}/{page_name}'
    
    search_text = parse.quote(search_text)

    if replace or not os.path.isfile(full_name):
        
        if not load:
            raise(Exception(f'not found file {full_name} and can not load'))

        full_url = f'https://zoon.ru/search/?city={city}&query={search_text}'
        logging.debug(f'request {full_url=} and save to {full_name=}')

        if is_driver:
            driver.get(full_url)
            html_result = driver.page_source
        else:
            headers = common.get_header_dict_from_txt('zoon_parser/headers.txt')
            headers['Cookie'] = get_cookies('zoon_parser/cookie_for_search.txt')
    
            res = requests.get(full_url,headers=headers,verify=False)
            if res.status_code == 512:
                raise(Exception('can not load data'))

        if 'Zoon.ru для вас недоступен, к сожалению' in html_result:
            raise(Exception('can not load data!'))
        with open(full_name, 'w', encoding='utf-8') as f:
            f.write(html_result)
        get_random_second()
    else:
        #logging.debug(f'ready load {full_name=}')
        pass
    
    with open(full_name, 'r', encoding='utf-8') as f:
        html_result = f.read()
    
    if 'Zoon.ru для вас недоступен, к сожалению' in html_result:
        raise(Exception('can not load data!'))
        
    logging.debug(f'{len(html_result)=}')
    
    return html_result

# import hyper.contrib as hyper_c
# import importlib
# importlib.reload(hyper_c)
#from hyper.contrib import HTTP20Adapter

def get_page(city,obj,pageid = 1):

    obj_key = obj['key']
    obj_name = obj['name'] if obj['name'] != "" else obj['title'] 
    logging.debug(f'{obj_key=}, {obj_name=}')
    #&show_prices_on_map=1
    
    full_url = f'https://zoon.ru/{city}/restaurants/?action=listJson&type=service&show_prices_on_map=1'
    #pageid = 2
    data = f"need%5B%5D=items&page={pageid}&search_query_form=1&m%5B{obj_key}%5D=1"

    full_name = f"{common.get_folder(base_folder, city, obj_name)}/page_{pageid}.json"

    if os.path.isfile(full_name):
        logging.debug(f'already exists {full_name=}')
        return

    headers = {
        # ,"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        # , "Accept-Encoding":"gzip, deflate, br"
        #"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36", 
        #"Cookie": "locale=ru_RU; AATestGlobal=variation; anon_id=20230920095826SWst.2ddd; _ga=GA1.2.1291800659.1695193108; _gid=GA1.2.1223008631.1695193108; _ym_uid=1695193108677982975; _ym_d=1695193108; _ym_isad=2; sid=d02f3aa4650ab90d9feea242783596; city=msk; _ga_KK9RGD935B=GS1.2.1695204276.4.1.1695204590.23.0.0", 'Sec-Ch-Ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"', 'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2OTUyMDE1NTAsImV4cCI6MTY5NTI4Nzk1MCwidHlwZSI6MH0.R-QDRRteUJAAF5DZz7ZsAqtxGPvg4akN8LvSd1FvynI'
        # ":authority":"zoon.ru"
        # ,":method":"POST"
        # ,":path":"/msk/restaurants/?action=listJson&type=service&show_prices_on_map=1"
        # ,":scheme":"https"
        "Accept":"*/*"
        ,"Accept-Encoding":"gzip, deflate, br"
        ,"Accept-Language":"en-US,en;q=0.9,ru;q=0.8"
        ,"Content-Length":"77"
        ,"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"
        ,"Cookie":"locale=ru_RU; AATestGlobal=variation; anon_id=20230920095826SWst.2ddd; _ga=GA1.2.1291800659.1695193108; _gid=GA1.2.1223008631.1695193108; _ym_uid=1695193108677982975; _ym_d=1695193108; _ym_isad=2; sid=d02f3aa4650ab90d9feea242783596; city=msk; _gat=1; _ga_KK9RGD935B=GS1.2.1695204276.4.1.1695209725.20.0.0"
        ,"Origin":"https://zoon.ru"
        #,"Referer":f"https://zoon.ru/{city}/restaurants/type/{obj_key}/page-{pageid}/"
        ,"Sec-Ch-Ua":'"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"'
        ,"Sec-Ch-Ua-Mobile":"?0"
        ,"Sec-Ch-Ua-Platform":'"Windows"'
        ,"Sec-Fetch-Dest":"empty"
        ,"Sec-Fetch-Mode":"cors"
        ,"Sec-Fetch-Site":"same-origin"
        ,"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        ,"X-Requested-With":"XMLHttpRequest"    
    }

    logging.debug(f'request {full_url=}')

    # s = requests.Session()
    # s.mount("https://zoon.ru/msk/restaurants", hyper_c.HTTP20Adapter())

    res = requests.post(full_url,data=data, headers=headers,verify=False)
    with open(full_name, 'w', encoding='utf') as f:
        f.write(res.text)
    get_random_second()

    obj_result = json.loads(res.text)
    if not 'success' in obj_result:
        raise(Exception('not key success!!'))
    
    if not obj_result['success']:
        raise(Exception('not success!!!'))
    
    if not 'html' in obj_result:
        raise(Exception('not key html!!'))
    len_html = len(obj_result['html'])
    if len_html == 0:
        raise(Exception('html empty!!!'))

    logging.debug(f'{len_html=}')
    logging.debug(f'\tsaved {full_name=}')


    #need%5B%5D=items&page=2&search_query_form=1&m%5B4f84a6c93c72dddc66000019%5D=1
# obj = {"title": "бар", "name":"bary","key": "4f84a6c93c72dddc66000019"}
# obj = {"title": "пекарня", "name":"","key": "59683fb064288e27c6149cc7"}
#get_page('msk',obj,12)

def start_load():
    for obj in map_dict.list_map_dict:
        count_error = 0
        max_error = 3
        for pageId in range(1,11):
            try:
                #больше не применимо все рестораны не скачиваем
                # скачиваем только по поиску
                get_page('msk',obj, pageId)
                count_error = 0
            except Exception as ex:
                logging.error('error',exc_info=True)
                count_error += 1
                if count_error > max_error:
                    logging.error('break by ', exc_info=True)
                    break


# if __name__ == '__main__':
#     init_driver()
#     start_load()