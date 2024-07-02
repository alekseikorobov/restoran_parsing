#%%
import os
#os.chdir(r'C:\work\map_api')
import numpy as np
import unicodedata
import common.dict_city as dict_city
import re
import math
import geopy.distance
import geopy
import common.my_language_ru_pack as my_language_ru_pack 
from bs4 import BeautifulSoup, NavigableString, PageElement, Tag

# import importlib
# importlib.reload(dict_city)

def normalize_z_source_url(url:str):
    if is_nan(url): return url

    url = url.rstrip('/')

    if not url.startswith('https'):
        return url
    
    idx = url.find('/',8) # 8 = len('https://')
    if idx == -1:
        return url
    
    domain = url[8:idx]

    domain = domain.replace('www.','')

    count_dot = domain.count('.')
    if count_dot == 1:
        return url[idx:]
    if count_dot == 2:
        idx_l = domain.find('.')
        city = domain[0:idx_l]
        return '/'+city+url[idx:]
    
    raise(Exception(f'not correct normalize url {url}'))

def get_rectangle_bounds(coordinates, width=314, length=314):

    start = geopy.Point(coordinates)
    hypotenuse = math.hypot(width/1000, length/1000)

    # Edit used wrong formula to convert radians to degrees, use math builtin function
    northeast_angle = 0 - math.degrees(math.atan(width/length)) 
    southwest_angle = 180 - math.degrees(math.atan(width/length)) 

    d = geopy.distance.distance(kilometers=hypotenuse/2)
    northeast = d.destination(point=start, bearing=northeast_angle)
    southwest = d.destination(point=start, bearing=southwest_angle)
    bounds = []
    for point in [northeast, southwest]:
        coords = (point.latitude, point.longitude)
        bounds.append(coords)

    return bounds

def get_folder(base_folder, city: str, type: str, is_page: bool|None = True) -> str:
    fold = ''
    if is_page is not None:
        fold = 'pages' if is_page else 'details'
    path = f'{base_folder}/{city}/{type}/{fold}'.rstrip('/')
    if not os.path.isdir(path):
        os.makedirs(path)
    return path

def isfile(path):
    '''бывают случаи что файл создается, потому выходит ошибка и он не удаляется.
    По этому стоит проверить размер файла, если он пустой, тогда его можно удалить и считать что файла не было
    '''
    if os.path.isfile(path):
        size_file = os.path.getsize(path)
        if size_file == 0:
            os.remove(path)

    return os.path.isfile(path)

def get_header_dict_from_txt(file):
    obj = {}
    with open(file,'r') as f:
        lines = f.read().splitlines()
        for i in range(0,len(lines),2):
            obj[lines[i].rstrip(':')] = lines[i+1]

        #print(lines)
    return obj

delete_words = [
    #'ooo' # приняли решение что это стоит исключить из удаление из транзакций, потому что результат становится хуже.
    #,'restoran'
    #,'restaurant'
    #,'dostavka'
]
replace_words = 'restoran,restaurant,dostavka'

def normalize_transaction_name(tran_name:str):

    tran_name = unicodedata.normalize('NFKD',tran_name).encode('1251','ignore').decode('1251')
    tran_name = tran_name.lower()
    text_new = ' '.join([w.replace('.ru','').replace('kh','h') for w in tran_name.split(' ') if w not in delete_words])
    
    for rep in replace_words.split(','):
        text_new = text_new.replace(rep,' ')
    
    text_new  = re.sub(r'[\"#\'\*\,\-\.\/\_]'," ", text_new)

    text_new = text_new.replace('&',' & ')

    text_new  = re.sub(r'  +'," ", text_new)

    return text_new.strip()
str_nan = str(np.nan)
def is_nan(obj):
    return obj is None or str(obj) == str_nan or obj == ''

def normalize_company_name(company_name:str, is_translit=True):
    if company_name is None: return company_name
    if str(company_name) == str(np.nan): return company_name
    #company_name = company_name.replace('№','n')
    norm1 = unicodedata.normalize('NFKD',company_name).encode('1251','ignore').decode('1251')
    norm2 = norm1.lower().strip()
    norm2 = norm2.replace('&',' & ')
    norm2  = re.sub(r'  +'," ", norm2)
    if is_translit:
        norm2 = my_language_ru_pack.my_translite(norm2)
    return norm2

list_replace_type_names = [
      'Банкетный зал '
    , 'Городской ресторан '
    , 'Загородный клуб '
    , 'Кафе-столовая '
    , 'Кофе-бар '
    , 'Кафе '
    , 'Клуб-ресторан '
    , 'Кондитерский дом '
    , 'Кофейня '
    , 'Кулинария-кафе '
    , 'Кулинария '
    , 'Паб крафтового пива '
    , 'Паб '
    , 'Пекарня '
    , 'Ресторан японской и азиатской кухни '
    , 'Ресторан '
    , 'Турецкий ресторан '
    , 'Фастфуд '
]

