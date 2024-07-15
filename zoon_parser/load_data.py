
import os

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


def get_random_second():
    t = random.choice([2,3,4,1])
    time.sleep(t)
    logging.debug(f'time.sleep({t=})')



def load_page_if_not_exists(base_folder, page_name, city: str, full_url:str,replace=False, timeout=120,proxy=None,headers=None):
    path = common.get_folder(base_folder.rstrip('/\\') + '/zoon', city, 'pages')
    full_name = f'{path}/{page_name}'
    if not replace and common.isfile(full_name):
        #logging.debug(f'ready load {full_name=}')
        return
    logging.debug(f'request {full_url=}')
    proxies = {'http': proxy,'https': proxy}
    res = requests.get(full_url,headers=headers,verify=False,timeout=timeout,proxies=proxies)
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

def get_full_name_for_search(base_folder, city_line, point, zoom = 18):
    page_name = f'{zoom}_{point[0]}_{point[1]}.json'
    path = common.get_folder(base_folder.rstrip('/\\') + '/zoon', city_line['city'],'search_p_json')
    full_name = f'{path}/{page_name}'
    return full_name


def save_json_by_search_page(base_folder, city_line:dict,point:tuple,replace=False, timeout=120, proxy=None,headers=None):
    zoom = 18
    full_name = get_full_name_for_search(base_folder, city_line, point,zoom=zoom)
    if replace or not common.isfile(full_name):
        html_result = get_html_by_point_search_company(base_folder, city_line,point,zoom,timeout=timeout, proxy=proxy,headers=headers)
        result_orgs = parse_data.get_items(html_result)
        with open(full_name,'w', encoding='utf') as f:
            json.dump(result_orgs,f, ensure_ascii=False)
        logging.debug(f'write result to file {full_name=}')
    else:
        logging.debug(f'already exists {full_name=}')
    return full_name

def get_html_by_point_search_company(base_folder, city_line:dict, point:tuple, zoom:int, timeout=120, proxy=None, headers = None):
    '''
    Пытаемся получить html со страницы поиска из zoon.ru.
    html кешируется.
    В некоторых случаеях приходит json, а в некоторых html.
    сначала проверяем присутствует ли html, тогда возвращаем.
    Если нет, тогда делаем запрос в zoon. Пытаемся получить данные как json. Если выходит ошибка парсинга json, тогда это чисто html.
    Записываем в файл.
    Если ошибки нет и это json, тогда извлекаем из него html и записываем в файл
    '''
    page_name = f'{zoom}_{point[0]}_{point[1]}.html'
    path = common.get_folder(base_folder.rstrip('/\\') + '/zoon', city_line['city'],'search_p')
    full_name = f'{path}/{page_name}'
    html_result = ''
    #logging.debug(f'{full_name=}')
    if not common.isfile(full_name):
        base_url = ''
        if city_line['is_domain'] == True:
            base_url = f"https://{city_line['city']}.zoon.ru"
        else:
            base_url = f"https://zoon.ru/{city_line['city']}"
        
        if headers is not None:
            headers['Origin'] = base_url
            headers['Referer'] = base_url

        #full_url = f'{base_url}/json-rpc/v1/'
        full_url = f'{base_url}/restaurants/?action=listJson&type=service'
        #logging.debug(f'request {full_url=}')

        bounds = common.get_rectangle_bounds(point)
        data = f'need%5B%5D=items&need%5B%5D=points&page=1&search_query_form=1&bounds%5B%5D={bounds[0][1]}&bounds%5B%5D={bounds[0][0]}&bounds%5B%5D=={bounds[1][1]}&bounds%5B%5D={bounds[1][0]}'
        proxies = {'http': proxy,'https': proxy}

        logging.debug(f'{full_url=}')
        logging.debug(f'{headers=}')
        logging.debug(f'{data=}')
        logging.debug(f'{proxies=}')
        logging.debug(f'{timeout=}')
        res = requests.post(full_url, data=data, headers=headers,timeout=timeout, verify=False,proxies=proxies)
        
        logging.debug(f'{res.status_code=}')

        if res.status_code == 200:
            res_json = ''
            is_error = False
            try:
                res_json = res.json()
            except Exception as ex:
                is_error=True
                logging.error(full_name,exc_info=True)
            if not is_error:
                html_result = parse_data.get_html_from_json_str(res_json)
            if is_error:
                # в некоторых случаях вместо json файла (в котором находится html), приходит сразу html с данными
                #  тогда идет проверка что полученый текст начиается с тега html и возвращаем эти данные 
                if '<html' in res.text:
                    if common.isfile(full_name):
                        logging.warn(f'delete file {full_name}')
                        os.remove(full_name)
                    html_result = res.text
                else:
                    logging.error(f'{res.text=}')
                    raise(Exception(f'not correct data by {full_url=}'))
            with open(full_name, 'w',encoding='UTF-8') as f:
                f.write(html_result)
            logging.debug(f'write to file {full_name=}')
            get_random_second()
        else:
            logging.error(f'{res.text=}')
            raise(Exception(f'{res.text=}'))

    else:
        with open(full_name,'r',encoding='UTF-8') as f:
            html_result = f.read()
        logging.debug(f'read from file {full_name=}')

    return html_result

