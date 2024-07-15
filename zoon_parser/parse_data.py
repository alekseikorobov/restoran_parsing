#%%
import os
import common.common as common
import json
from bs4 import BeautifulSoup, NavigableString, PageElement, Tag
import pandas as pd
import zoon_parser.map_dict as map_dict
import logging
import numpy as np
import re


def get_normal_text_from_element(element:PageElement)->str:
    
    if element is None: return ''
    
    text = element.get_text(' ',strip=True)
    text = text.replace('  ',' ')
    res_text = []
    for letter in text:
        if letter.isprintable():
            res_text.append(letter)
        else:
            res_text.append(' ')
    text_p = ''.join(res_text)
    return text_p

def get_dd_param_values(dl_element):
    result_list = []
    dd_elememt = dl_element.find(class_ = 'first-p expanding-description')
    
    if dd_elememt is None:
        dd_elememt = dl_element.find('dd')

    if dd_elememt is not None:
        a_list_elements = dd_elememt.find_all('a')
        if a_list_elements is not None:
            for a_element in a_list_elements:
                result_list.append(get_normal_text_from_element(a_element).lower())
    
    return result_list

def replace_description(text:str):
    '''
    описание ресторана решили не брать, поэтому функция больше не используется
    '''
    raise(Exception('not using this function!'))

    if str(text) == str(np.nan) or text == '' or text is None:
        return text
    paterns = [
            '\(рейтинг на (портале |)Zoon(\.ru|) (—|-) \d(\.\d|)\)'
            , 'Рейтинг .* на Zoon \- \d(\.\d|)\,.*?\.( (Достойные|Здоровая).*?\.|)'
            , '\([Рр]ейтинг на [Zz]oon(\.ru|)\)'
            , '\([Рр]ейтинг (организации|компании) на Zoon (—|-) \d(\.\d|)\)'
            , '(\(|)[Рр]ейтинг.*?Zoon(\.ru|) (—|-) \d(\.\d|)(\)|\.|)'
            , '(Полный список|Подробную информацию|Подробнее обо).*?Zoon(\.ru|)\.В (блоке|секции).*?\.'
            , '(Узнать более|Дополнительную).*?Zoon(\.ru|)\.'
            , '( |)(\(|)[Оо]ценка (пользователей|посетителей|компании от посетителей)( на |)(сайте|портале|) Zoon(\.ru|) (—|-) \d(\.\d|)(\)|\.|)'
            , 'На (портале|сайте) Zoon.*? по ссылкам.'
            , 'Рады приветствовать вас на Zoon!'
            , 'Ученики.*?Zoon.ru \d(\.\d|) (балла|баллов).'
            , 'Гости (сайта|портала) Zoon.ru.*?рейтинг (организации|компании) (—|-) \d(\.\d|) (балла|баллов)(!|\.)'
            , 'Посетители.*?поделились.*?Zoon.ru, и благодаря их оценкам рейтинг компании (—|-) \d(\.\d|) (балла|баллов)(!|\.)'
            , 'Если.*?то на портале Zoon.*?рейтинг.*? (—|-) \d(\.\d|).*?\.'
    ]
    for patern in paterns:
        match_text = re.search(patern,text)
        if match_text is not None:
            text = re.sub(patern,'',text)
    if 'zoon' in text or 'Zoon' in text:
        raise(Exception(f'in Description exists ZOON text - {text}'))
    
    return text.replace('  ',' ').strip()

fix_key = {
    'z_adress':'z_adress_2',
    'z_rating_value':'z_rating_value_2',
    'z_phone':'z_phone_2',
    'z_spurce_path':'z_source_path',
}

def replace_key(key:str):
    new_key = (f'z_{key}' if not key.startswith('z_') else key)
    return fix_key.get(new_key, new_key)

import re
import urllib.parse

def parse_url_from_zoon(url):
    if 'redirect' in url:
        pattern = r'to\=(http.*?)(\&|$)'
        m = re.search(pattern, url)
        #print(f'{m=}')
        if type(m) == re.Match:
            url_new = m.group(1)
            url_new_decode = urllib.parse.unquote(url_new)
            return url_new_decode
    return url

def parset_html_details_get_data_owner_id(soup):
    div_reviews_element = soup.find("div", {"data-owner-id" : True})
    if div_reviews_element is not None:
        data_owner_id_text = div_reviews_element.attrs['data-owner-id']
        return data_owner_id_text
    return ''