def zoon_name_fix(str1:str)->str:
    if str1 == '': return ''
    if str1 is None: return ''
    if str(str1) == str(np.nan): return str1

    for rep in list_replace_type_names:
        str1 = str1.replace(rep,'')

    return str1

list_replace_stop_word_adress = ['бульвар'
,'корпус'
,'корп.'
,'набережная'
,'область'
,'округ'
,'переулок'
,'площадь'
,'посёлок'
,'проезд'
,'проспект'
,'район'
,'строение'
,'стр.'
,'ул.'
,'улица'
,'шоссе'
,'село']


def replace_address_by_city_line(city_line, address_text:str|None):
    if address_text == '' or address_text is None or str(address_text) == str(np.nan):
        return address_text

    address_text = address_text.lower()
    address_text = re.sub('(этаж \\d+)|(\\d+ этаж.*?,)|(цокольный этаж.*?,)','',address_text).replace('  ',' ')
    for rep in city_line.replaces:
        address_text = address_text.replace(rep.lower(),'')

    address_text = address_text.replace(',',' ').replace(';',' ').replace('  ',' ')

    for rep in list_replace_stop_word_adress:
        address_text = ' '.join([a for a in address_text.split(' ') if a not in list_replace_stop_word_adress])

    return address_text.strip()

def replace_address_by_city_code(city_code:str, address_text:str|None, city_list):
    city_line = dict_city.get_line_by_city_code(city_code, city_list)

    return replace_address_by_city_line(city_line, address_text)

def replace_address_by_city(city_name:str, address_text:str|None, city_list):

    city_line = dict_city.get_line_by_city_name(city_name, city_list)

    return replace_address_by_city_line(city_line, address_text)

# def str_similarity_ww(str1:str,str2:str,func=str_similarity,is_debug=False):
#     '''
#     метод сравнивает подстроки, по отдельным словам высчитывается схожесть
#     и по всей строке считается средняя схожесть
#     '''
#     str1,str2 = str1.lower(),str2.lower()
#     str1,str2 = str1.split(' '),str2.split(' ')
#     n1,n2 = len(str1),len(str2)
    
#     if n1 > n2: str2.extend([''] * (n1 - n2))
#     if n2 > n1: str1.extend([''] * (n2 - n1))
#     if is_debug: print(f'{str1=}')
#     if is_debug: print(f'{str2=}')

#     max_result = 0 # находим лучшее среднее соответствие
#     for i_s in range(len(str2)): #i_s - индекс для смещения
#         str3 = [*str2[i_s:],*str2[0:i_s]] #происходит перестановка
        
#         res = [1 - func(w1,w2) for w1,w2 in zip(str1,str3)]
#         m = np.mean(res)
#         if m > max_result:
#             max_result = m 
#             if is_debug: print(f'{res=}, {max_result=}')
#         else:
#             if is_debug: print(f'{res=}, {m=}')
#     return 1 - max_result

def str_similarity2(str1:str,str2:str):
    is_nan1 = is_nan(str1)
    is_nan2 = is_nan(str2)
    if is_nan1 and is_nan2: return 1
    if not is_nan1 and is_nan2: return 0
    if is_nan1 and not is_nan2: return 0
    
    str1,str2 = str1.lower().strip(), str2.lower().strip()

    words1 = set(str1.split(' '))
    words2 = set(str2.split(' '))

    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))

    similarity = intersection / union
    
    return 1.0 - similarity

# def str_similarity_new(str1:str,str2:str):
#     is_nan1 = is_nan(str1)
#     is_nan2 = is_nan(str2)
#     if is_nan1 and is_nan2: return 1
#     if not is_nan1 and is_nan2: return 0
#     if is_nan1 and not is_nan2: return 0
#     #используется Jaccard-индекс
#     #Косинусное сходство и Расстояние Левенштейна дают хуже точности для адресов
#     #     
#     #print(sim.jaccard_index)
#     #print(sim.jaccard_index(str1,str2))
#     return 1.0 - sim.jaccard_index(str1,str2)

def str_similarity(str1:str,str2:str):
    '''
    return: 
        0 - полное соответствие
        1 - полное не соответсвтие! 
    '''
    is_nan1 = is_nan(str1)
    is_nan2 = is_nan(str2)
    if is_nan1 and is_nan2: return 1
    if not is_nan1 and is_nan2: return 0
    if is_nan1 and not is_nan2: return 0
    #используется Jaccard-индекс
    #Косинусное сходство и Расстояние Левенштейна дают хуже точности для адресов

    str1,str2 = str1.lower().strip(), str2.lower().strip()
    words1 = set([c for c in str1])
    words2 = set([c for c in str2])

    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))

    similarity = intersection / union
    
    return 1.0 - similarity


