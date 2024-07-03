#%%
import requests
import os
import time, random
import re
import json
from bs4 import BeautifulSoup, NavigableString, PageElement, Tag

base_folder = f'{os.path.abspath("")}/data/trip'
import sys
import warnings
import logging
warnings.filterwarnings("ignore")
import importlib
importlib.reload(logging)
import common.common as common

# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s [%(levelname)s] %(message)s",
# )
# # logging.debug('12')
# logging.debug('1')
# logging.debug('1')
# logging.warn('1')
# logging.error('1')
#%%
def get_random_second():
    time.sleep(random.choice([2,3, 1]))

def get_full_name_from_url(city, url):
    path = common.get_folder(base_folder,city,'details',None)
    url = url.strip('/')
    page_name = url.split('/')[-1]
    full_name = f'{path}/{page_name}'
    return full_name

def get_full_name_by_query_html(city,query,page_offset):
    filename = pretty_file_name(query.lower().replace(',','').replace(' ',''))
    path = common.get_folder(base_folder,city,'search',None)
    full_name = f'{path}/{filename}.html'
    if page_offset>0:
        full_name = f'{path}/{filename}_{page_offset}.html'
    return full_name

def get_trip_query_pretty(query:str):
    '''
    метод для сохранения информации о поиске, соответствует назнванию файла без расширения
    нужен для обратной совместимсоти с найдеными значенями из json
    используется для связки
    '''
    query_res = pretty_file_name(query.lower().replace(',','').replace(' ',''))
    return query_res

def get_trip_query(city_name:str,ya_company_name:str):
    if common.is_nan(ya_company_name): return ''
    query = f"{ya_company_name} {city_name}"
    return query

def get_full_name_by_query_json(city, query, page_offset):
    filename = pretty_file_name(query.lower().replace(',','').replace(' ',''))
    path = common.get_folder(base_folder,city,'search_json',None)
    full_name = f'{path}/{filename}.json'
    if page_offset>0:
        full_name = f'{path}/{filename}_{page_offset}.json'
    return full_name

def get_header_dict_from_txt(file):
    obj = {}
    with open(file,'r') as f:
        lines = f.read().splitlines()
        for i in range(0,len(lines),2):
            obj[lines[i].rstrip(':')] = lines[i+1]

        #print(lines)
    return obj

def get_html_by_url(full_name, url:str, type_page='details',replace=False, timeout=120, proxy = None):
    html_result = ''
    if not common.isfile(full_name) or replace:
        if type_page == 'details':
            headers = get_header_dict_from_txt('ta_parser/headers.txt')
        else:
            headers = get_header_dict_from_txt('ta_parser/headers_search.txt')
            headers['Referer'] = url
        logging.debug(f'load by {url=}')
        logging.debug(f'{headers=}')

        proxies = None
        if proxy is not None:
            proxies = {
            'http': proxy,
            'https': proxy
            }

        res = requests.get(url, headers=headers, verify=False, timeout=timeout,proxies=proxies)
        get_random_second()
        with open(full_name, 'w', encoding='utf-8') as f:
            html_result = res.text
            f.write(html_result)
    else:
        logging.debug(f'already exists {full_name=}')
        with open(full_name,'r',encoding='UTF-8') as f:
            html_result = f.read()
    logging.debug(f'html_result {len(html_result)=}')
    return html_result

def get_full_name_by_details_json(city, id):
    path = common.get_folder(base_folder, city,'details_json',None)
    result_details_json = f'{path}/{int(id)}.json'
    return result_details_json

def get_location_id_from_url(ta_link:str):
    patern = r'Review-g\d+-d(\d+)-Reviews'
    m = re.search(patern,ta_link)
    if m:
        res = m.group(1)
        return int(res)
    else:
        raise(Exception(f'cannot location id from url {ta_link=}'))

def get_html_details_and_parse(city, test_url, id,replace_json=False,timeout=120):
    
    result_details_json = get_full_name_by_details_json(city, id)
    
    if replace_json or not common.isfile(result_details_json):
        full_name = get_full_name_from_url(city, test_url)
        html_result = get_html_by_url(full_name, test_url,timeout=timeout)
        start_index = html_result.find('__WEB_CONTEXT__')
        if start_index == -1:
            logging.warn(f'not found __WEB_CONTEXT__ in {full_name=}')
        cur = start_index
        N = len(html_result)
        result_data = ''
        while cur < N and html_result[cur:cur+2] != '};':
            cur += 1

        result_data = html_result[start_index:cur+2]
        result_data = result_data.replace('__WEB_CONTEXT__=','')\
                                .replace('pageManifest','"pageManifest"')\
                                .replace('};','}')
        logging.debug(f'write to {result_details_json=}')
        with open(result_details_json,'w', encoding='utf') as f:
            obj = json.loads(result_data)
            json.dump(obj,f, ensure_ascii=False)
    else:
        logging.debug(f'already exists {result_details_json=}')

    #print(len(result_data))
    
    #print(len(obj['pageManifest']['redux']['api']['responses'][f"/data/1.0/location/{id}"]['data']))