def parset_html_details_get_rating_value(soup):
    rating_value_element = soup.find(class_="rating-value")
    if rating_value_element is not None:
        return get_normal_text_from_element(rating_value_element)
    
    div_stars_count_element = soup.find("div", {"data-uitest" : 'stars-count'})
    if div_stars_count_element is not None:
        return get_normal_text_from_element(div_stars_count_element)
        
    return ''

def parset_html_details_get_rest_param(description_block):

    z_type_organization,z_kitchens_str,z_all_param = '','',''

    service_description_block = description_block.find(class_='service-description-block')
    if service_description_block is not None:
        dl_list_elements = service_description_block.find_all('dl')
        if dl_list_elements is not None:
            all_param_text_list = [] # на всякий случай лучше собрать все разделы, чтобы знать какие есть.
            #на случай если слово 'Кухня' изменится или будет другой похожий раздел
            z_kitchens = []
            for dl_element in dl_list_elements:
                #если это новая разметка страницы:
                dt_element = dl_element.find('dt',{'data-value':True})
                if dt_element is None:
                   #иначе это старая разметка страницы
                    dt_element = dl_element.find('dt',class_='z-text--13 z-text--dark-gray')
                if dt_element is not None:
                    dt_element_text = get_normal_text_from_element(dt_element)
                    dt_element_text = dt_element_text.lower()
                    if dt_element_text == 'тип заведения':
                        list_values = get_dd_param_values(dl_element)
                        z_type_organization = ','.join(list_values)
                    elif dt_element_text == 'кухня':                        
                        list_values = get_dd_param_values(dl_element)
                        if len(list_values) > 0:
                            z_kitchens.extend(list_values)
                    if dt_element_text in z_kitchens:
                        list_values = get_dd_param_values(dl_element)
                        if len(list_values) > 0:
                            z_kitchens = [z_kitchen for z_kitchen in z_kitchens if z_kitchen != dt_element_text]
                            z_kitchens.extend(list_values)
                    z_kitchens_str = ','.join(z_kitchens)

                    all_param_text_list.append(dt_element_text)
            z_all_param = ','.join(all_param_text_list)
        else:
            logging.warning('class params-list not found')    
    else:
        logging.warning('class service-description-block not found')

    return z_type_organization,z_kitchens_str,z_all_param


def parset_html_details_get_description_element(soup):
    element = soup.find(id = 'description')
    if element is None:
        element = soup.find(id = 'info')
    return element