def _get_min_index_from_chars(text:str, chars:list[str],start:int,right=False):
    best_index = -1
    curr_index,res_char = -1,''
    min_index = len(text)
    #print(f'{min_index=}, {start=}')

    for char in chars:
        if right:
            curr_index = text[0:start].rfind(char)
        else:
            curr_index = text.find(char, start)
            #print(f'{curr_index=}')
        if curr_index != -1 and curr_index < min_index:
            min_index = curr_index
            best_index = curr_index
            res_char = char
            #print(f'change {min_index}, {res_char=}')
    return best_index, res_char

def get_part_description_200(text:str,max_len = 200):
    '''
    описание ресторана решили не брать, поэтому функция больше не используется
    '''
    raise(Exception('not using this function!'))

    if is_nan(text): return text

    # к максимальной длине добавим количество пробелов с левой части текста
    max_len += text[0:max_len].count(' ')
    # если общая длина меньше количества символов, то возвращаем текст
    if len(text) <= max_len:
        return text
    
    #ищем первую точку слева начиная с максимального индекса
    sep_index,last_char = _get_min_index_from_chars(text,['.','!','?'],max_len)
    #print(f'res1 {sep_index=}, {last_char=}')
    #если точки справа нет
    if sep_index == -1:
        # тогда берем точку самую правую с нашей левой части
        sep_index,last_char = _get_min_index_from_chars(text,['.','!','?'],max_len,right=True)
        #print(sep_index,last_char)
    # если и там нет точки
    if sep_index == -1:
        # тогда берем до первой точки слева из всего текста
        sep_index, last_char = _get_min_index_from_chars(text,['.','!','?'],0)
        #print(sep_index,last_char)
        # если и там нет точки
        if sep_index == -1:
            # тогда просто берем весь текст
            return text
    # иначе берем левую часть до точки
    return text[0:sep_index] + last_char
#%%

def get_normalize_phones(phones_text:str):
    phones_text = phones_text.replace('‒','-').replace(' ','')
    patern_rep = r'(\+7|8)(\(|-|)(80\d{1})(\)|-|)(\d{3})(-|)(\d{2})(-|)(\d{2})'
    mat = re.match(patern_rep,phones_text)
    if mat:
        return re.sub(patern_rep,r'\1 (\3) \5-\7-\9',phones_text)
    
    patern_rep = r'(\+7|8)(\(|-|)(8\d{3})(\)|-|)(\d{2})(-|)(\d{2})(-|)(\d{2})'
    mat = re.match(patern_rep,phones_text)
    if mat:
        return re.sub(patern_rep,r'\1 (\3) \5-\7-\9',phones_text)
    
    patern_rep = r'(\+7|8)(\(|-|)([94]\d{2})(\)|-|)(\d{3})(-|)(\d{2})(-|)(\d{2})'
    mat = re.match(patern_rep,phones_text)
    if mat:
        return re.sub(patern_rep,r'\1 (\3) \5-\7-\9',phones_text)
    
    patern_rep = r'(\+7|8)(\(|-|)(\d{3})(\)|-|)(\d{3})(-|)(\d{2})(-|)(\d{2})'
    mat = re.match(patern_rep,phones_text)
    if mat:
        return re.sub(patern_rep,r'\1 (\3) \5-\7-\9',phones_text)
    
    return ''

exclude_websites = [
    'instagram.com'
]


def strip_url(url_link:str,use_exclude = True):
    if is_nan(url_link): return url_link

    if use_exclude:
        for exclude_website in exclude_websites:
            if exclude_website in url_link:
                return ''

    if '?' in url_link:
        url_link = url_link[0: url_link.find('?')]
    return url_link 


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

if __name__ == '__main__':
    print(str_similarity('123','134'))
    print(str_similarity_new('123','134'))
    # list_phone = [
    # '+7 (8314) 33-16-91'
    # ,'+7 342 203-00-63'
    # ,'+79889698282'
    # ,'+78462313000'
    # ,'+74950040561'
    # ,'+73832180939'
    # ,'8 (800) 707-50-76'
    # ,'8 (800) 200-58-06'
    # ,'+7 843 207 99 99'
    # ,'+7 8442 50 55 07'
    # ,'+7 910 000 15 09'
    # ,'+7960048421'
    # ,'+7‒928‒038‒88‒33'
    # ,'53-51-20'
    # ,'222-44-77'
    # ,'+7 8 (903) 343-73-07'
    # ]
    # for phone in list_phone:
    #     print(f'("{phone}", "{get_normalize_phones(phone)}"),')