def pretty_file_name(filename:str):
    return re.sub(r'[\\/*?:"<>|]',"_", filename)


ssrc_map = {
    'HOTEL':'h',
    'RESTAURANT':'e',
}

def get_html_by_search_page(city, query,page_offset,replace=False,type_org = 'HOTEL',timeout=120):
    q_param = requests.utils.quote(query)
    logging.debug(f'{q_param=}')
    
    if not type_org in ssrc_map:
        raise(Exception(f'not correct type_org value - {type_org}!'))
    
    ssrc = ssrc_map[type_org]
    test_url = f'https://www.tripadvisor.ru/Search?q={q_param}&ssrc={ssrc}&searchSessionId=7236A310399549A50A126094AFC0892C1696514443093ssid&sid=D0973E54C82A43E1BF5883FCF8DC9D1A1696514444209&blockRedirect=true&isSingleSearch=true&locationRejected=true&firstEntry=false&o={page_offset}'
    full_name = get_full_name_by_query_html(city, query, page_offset)
    logging.debug(f'{full_name=}')
    html_result = get_html_by_url(full_name, test_url,type_page='search',replace=replace,timeout=timeout)
    logging.debug(f'{len(html_result)=}')
    return html_result


def get_params_from_attr_widgetEvCall(text:str):
    patern = "(\/.*?html).*{type: '(.*?)'.*locationId: '(.*?)'"
    params_atr = re.search(patern,text)
    link,type_org,location_id = '','',''
    if params_atr is None:
        logging.warn(f'not found patern in {text=}')
    else:
        link,type_org,location_id = params_atr.groups()
    return link,type_org,location_id

def get_normal_text_from_element(element:PageElement):
    
    if element is None: return ''
    
    text = element.get_text(' ',strip=True)
    text = re.sub(' +',' ', text)
    res_text = []
    for letter in text:
        if letter.isprintable():
            res_text.append(letter)
        else:
            res_text.append(' ')
    text_p = ''.join(res_text)
    return re.sub(' +',' ', text_p)

def get_cuisines(cuisines):
    return ','.join([item['name'] for item in cuisines])

def merge_json(json1, json2):
    if isinstance(json1, str):
        json1 = json.loads(json1)
    if isinstance(json2, str):
        json2 = json.loads(json2)

    if isinstance(json1, dict) and isinstance(json2, dict):
        merged = json1.copy()
        for key, value in json2.items():
            if key in merged and isinstance(merged[key], (dict, list)) and isinstance(value, (dict, list)):
                merged[key] = merge_json(merged[key], value)
            else:
                merged[key] = value
        return merged

    if isinstance(json1, list) and isinstance(json2, list):
        merged = json1 + json2
        return merged

    return json2