def parse_html_details(full_name, is_debug_log = False):
    result_data = {
        'z_name':'',
        'z_rating_value_2':'', # с индексом 2, так как на странице поиска тоже есть рейтинг и он может отличать от страницы деталей
        #'z_description':'', #описание ресторана решили не брать
        'z_type_organization':'',
        'z_kitchens':'',
        'z_all_param':'',
        'z_phone_2':'',
        'z_address_2':'',
        'z_hours':'',
        'z_price':'',
        'z_url':'',
        'z_id':'',
        #'z_source_path':'', придет из уровня json
        'z_source_url':'',
        'z_source_url_n':''
    }
    
    if not common.isfile(full_name):
        raise(Exception(f'not found file {full_name=}'))
    logging.debug(f'parse html {full_name}')
    html_str = ''
    with open(full_name,'r',encoding='utf-8') as f:
        html_str = f.read()
    
    #print(len(html_str))
    
    soup = BeautifulSoup(html_str,"html.parser")
    #<span itemprop="name">
    name_element = soup.find("span", {"itemprop" : "name"})
    if name_element is not None:
        result_data['z_name'] = get_normal_text_from_element(name_element)

    og_url_element = soup.find("meta", {"property" : "og:url"})
    if og_url_element is not None:
        if og_url_element.attrs is not None:
            result_data['z_source_url'] = og_url_element.attrs['content']
            result_data['z_source_url_n'] = common.normalize_z_source_url(result_data['z_source_url'])
            #<meta property="og:url" content="https://ekb.zoon.ru/restaurants/restoran_krevetki_i_burgery_na_ulitse_malysheva/">

    result_data['z_id'] = parset_html_details_get_data_owner_id(soup)
    
    result_data['z_rating_value_2'] = parset_html_details_get_rating_value(soup)

    
        
    description_block = parset_html_details_get_description_element(soup)
    if description_block is None:
        logging.warning('id description element not found ' + full_name)
        return result_data


    #LEFT BLOCK
    z_type_organization,z_kitchens,z_all_param = parset_html_details_get_rest_param(description_block)

    result_data['z_type_organization'] = z_type_organization
    result_data['z_kitchens'] = z_kitchens
    result_data['z_all_param'] = z_all_param
    
    
    #RIGHT BLOCK
    
    phone_element = description_block.find(class_='tel-phone js-phone-number')
    if phone_element is not None:
        if 'href' in phone_element.attrs:
            href_phone = phone_element.attrs['href']
            result_data['z_phone_2'] = href_phone.replace('tel:','')
    
    
    adress_element = description_block.find('address',{'itemprop':'address'})
    if adress_element is not None:
        result_data['z_address_2'] = get_normal_text_from_element(adress_element)

    service_box_description_block = description_block.find(class_='service-box-description box-padding btop')
    if service_box_description_block is not None:
        dl_list_elements = service_box_description_block.find_all('dl')
        if dl_list_elements is not None:
            for dl_element in dl_list_elements:
                dt_element = dl_element.find('dt')
                if dt_element is not None:
                    dt_element_text = get_normal_text_from_element(dt_element)
                    if is_debug_log:logging.debug(f'{dt_element_text=}')
                    if dt_element_text == 'Время работы':
                        dd_element = dl_element.find('dd')
                        result_data['z_hours'] = get_normal_text_from_element(dd_element)
                    elif dt_element_text == 'Официальный сайт':
                        dd_element = dl_element.find('dd')
                        a_element = dd_element.find('a')
                        if a_element is not None and a_element.attrs:
                            result_data['z_url'] = parse_url_from_zoon(a_element.attrs['href'])
                        else:
                            result_data['z_url'] = get_normal_text_from_element(dd_element)
                    elif dt_element_text == 'Сайт':                        
                        dd_element = dl_element.find('dd')
                        a_element = dd_element.find('a')
                        if a_element is not None and a_element.attrs:
                            result_data['z_url'] = parse_url_from_zoon(a_element.attrs['href'])
                    elif dt_element_text == '':
                        dd_element = dl_element.find('dd')
                        time_price_element = dd_element.find(class_='time__price')
                        if time_price_element is not None:
                            if is_debug_log: logging.debug('exists time_price_element') 
                            price_range_element = dd_element.find('span',{'itemprop':'priceRange'})
                            if price_range_element is not None:
                                if is_debug_log: logging.debug('exists price')                          
                                result_data['z_price'] = get_normal_text_from_element(price_range_element)
        else:
            logging.warning('element dl not found in element service-box-description')
    else:
        logging.warning('class service-box-description box-padding btop not found')

    return result_data

def get_details_json(base_folder, page_name, city, replace=False,is_debug_log = False):
    
    path = common.get_folder(base_folder.rstrip('/\\') + '/zoon', city, 'pages')
    path_json = common.get_folder(base_folder.rstrip('/\\') + '/zoon', city, 'pages_json')
    full_name_json = f'{path_json}/{page_name}.json'
    full_name_html = f'{path}/{page_name}'

    logging.debug(f'{full_name_json=}')
    if not replace and common.isfile(full_name_json):
        #если json уже существует, то забираем только его
        with open(full_name_json, 'r', encoding='utf-8') as f:
            result_data = json.load(f)
            result_data = {replace_key(key):result_data[key] for key in result_data }
            result_data['z_source_path'] = full_name_json
            if 'z_source_url_n' not in result_data:
                result_data['z_source_url_n'] = common.normalize_z_source_url(result_data['z_source_url'])
    else:
        #если json нет, тогда парсим html и результат сохраняем в json
        result_data = parse_html_details(full_name_html, is_debug_log=is_debug_log)
        result_data['z_source_path'] = full_name_json
        if 'z_source_url_n' not in result_data:
            result_data['z_source_url_n'] = common.normalize_z_source_url(result_data['z_source_url'])

        with open(full_name_json,'w', encoding='utf') as f:
            json.dump(result_data,f, ensure_ascii=False)
        
    return result_data


def get_html_from_json_str(obj_result):
    if not 'success' in obj_result:
        raise(Exception('not key success!!'))
    
    if not obj_result['success']:
        raise(Exception('not success!!!'))
    
    if not 'html' in obj_result:
        raise(Exception('not key html!!'))
    len_html = len(obj_result['html'])
    if len_html == 0:
        raise(Exception('html empty!!!'))
    
    html_str = obj_result['html']
    return html_str

