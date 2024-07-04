

import unittest
import common.common as common
from common import my_language_ru_pack
import zoon_parser.parse_data as parse_data
import zoon_parser.select_best_zoon_search as select_best_zoon_search
import ta_parser.load_data as ta_load_data
import pandas as pd
import ya_parser.load_ya_raiting as load_ya_raiting
from params import Params
from bs4 import BeautifulSoup, NavigableString, PageElement, Tag
import json

class MyTest(unittest.TestCase):

    def test_replace_address_by_city(self):
        
        #from, to
        test_list = [
            ('Лубянский проезд, 15с2, этаж 1, Москва','лубянский 15с2'),
           ('Лубянский проезд, 15с2, этаж 2, Москва','лубянский 15с2'),
           ('парк Малевича, 1, 1 этаж, Москва','парк малевича 1'),
            ('парк Малевича, 1, 1 этаж; центр Аура, Москва','парк малевича 1'),
            ('Авиаторов, 19, цокольный этаж; гостиница Сибирь, Москва','авиаторов 19'),
            ('Пискунова, 8, цокольный этаж, Москва','пискунова 8'),
        ]
        param = Params()
        with open('params.json','r',encoding='UTF-8') as f:
            param = json.load(f, object_hook=lambda d: Params(**d))
            print(type(param))

        for test_case in test_list:
            self.assertEqual(common.replace_address_by_city('Москва',test_case[0],param.city_list,param.list_replace_stop_word_adress),test_case[1])
    

    def test_get_id_from_ya_image_url(self):
        url = 'https://avatars.mds.yandex.net/get-altay/4737312/2a0000017abf099a6142bcc666c109dccd85/XXXL'
        result_id = '4737312_2a0000017abf099a6142bcc666c109dccd85'
    
        fact_id = common.get_id_from_ya_image_url(url)
        self.assertEqual(result_id,fact_id)

    def test_normalize_transaction_name(self):
        
        #from, to
        test_list = [
            ('ooo 123 restoran','ooo 123'),
            ('  123 ooo restaurant','123 ooo'),
            ('123 ooo 456 dostavka','123 ooo 456'),
            ('123 ooo 456.ru dostavka','123 ooo 456'),
            ('TEST OOO  ','test ooo'),
            ('krasota.wrf.su','krasota wrf su'),
            ('kras"#\'*,-./_ota.wrf.su','kras ota wrf su'),
            ('restoran',''),
            ('restoransyrovarnya','syrovarnya'),
            ('dostavkasyrovarnya','syrovarnya'),
            ('khat','hat'),
            ('khat 1121kh','hat 1121h'),
            ('Salone pasta&bar','salone pasta & bar'),
            ('Beerman&Grill','beerman & grill'),
            ('Креветки и бургеры','креветки и бургеры'),
            ('Чайхона № 1','чаихона no 1'),
        ]
        for test_case in test_list:
            self.assertEqual(common.normalize_transaction_name(test_case[0]),test_case[1])
    
    def test_normalize_company_name(self):
        
        #from, to
        test_list = [
            ('Beerman&Grill','beerman & grill',True),
            ('Be&erman&Grill','be & erman & grill',True),
            ('Be & erman & Grill','be & erman & grill',True),
            ('Креветки и бургеры','креветки и бургеры', False),
            
            #('Чайхона №1','chaihona n1'),
        ]
        for test_case in test_list:
            self.assertEqual(common.normalize_company_name(test_case[0],test_case[2]),test_case[1])



    def test_get_best_from_result_zoon_1(self):
        new_row = {
            's_point':'55.01,37.01','s_location_nm_rus':'Москва',
            's_address':'adr1',
            's_company_name_norm':'chaihana granat',
            'transaction_info_new':'chayhana granat',
            'is_map':False
        }
        json_result_list = [{
            'id':'1',
            'lat':'37.01','lon':'55.01001',
            'address':'adr1',
            'title':'granat',
            'z_status':'new',
            'z_dist':0,
            'z_similarity_title_with_tran2':0,
            'z_similarity_title_with_tran':0,
            'z_similarity_title2':0,
            'z_similarity_title':0,
            'z_similarity_address':0,
        },{
            'id':'2',
            'lat':'37.01','lon':'55.01001',
            'address':'adr1',
            'title':'chynar',
            'z_status':'new',
            'z_dist':0,
            'z_similarity_title_with_tran2':1,
            'z_similarity_title_with_tran':1,
            'z_similarity_title2':0,
            'z_similarity_title':0,
            'z_similarity_address':0,
        }]
        sbz = select_best_zoon_search.SelectBestZoonSearch({})
        res = sbz.get_best_from_result(pd.DataFrame(json_result_list))
        if res is not None:
            self.assertEquals(1,len(res[res['id'] == '1']))


    def test_translite(self):
        self.assertEqual(my_language_ru_pack.my_translite('вишня'),'vishnya') 
        self.assertEqual(my_language_ru_pack.my_translite('дизайн'),'dizajn') #????? может dizayn
        self.assertEqual(my_language_ru_pack.my_translite('гриль бутыль'),'gril butyl')
        self.assertEqual(my_language_ru_pack.my_translite('эврен'),'evren')
        self.assertEqual(my_language_ru_pack.my_translite(
             'абвгдезийклмнопрстуфх ц  Ц ъыьАБВГДЕЗИЙКЛМНОПРСТУФХЪЫЬ'.replace(' ',''))
            ,'abvgdezijklmnoprstufh ts Ts_y_ABVGDEZIJKLMNOPRSTUFH_Y_'.replace(' ','').replace('_',''))
        

    @unittest.skip("функция parse_data.replace_description перестала использоваться")    
    def test_replace_description_zoon(self):
        test_list = [
            ('Ресторан Сосновый Дворик (рейтинг на Zoon) приглашает вас окунуться в атмосферу любимых вкусов.','Ресторан Сосновый Дворик приглашает вас окунуться в атмосферу любимых вкусов.'),
            ('Р (рейтинг на Zoon.ru) п.','Р п.'),
            ('Р (Рейтинг на Zoon.ru) п.','Р п.'),
            ('Р (Рейтинг на zoon.ru) п.','Р п.'),
            ('Bahroma (рейтинг на Zoon - 4.1) приглаша','Bahroma приглаша'),
            ('Bahroma (рейтинг на Zoon - 4) приглаша','Bahroma приглаша'),
            ('Bahroma (рейтинг на Zoon — 4) приглаша','Bahroma приглаша'),
            ('Bahroma (рейтинг на Zoon — 4.2) приглаша','Bahroma приглаша'),
            ('МИЛТИ (рейтинг компании на Zoon — 4) дел','МИЛТИ дел'),
            ('Крестьянская улица, 9Б. Рейтинг пироговой на Zoon - 3. График','Крестьянская улица, 9Б. График'),
            ('Студия капоэйры (рейтинг на сайте Zoon.ru - 4.1) предлагает','Студия капоэйры предлагает'),
            ('дресс-коду. Узнать более подробную информацию о развлекательной программе и наличии доступных для бронирования столов вы можете на сайте Zoon.ru. Всех','дресс-коду. Всех'),
            ('Восход, 28. Дополнительную информацию вы можете узнать по телефону или на сайте: Zoon.ru.','Восход, 28.'),
            ('Восход, 28. Дополнительную информацию вы можете узнать по телефону или на сайте: Zoon.ru. rfr','Восход, 28. rfr'),
            ('страсти. Узнать более детальную информацию о предлагаемой программе и наличии свободных столиков вы можете на сайте Zoon.ru. Всех','страсти. Всех'),
            ('Буфет предлагает вам окунуться в атмосферу вкусной еды и прохладных напитков. Заведения общепита не случайно являются неотъемлемой частью современного мира. Не хотите тратить на приготовление еды драгоценное время? Нет ничего проще: найдите ресторан или кафе по душе и выберите блюдо из меню! Рейтинг буфета на Zoon - 2, однако вы можете поделиться вашим личным мнением о заведении, написав отзыв о нём, и повлиять на эту оценку. Здоровая конкуренция и неравнодушные посетители — вот две вещи, приводящие к тому, что уровень еды, которую предлагают для нас повара за деньги, продолжает расти. Всех гостей ждут по адресу: Ворошилова, 16. Для гостей заведение работает Пн-пт: 09:00 - 18:00. '
             ,'Буфет предлагает вам окунуться в атмосферу вкусной еды и прохладных напитков. Заведения общепита не случайно являются неотъемлемой частью современного мира. Не хотите тратить на приготовление еды драгоценное время? Нет ничего проще: найдите ресторан или кафе по душе и выберите блюдо из меню! Всех гостей ждут по адресу: Ворошилова, 16. Для гостей заведение работает Пн-пт: 09:00 - 18:00.'
            ),

            ('необходимость. Оценка пользователей на сайте Zoon.ru — 5. Вы','необходимость. Вы'),
            ('необходимость. Оценка пользователей на сайте Zoon.ru — 4.5. Вы','необходимость. Вы'),
            ('Магазина детской одежды Domilina (оценка посетителей на сайте Zoon.ru — 3). Девочек','Магазина детской одежды Domilina. Девочек'),
            ('знания в этой сфере. Оценка компании от посетителей Zoon.ru - 2.3. Обратиться','знания в этой сфере. Обратиться'),
            ('ветеринара к себе на дом. На портале Zoon собрана проверенная информация о работе докторов клиники, и вы легко можете ознакомиться с ней, перейдя по ссылкам. Вязовых'
             ,'ветеринара к себе на дом. Вязовых'),
             ('состояния. На сайте Zoon.ru собрана достоверная информация о докторах клиники, и вы можете ознакомиться с ней по ссылкам. Кейних'
              ,'состояния. Кейних'),
              ('Рады приветствовать вас на Zoon! Сеть Сервисных центров','Сеть Сервисных центров'),
              ('занятий. Ученики, которые закончили обучение в Репетиторском центре Family Class, остались довольны организацией уроков, и поставили оценку на портале Zoon.ru 4.3 балла. Вы тоже',
               'занятий. Вы тоже'),
              ('занятий. Ученики, которые закончили обучение в Репетиторском центре Family Class, остались довольны организацией уроков, и поставили оценку на портале Zoon.ru 5 баллов. Вы тоже',
               'занятий. Вы тоже'),
               ('доставку! Гости сайта Zoon.ru высоко оценили сервис и качество покупок: рейтинг компании — 5 баллов! Вы','доставку! Вы'),
               ('удовольствия. Посетители Lounge Бар поделились своими впечатлениями о проведенном досуге с Zoon.ru, и благодаря их оценкам рейтинг компании - 4.9 балла! Вы тоже','удовольствия. Вы тоже'),
               ('домой. Если вам трудно определиться с выбором клиники для вашего питомца, то на портале Zoon можно ознакомиться с достоверной оценкой, которую поставили клиенты организации. Так, рейтинг клиники — 4.8, и это означает, что вы можете доверять её специалистам. Компания'
                ,'домой. Компания'),
               ('',''),
        ]
        for test_c in test_list:
            self.assertEqual(parse_data.replace_description(text=test_c[0]),test_c[1])

    @unittest.skip("функция common.get_part_description_200 перестала использоваться")  
    def test_get_part_description_200(self):
        test_cases = [
                ('1234',200,'1234'),
                ('1234. 56789',6,'1234.'),
                ('1234. 56789. 1123456. 789.',5,'1234. 56789.'),
                ('1234. 56789. 1123456? 789.',11,'1234. 56789. 1123456?'),
        ]
        for search_text, max_len, result in test_cases:
            self.assertEqual(common.get_part_description_200(search_text, max_len),result,f'{search_text} - {max_len}')

    def test_get_location_id_from_url(self):
        test_cases = [
                ("/Restaurant_Review-g298484-d14780307-Reviews-Restaurant_Yacht_Lastochka-Moscow_Central_Russia.html", 14780307),
        ]
        for url, result in test_cases:
            self.assertEqual(ta_load_data.get_location_id_from_url(url),result,f'{url}')

    def test_strip_url(self):
        test_cases = [
                ("https://ulrtr/?32432", "https://ulrtr/"),
                ("https://polyana-kafe.obiz.ru/?token=20230920095826SWst", "https://polyana-kafe.obiz.ru/"),
                ("https://tanukifamily.ru/tanuki/?utm_campaign=ip_tanuki_geoservice_d-m_all-aud_all-types&utm_medium=cpp&utm_source=yandexmap", "https://tanukifamily.ru/tanuki/"),
                ("instagram.com", ""),
                ("https://instagram.com/12121", ""),
                ("https://instagram.com/?werewew", ""),
        ]
        for url, result in test_cases:
            self.assertEqual(common.strip_url(url),result,f'{url}')

    
    def test_normalize_phone(self):
        test_cases = [
                ("+7 (8314) 33-16-91", "+7 (8314) 33-16-91"),
                ("+7 342 203-00-63", "+7 (342) 203-00-63"),
                ("+79889698282", "+7 (988) 969-82-82"),
                ("+78462313000", "+7 (8462) 31-30-00"),
                ("+74950040561", "+7 (495) 004-05-61"),
                ("+73832180939", "+7 (383) 218-09-39"),
                ("8 (800) 707-50-76", "8 (800) 707-50-76"),
                ("8 (800) 200-58-06", "8 (800) 200-58-06"),
                ("+7 843 207 99 99", "+7 (8432) 07-99-99"),
                ("+7 8442 50 55 07", "+7 (8442) 50-55-07"),
                ("+7 910 000 15 09", "+7 (910) 000-15-09"),
                ("+7960048421", ""),
                ("+7‒928‒038‒88‒33", "+7 (928) 038-88-33"),
                ("53-51-20", ""),
                ("222-44-77", ""),
                ("+7 8 (903) 343-73-07", ""),
        ]
        for phone_text, result in test_cases:
            self.assertEqual(common.get_normalize_phones(phone_text),result,f'{phone_text}')


    def test_parse_url_from_zoon(self):
        urls = [
            ('https://kazan.zoon.ru/redirect/?to=http%3A%2F%2Ftaplink.cc%2Fcheerem_tatar&hash=b6ac1d0e0b989965ea792ac062a875a0&from=5a0f750ca24fd967b92f76d4.b977&ext_site=ext_site&backurl=https%3A%2F%2Fkazan.zoon.ru%2Frestaurants%2Ftatarskij_restoran_chirem%2F'
            ,'http://taplink.cc/cheerem_tatar')
            
            ,('http://ufa.zoon.ru/redirect/?to=http%3A%2F%2Frchc.ru&hash=2774fc0c0f0d37779f0e6e25694fe380&from=60dda9b9b1d1b27d50175745.a2c8&ext_site=ext_site&backurl=https%3A%2F%2Fufa.zoon.ru%2Frestaurants%2Frestoran_chestnyh_tsen_na_prospekte_oktyabrya%2F'
            ,'http://rchc.ru')
            
            ,('http://ufa.zoon.ru/redirect/?to=http%3A%2F%2Frchc.ru'
            ,'http://rchc.ru')
            
            ,('http://ufa.zoon.ru/','http://ufa.zoon.ru/')
        ]

        for url,result in urls:
            self.assertEqual(parse_data.parse_url_from_zoon(url), result)

    
    def test_normalize_z_source_url(self):
        urls = [
            ('https://zoon.ru/msk/restaurants/kul','/msk/restaurants/kul'),
            ('https://www.zoon.ru/msk/restaurants/kul','/msk/restaurants/kul'),
            ('https://msk.zoon.ru/restaurants/kul','/msk/restaurants/kul'),
            ('/msk/restaurants/kul','/msk/restaurants/kul'),
            ('https://chelyabinsk.zoon.ru/shops/1001_vkus/','/chelyabinsk/shops/1001_vkus'),
        ]

        for url,result in urls:
            self.assertEqual(common.normalize_z_source_url(url), result)

    def test_zoon_parse_data_owner_id_from_html(self):
        
        full_name = r'data_unit_test\zoon\ekb\pages\pages\kafe_na_pervomajskoj'
        html_str = ''
        with open(full_name,'r',encoding='utf-8') as f:
            html_str = f.read()
        soup = BeautifulSoup(html_str,"html.parser")

        result_id = parse_data.parset_html_details_get_data_owner_id(soup)
        assert result_id == '54f54665a46cba6f2b8b4572'
    
    
    def test_parset_html_details_get_rating_value(self):
        params = [
            ('5,0',r'data_unit_test\zoon\volgograd\pages\pages\kafe_epitsentr_vkusa_-_lavashok_na_angarskoj_ulitse_old'),
            ('5,0',r'data_unit_test\zoon\volgograd\pages\pages\kafe_epitsentr_vkusa_-_lavashok_na_angarskoj_ulitse_new'),
        ]
        for expect_value, full_name in params:
            html_str = ''
            with open(full_name,'r',encoding='utf-8') as f:
                html_str = f.read()
            soup = BeautifulSoup(html_str,"html.parser")

            rating_value = parse_data.parset_html_details_get_rating_value(soup)
            assert rating_value == expect_value,f'{rating_value=} != {expect_value=} by {full_name=}'
    
    
    def test_parset_html_details_get_rest_param(self):
        params = [
            (r'data_unit_test\zoon\volgograd\pages\pages\kafe_epitsentr_vkusa_-_lavashok_na_angarskoj_ulitse_old',
            'кафе,кофейня,пекарня,шашлычная,банкетный зал,гриль-бар,стейк-хаус,фастфуд',
            'домашняя кухня,восточная кухня,авторская кухня,грузинская кухня',
            'кухня,рестораны,тип,тип заведения,кавказская кухня,фастфуд,доставка еды,безалкогольный бар,дополнительные опции меню,доставка кавказской еды,доставка фастфуда,особенности заведения,ресторан'            
            ),
            (r'data_unit_test\zoon\volgograd\pages\pages\kafe_epitsentr_vkusa_-_lavashok_na_angarskoj_ulitse_new',
            'кафе,кофейня,пекарня,шашлычная,банкетный зал,гриль-бар,стейк-хаус,фастфуд',
            'домашняя кухня,восточная кухня,авторская кухня,грузинская кухня',
            'кухня,рестораны,тип,тип заведения,кавказская кухня,фастфуд,доставка еды,безалкогольный бар,дополнительные опции меню,доставка кавказской еды,доставка фастфуда,особенности заведения,ресторан'            
            ),
        ]
        for full_name,z_type_organization_expect,z_kitchens_expect,z_all_param_expect  in params:
            html_str = ''
            with open(full_name,'r',encoding='utf-8') as f:
                html_str = f.read()
            soup = BeautifulSoup(html_str,"html.parser")

            description_block = parse_data.parset_html_details_get_description_element(soup)

            z_type_organization,z_kitchens,z_all_param  = parse_data.parset_html_details_get_rest_param(description_block)
            assert z_type_organization == z_type_organization_expect,f'{z_type_organization=} != {z_type_organization_expect=} by {full_name=}'
            assert z_kitchens == z_kitchens_expect,f'{z_kitchens=} != {z_kitchens_expect=} by {full_name=}'
            assert z_all_param == z_all_param_expect,f'{z_all_param=} != {z_all_param_expect=} by {full_name=}'

    def test_zoon_parse_description_element(self):
        
        params = [
            r'data_unit_test\zoon\volgograd\pages\pages\kafe_epitsentr_vkusa_-_lavashok_na_angarskoj_ulitse_old',
            r'data_unit_test\zoon\volgograd\pages\pages\kafe_epitsentr_vkusa_-_lavashok_na_angarskoj_ulitse_new',
        ]
        for full_name in params:
            html_str = ''
            with open(full_name,'r',encoding='utf-8') as f:
                html_str = f.read()
            soup = BeautifulSoup(html_str,"html.parser")

            description_element = parse_data.parset_html_details_get_description_element(soup)
            assert description_element is not None,f'not found description by {full_name=}'
        

    def test_get_data_from_item_rating_value(self):
        params = [
            ('4,9',r'data_unit_test\zoon\msk\search_p\18_55.666788_37.551627_new.json'),
            ('3,8',r'data_unit_test\zoon\msk\search_p\18_55.666788_37.551627_old.json'),
        ]
        for expect_value,full_name in params:
            html_str = parse_data.get_html_from_json_file(full_name)
            soup = BeautifulSoup(html_str,"html.parser")
            items = soup.find_all(class_='minicard-item js-results-item')
            object_results = []
            for item_element in items:
                rating_value = parse_data.get_data_from_item_rating_value(item_element)
                print(f'{rating_value=}')
                assert expect_value == rating_value, f'{expect_value=} != {rating_value=} by {full_name=}'
                break

    def test_ya_raiting_parse_html_get_json(self):

        with open(r"data_unit_test\yandex_r\ekb\html\1305638501.html",'r',encoding='UTF-8') as f:
            json_res = load_ya_raiting.parse_html_get_json(f.read())

            self.assertIsNotNone(json_res)
            self.assertEqual(len(json_res),4)
            self.assertTrue('ya_org_name' in json_res)
            self.assertTrue('ya_stars_count' in json_res)
            self.assertTrue('ya_rating' in json_res)
            self.assertTrue('ya_link_org' in json_res)
            self.assertFalse(json_res['ya_org_name'] == '')
            self.assertFalse(json_res['ya_stars_count'] == '')
            self.assertFalse(json_res['ya_rating'] == '')
            self.assertFalse(json_res['ya_link_org'] == '')

# if __name__ == '__main__':
#     unittest.main()