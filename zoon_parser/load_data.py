
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


def get_random_second():
    time.sleep(random.choice([2,3,4, 1]))


import hashlib

##TODO: уточнить как правильно задавать путь
base_folder = f'{os.path.abspath("")}/data/zoon'

def load_page_if_not_exists(city: str, full_url:str,replace=False, timeout=120):
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
    if not replace and common.isfile(full_name):
        #logging.debug(f'ready load {full_name=}')
        return

    headers = common.get_header_dict_from_txt('zoon_parser/headers.txt')
    headers['Cookie'] = get_cookies('zoon_parser/cookie_for_details.txt')
    
    logging.debug(f'request {full_url=}')
    res = requests.get(full_url,headers=headers,verify=False,timeout=timeout)
    if res.status_code == 512:
        raise(Exception('can not load data'))
    
    with open(full_name, 'w', encoding='utf-8') as f:
        f.write(res.text)
    get_random_second()



def pretty_file_name(filename:str):
    return re.sub(r'[\\/*?:"<>|]',"_", filename)
               
def get_cookies(file_path):
    if not common.isfile(file_path):
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

def save_json_by_search_page(city_line:dict,point:tuple,replace=False, timeout=120):
    zoom=18
    page_name = f'{zoom}_{point[0]}_{point[1]}.json'
    path = common.get_folder(base_folder, city_line.city,'search_p_json',None)
    full_name = f'{path}/{page_name}'
    if replace or not common.isfile(full_name):
        html_result = get_html_by_point_search_company(city_line,point,zoom,timeout=timeout)
        result_orgs = parse_data.get_items(html_result)
        with open(full_name,'w', encoding='utf') as f:
            json.dump(result_orgs,f, ensure_ascii=False)
        logging.debug(f'write result to file {full_name=}')
    else:
        logging.debug(f'already exists {full_name=}')

def get_html_by_point_search_company(city_line:dict, point:tuple, zoom:int, timeout=120):

    page_name = f'{zoom}_{point[0]}_{point[1]}.json'
    path = common.get_folder(base_folder, city_line.city,'search_p',None)
    full_name = f'{path}/{page_name}'

    #logging.debug(f'{full_name=}')
    if not common.isfile(full_name):
        headers = common.get_header_dict_from_txt('zoon_parser/headers_for_search_by_p.txt')
        base_url = ''
        if city_line.is_domain == True:
            base_url = f"https://{city_line.city}.zoon.ru"
        else:
            base_url = f"https://zoon.ru/{city_line.city}"
        headers['Origin'] = base_url
        headers['Referer'] = base_url

        full_url = f'{base_url}/json-rpc/v1/'
        full_url = f'{base_url}/restaurants/?action=listJson&type=service'
        #logging.debug(f'request {full_url=}')

        bounds = common.get_rectangle_bounds(point)
        logging.debug(f'{full_url=}')
        data = f'need%5B%5D=items&need%5B%5D=points&page=1&search_query_form=1&bounds%5B%5D={bounds[0][1]}&bounds%5B%5D={bounds[0][0]}&bounds%5B%5D=={bounds[1][1]}&bounds%5B%5D={bounds[1][0]}'

        logging.debug(f'{headers=}')
        logging.debug(f'{data=}')
        res = requests.post(full_url, data=data, headers=headers,timeout=timeout)
        
        logging.debug(f'{res.status_code=}')

        if res.status_code == 200:
            res_json = ''
            is_error = False
            with open(full_name, 'w',encoding='UTF-8') as f:
                try:
                    res_json = res.json()
                except Exception as ex:
                    logging.error(ex)
                    is_error=True
                    logging.error(full_name,exc_info=True)
                if not is_error:
                    json.dump(res_json, f, ensure_ascii=False)
            if is_error:
                # в некоторых случаях вместо json файла (в котором находится html), приходит сразу html с данными
                #  тогда идет проверка что полученый текст начиается с тега html и возвращаем эти данные 
                if '<html' in res.text:
                    if common.isfile(full_name):
                        logging.warn(f'delete file {full_name}')
                        os.remove(full_name)
                    return res.text
                else:
                    logging.error('get text:')
                    print(res.text)
                    logging.error(res.text)
                    raise(Exception(f'not correct data by {full_name=}'))
            get_random_second()
        else:
            logging.error(f'{res.text=}')
            raise(Exception(f'{res.text=}'))

    html = parse_data.get_html_from_json_file(full_name)

    return html

def get_html_by_search_company(city:str, search_text:str,replace=False,load=True,timeout=120):
    driver = get_driver()
    html_result = ''    
    
    search_text = get_search_text(search_text)

    page_name = f'{pretty_file_name(search_text)}.html'
    path = common.get_folder(base_folder, city,'search',None)
    full_name = f'{path}/{page_name}'
    
    search_text = parse.quote(search_text)

    if replace or not common.isfile(full_name):
        
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
    
            res = requests.get(full_url,headers=headers,verify=False,timeout=timeout)
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