def parse_page_details_from_json(full_name:str, location_id:int):

    row = {}
    row['ta_source_d_json'] = full_name
    with open(full_name,'r',encoding='utf-8') as f:
        obj_list = json.load(f)
    #location_id = int(row['ta_location_id'])
    data = obj_list['pageManifest']['redux']['api']['responses'][f"/data/1.0/location/{location_id}"]['data']
    data_rest = None
    if f'/data/1.0/restaurant/{location_id}/overview' in obj_list['pageManifest']['redux']['api']['responses']:
        data_rest = obj_list['pageManifest']['redux']['api']['responses'][f'/data/1.0/restaurant/{location_id}/overview']['data']

    
    row['ta_location_id'] = location_id
    row['ta_address_2'] = data.get('address',None)
    #row['ta_description'] = data.get('description',None) #больше не требуется
    if 'category' in data:
        row['ta_category'] = f"{data['category']['key']}_{data['category']['name']}"
    if 'cuisine' in data:
        row['ta_cuisine'] = get_cuisines(data['cuisine'])
    else:
        row['ta_cuisine'] = None
    
    if 'display_hours' in data:
        display_hours_join = data['display_hours']
        row['ta_display_hours_json'] =json.dumps(display_hours_join,ensure_ascii=False)
    if 'hours' in data:
        hours_join = data['hours']
        row['ta_hours_json'] =json.dumps(hours_join,ensure_ascii=False)
    row['ta_is_closed'] =data.get('is_closed',None)
    row['ta_is_long_closed'] =data.get('is_long_closed',None)
    row['ta_latitude'] =data.get('latitude',None)
    row['ta_longitude'] =data.get('longitude',None)
    row['ta_name'] =data.get('name',None)
    row['ta_num_reviews'] =data.get('num_reviews',None)
    row['ta_phone'] =data.get('phone',None)
    row['ta_price_level'] =data.get('price_level',None)
    row['ta_price'] =data.get('price',None)
    if data_rest is not None and 'detailCard' in data_rest:
        row['ta_numericalPrice'] =data_rest['detailCard'].get('numericalPrice',None)
    row['ta_ranking_category'] =data.get('ranking_category',None)
    row['ta_ranking_denominator'] =data.get('ranking_denominator',None)
    row['ta_ranking_position'] =data.get('ranking_position',None)
    row['ta_rating'] =data.get('rating',None)
    row['ta_raw_ranking'] =data.get('raw_ranking',None)
    row['ta_website'] = data.get('website',None)
    return row

def get_list_str(list_obj):
  return ','.join([obj["amenityNameLocalized"].replace('\xa0',' ') for obj in list_obj if obj is not None and "amenityNameLocalized" in obj and obj["amenityNameLocalized"] is not None ])

def parse_page_details_from_json_hotel(full_name:str, location_id:int):
    obj_list = None
    with open(full_name,'r',encoding='utf-8') as f:
        obj_list = json.load(f)
        
    #row_new = load_data.parse_page_details_from_json(full_name, int(location_id))

    json_result = {}
    for key,val in obj_list['pageManifest']['urqlCache']['results'].items():
        d_str = val['data']
        json_result = merge_json(json_result, d_str)

    obj_res = None
    for obj in json_result['locations']:
        if obj is not None and 'accommodationType' in obj:
            obj_res = obj

    row = {}
    row['ta_source_d_json'] = full_name
    row['ta_location_id'] = location_id
    
    row['ta_languagesSpoken'] = get_list_str(obj_res['detail']['hotelAmenities']['languagesSpoken'])
    row['ta_roomFeatures'] = '' 
    row['ta_roomTypes'] = ''
    row['ta_propertyAmenities'] = '' 
    if obj_res['detail']['hotelAmenities']['highlightedAmenities'] is not None:
        row['ta_roomFeatures'] = get_list_str(obj_res['detail']['hotelAmenities']['highlightedAmenities']['roomFeatures'])
        row['ta_roomTypes'] = get_list_str(obj_res['detail']['hotelAmenities']['highlightedAmenities']['roomTypes'])
        row['ta_propertyAmenities'] = get_list_str(obj_res['detail']['hotelAmenities']['highlightedAmenities']['propertyAmenities'])

    if obj_res['detail']['hotelAmenities']['nonHighlightedAmenities'] is not None:
        roomFeatures_other = get_list_str(obj_res['detail']['hotelAmenities']['nonHighlightedAmenities']['roomFeatures'])
        roomTypes_other = get_list_str(obj_res['detail']['hotelAmenities']['nonHighlightedAmenities']['roomTypes'])
        propertyAmenities_other = get_list_str(obj_res['detail']['hotelAmenities']['nonHighlightedAmenities']['propertyAmenities'])

        if len(roomFeatures_other)>0: row['ta_roomFeatures'] += ','+roomFeatures_other
        if len(roomTypes_other)>0: row['ta_roomTypes'] += ','+roomTypes_other
        if len(propertyAmenities_other)>0: row['ta_propertyAmenities'] += ','+propertyAmenities_other

    row['ta_propertyAmenities'] = ','.join(set(row['ta_propertyAmenities'].split(',')))

    row['ta_starRating'] = None
    if any(obj_res['detail']['starRating']):
        row['ta_starRating'] = obj_res['detail']['starRating'][0]['tagNameLocalized']

    row['ta_review_count'] = None
    row['ta_review_rating'] = None
    if 'locationInfo' in json_result and any(json_result['locationInfo']):
        reviewSummary = json_result['locationInfo'][0]['reviewSummary']
        if reviewSummary is not None:
            row['ta_review_count'] = reviewSummary['count']
            row['ta_review_rating'] = reviewSummary['rating']
        else:
            logging.warn(f'{json_result["locationInfo"]=}')

    row['ta_TypePopIndex'] = None
    row['ta_OverallPopIndex'] = None
    row['ta_CategoryPopIndex'] = None
    if 'popIndexInfo' in json_result and any(json_result['popIndexInfo']):
        # "accommodationType": "T_HOTEL",
        # "localizedTypePopIndexString": "№ 5 из 111 отелей в Адлере",
        # "localizedOverallPopIndexString": "№ 6 из 769 — отели — Адлер",
        # "localizedCategoryPopIndexString": "№ 5 из 113 — отели — Адлер"
        row['ta_TypePopIndex'] = json_result['popIndexInfo'][0]['localizedTypePopIndexString']
        row['ta_OverallPopIndex'] = json_result['popIndexInfo'][0]['localizedOverallPopIndexString']
        row['ta_CategoryPopIndex'] = json_result['popIndexInfo'][0]['localizedCategoryPopIndexString']
    
    row['ta_latitude'] = None
    row['ta_longitude'] = None
    row['ta_address_2'] = None

    #row['ta_linksForWebsite'] = json_result['currentLocation'][0]['linksForWebsite']
    if 'currentLocation' in json_result:
        row['ta_latitude'] = json_result['currentLocation'][0]['latitude']
        row['ta_longitude'] = json_result['currentLocation'][0]['longitude']
        row['ta_address_2'] = json_result['currentLocation'][0]['streetAddress']['fullAddress']

    return row