#not using method
def get_html_from_json_file(full_path_page):
    #full_path_page = 'data/msk/sushi-bar/pages/page_1.json'
    with open(full_path_page,'r',encoding='UTF-8') as f:
        try:
            obj_result = json.load(f)
        except Exception as ex:
            logging.error(full_path_page,exc_info=True)
            raise(ex)
        if not 'success' in obj_result:
            raise(Exception('not key success!!'))
        
        if not obj_result['success']:
            raise(Exception('not success!!!'))
        
        if not 'html' in obj_result:
            raise(Exception('not key html!!'))
        len_html = len(obj_result['html'])
        if len_html == 0:
            raise(Exception('html empty!!!'))
        
        html_str = obj_result['html']
    return html_str

def get_data_from_item_rating_value(item_element):
    rating_value_element = item_element.find(class_ = 'rating-value')
    if rating_value_element is not None:
        return rating_value_element.text
    else:
        #новая разметка
        rating_value_element = item_element.find(class_ = 'stars')
        if rating_value_element is not None:
            return get_normal_text_from_element(rating_value_element)
    return ''


def get_data_from_item(item_element):
    object_result = {
        'z_title':'',
        'z_source_url':'',
        'z_source_url_n':'',
        'z_lon':'',
        'z_lat':'',
        'z_id':'',
        'z_object_id':'',
        'z_ev_label':'',
        'z_features':'',
        'z_rating_value':'',
        'z_worktimes':'',
        'z_address':'',
        'z_phone':'',
    }
    element_title = item_element.find(class_ = 'title-link js-item-url')

    if element_title is not None:
        object_result['z_title'] = element_title.text.strip()
        object_result['z_source_url'] = element_title.attrs.get('href',None)
        object_result['z_source_url_n'] = common.normalize_z_source_url(object_result['z_source_url'])

    #li class="minicard-item js-results-item  " data-lon="37.629834" data-lat="55.782546999962" data-id="4fa56de03c72dd5c550000d0" data-object_id="4fa56de03c72dd5c550000d0.8247" data-ev_label="premium"
    object_result['z_lon'] = item_element.attrs.get('data-lon','')
    object_result['z_lat'] = item_element.attrs.get('data-lat','')
    object_result['z_id'] = item_element.attrs.get('data-id','')
    object_result['z_object_id'] = item_element.attrs.get('data-object_id','')
    object_result['z_ev_label'] = item_element.attrs.get('data-ev_label','')

    features = []
    minicard_item__features = item_element.find(class_ = 'minicard-item__features')
    if minicard_item__features is not None:
        for content in minicard_item__features.contents:
            if content.name == 'a':
                features.append(content.text)
            elif content.name == 'span':
                if len(content.attrs) == 0: # сейчас текст без класса
                    features.append(content.text)
                else:
                    # но если добавят какой-то класс, то исключим bullet, это просто точка 
                    if not 'bullet' in content.attrs['class']:
                        features.append(content.text)
    
    object_result['z_features'] =  ';'.join(features)

    object_result['z_rating_value'] = get_data_from_item_rating_value(item_element)


    minicard_item__worktime_element = item_element.find(class_ = 'minicard-item__work-time')
    worktimes = []
    if minicard_item__worktime_element is not None:
        for content in minicard_item__worktime_element.contents:
            if content.name == 'span':
                if len(content.attrs) == 0: # сейчас текст без класса
                    worktimes.append(content.text)
                else:
                    # но если добавят какой-то класс, то исключим bullet, это просто точка 
                    if not 'bullet' in content.attrs['class']:
                        worktimes.append(content.text)
    object_result['z_worktimes'] =  ';'.join(worktimes)

    minicard_item__address_element = item_element.find(class_ = 'minicard-item__address')
    if minicard_item__address_element is not None:
        address_element = minicard_item__address_element.find(class_='address')
        if address_element is not None:
            object_result['z_address'] =  address_element.text
    
    js_phone_number_element = item_element.find(class_ = 'js-phone-number')
    if js_phone_number_element is not None:
        object_result['z_phone'] = js_phone_number_element.attrs.get('href','').replace('tel:','')

    return object_result

def get_items(html_str):
    soup = BeautifulSoup(html_str,"html.parser")
    items = soup.find_all(class_='minicard-item js-results-item')
    object_results = []
    for item_element in items:
        object_result = get_data_from_item(item_element)
        #object_result['z_path_source'] = full_path_page
        object_results.append(object_result)
    return object_results