def parse_page_search(html_result:str, page_offset:int):
    result_orgs = []
    page_offsets = []
    if 'ничего не удалось найти' in html_result:
        logging.warn(f'list result search is empty with phrase "ничего не удалось найти" {page_offset=}')
        return result_orgs,page_offsets
    soup = BeautifulSoup(html_result,"html.parser")
    address_list_elements = soup.find_all(class_='result inner-columns-wrapper')
    logging.debug(len(address_list_elements))
    if len(address_list_elements) == 0:
        raise(Exception('not found element from search page'))
    for address_element_item in address_list_elements:
        result_org = {
            'name':'',
            'link':'',
            'type_org':'',
            'location_id':'',
            'address':'',
        }
        result_title_element = address_element_item.find(class_='result-title')
        if result_title_element is None:
            logging.debug(f'{address_element_item=}')
        else:
            result_org['name'] = get_normal_text_from_element(result_title_element)

        address_element = address_element_item.find(class_="address")
        onclick_text = address_element.attrs['onclick']
        if onclick_text is None:
            raise(Exception('not found atribute onclick in class address'))

        link,type_org,location_id = get_params_from_attr_widgetEvCall(onclick_text)
        result_org['link'] = link
        result_org['type_org'] = type_org
        result_org['location_id'] = location_id
        address_text_element = address_element.find(class_='address-text')
        result_org['address']  = get_normal_text_from_element(address_text_element)
        result_orgs.append(result_org)

    
    if page_offset == 0:
        pageNumbers_element = soup.find(class_='pageNumbers')
        if type(pageNumbers_element) == Tag and pageNumbers_element is not None:
            for child in pageNumbers_element.contents:
                if type(child) == Tag:
                    if child.name == 'span':
                        break
                    elif child.name == 'a':
                        if 'data-offset' in child.attrs:
                            offset = child.attrs['data-offset']
                            if int(offset) == 0: continue #первую страницу пропускаем, так как мы уже на ней
                            page_offsets.append(int(offset))
    return result_orgs, page_offsets[0:6] # не более 6ти страниц

def save_json_by_search_page(city:str, query:str,page_offset:int = 0,replace_json=False,timeout=120):
    logging.debug(f'start - {city=}, {query=}')
    full_name = get_full_name_by_query_json(city, query, page_offset)
    logging.debug(f'start {full_name=}')
    if replace_json or not common.isfile(full_name):
        html_result = get_html_by_search_page(city ,query, page_offset,type_org='RESTAURANT',timeout=timeout)
        result_orgs, page_offsets = parse_page_search(html_result, page_offset)
        logging.debug(f'get pages - {page_offsets=}')
        with open(full_name,'w', encoding='utf') as f:
            json.dump(result_orgs,f, ensure_ascii=False)
        for _page_offset in page_offsets:
            save_json_by_search_page(city,query,_page_offset,replace_json,timeout=timeout)
    else:
        logging.debug(f'already exists {full_name=}')

