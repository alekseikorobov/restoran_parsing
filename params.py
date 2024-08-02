from dataclasses import dataclass, field
from string import Template
import datetime
import json

@dataclass
class Params:
    # def __init__(self, **entries):
    #     self.__dict__.update(entries)

    base_path:str = '.'
    '''Базовый путь к файлам, используется как раметр $base_path
    '''

    @property
    def yandex_data_file(self):
        '''Возвращает _yandex_data_file с подстановкой параметра base_path'''
        return Template(self._yandex_data_file).substitute({'base_path':self.base_path.rstrip('/\\')})
    @property
    def temp_zoon_search_file(self):
        '''Возвращает _temp_zoon_search_file с подстановкой параметра base_path'''
        return Template(self._temp_zoon_search_file).substitute({'base_path':self.base_path.rstrip('/\\')})
    @property
    def temp_select_best_zoon_search_file(self):
        '''Возвращает _temp_select_best_zoon_search_file с подстановкой параметра base_path'''
        return Template(self._temp_select_best_zoon_search_file).substitute({'base_path':self.base_path.rstrip('/\\')})
    @property
    def zoon_details_file(self):
        '''Возвращает _zoon_details_file с подстановкой параметра base_path'''
        return Template(self._zoon_details_file).substitute({'base_path':self.base_path.rstrip('/\\')})
    @property
    def temp_trip_search_file(self):
        '''Возвращает _temp_trip_search_file с подстановкой параметра base_path'''
        return Template(self._temp_trip_search_file).substitute({'base_path':self.base_path.rstrip('/\\')})
    @property
    def temp_select_best_trip_search_file(self):
        '''Возвращает _temp_select_best_trip_search_file с подстановкой параметра base_path'''
        return Template(self._temp_select_best_trip_search_file).substitute({'base_path':self.base_path.rstrip('/\\')})
    @property
    def trip_details_file(self):
        '''Возвращает _trip_details_file с подстановкой параметра base_path'''
        return Template(self._trip_details_file).substitute({'base_path':self.base_path.rstrip('/\\')})
    @property
    def cache_data_folder(self):
        '''Возвращает _cache_data_folder с подстановкой параметра base_path'''
        return Template(self._cache_data_folder).substitute({'base_path':self.base_path.rstrip('/\\')})
    @property
    def ya_image_params_file(self):
        '''Возвращает _ya_image_params_file с подстановкой параметра base_path'''
        return Template(self._ya_image_params_file).substitute({'base_path':self.base_path.rstrip('/\\')})
    @property
    def ya_images_folder(self):
        '''Возвращает _ya_images_folder с подстановкой параметра base_path'''
        return Template(self._ya_images_folder).substitute({'base_path':self.base_path.rstrip('/\\')})

    @property
    def logs_path(self):
        '''Возвращает _logs_path с подстановкой параметра base_path и date_now в заданом формате параметра date_time_format'''
        return Template(self._logs_path).substitute({
            'base_path':self.base_path.rstrip('/\\'),
            'date_now':datetime.datetime.strftime(datetime.datetime.now(), self.date_time_format)
        })
    
    date_time_format:str = '%Y%m%d_%H%M%S'
    '''Параметр для форматирования даты логирования, по умолчанию %Y%m%d_%H%M%S'''

    _yandex_data_file: str = '$base_path/tables/dm_rest_yandex_data.parquet'
    '''таблица входного фала для поиска'''

    _temp_zoon_search_file: str = '$base_path/tables/zoon_search.pik'
    '''временный файл результата парсинга со страницы поиска из zoon.ru'''

    _temp_select_best_zoon_search_file: str = '$base_path/tables/zoon_select_best.pik'
    '''временный файл результата выбора лучшего соответствия между данными из яндекса и zoon.ru со страницы поиска'''

    #выходной файл по zoon
    _zoon_details_file: str = '$base_path/tables/zoon_details.parquet'
    '''выходной файл результата парсинга из zoon.ru'''
    _temp_trip_search_file: str = '$base_path/tables/trip_search.pik'
    _temp_select_best_trip_search_file: str = '$base_path/tables/trip_select_best.pik'
    _trip_details_file: str = '$base_path/tables/trip_details.parquet'
    _ya_image_params_file: str = '$base_path/tables/ya_image_params.pik'
    '''параметры (+ прямые ссылки) по картинкам из яндекса'''
    _logs_path: str = '$base_path/logs/all_logs_${date_now}.log'
    '''файл логов результата работы парсинга'''
    _cache_data_folder: str = '$base_path/data'
    '''папка с кешированными данным во время поиска, такие как html и json, необходимо для того чтобы запрос в сторонние сервисы делать только единожды, экономия трафика и времени работы. Нужно удалять вручную если необходимо сделать обновление данных'''
    _ya_images_folder: str = '$base_path/data/images'
    '''Папка с картинками jpg из яндекс'''
    log_level:str = 'DEBUG'
    '''уроверь логирования DEBUG, INFO, WARN, ERROR '''
    log_level_selenium:str = 'DEBUG'
    '''уроверь логирования для селениум, отличается от logging: DEBUG - это трассировочные логи, пишет очень много данных включая результаты полученных html, INFO - как debug режим пишет только основную информацию, WARN - только предупреждения и ошибки, ERROR - только ошибки '''
    
    zoon_details_replace_json = False
    '''перезаписать json деталей из html по zoon (если были правки парсинга в zoon_parser\parse_data.py, методе get_details_json)
    '''
    zoon_details_debug_log = False
    '''детальные логи при парсинге zoon
    '''
    # делать удаление перед записью или нет
    is_replace_file = False
    '''если True, то перед запускам удаляются временые таблицы результатов парсинга
    '''
    is_zoon_search_replace_html_request:bool = True
    '''перезатирать html из кеша (то есть запрос на сайт zoon будет всегда)'''
    is_zoon_search_replace_json_request:bool = True
    '''перезатирать JSON из кеша (то есть послу получения HTML парсится json и он будет перезатерт)'''

    is_ya_param_replace_json_request:bool = True
    '''Перезатирать json c параметрами для получения картинок из яндекса'''
    
    is_ya_param_g_replace_json_request:bool = True
    '''Перезатирать json c параметрами из Галереии для получения картинок из яндекса'''
    
    is_ya_param_g_replace_html_request:bool = True
    '''Перезатирать HTML c параметрами из Галереии для получения картинок из яндекса'''

    is_ya_rating_replace_html_request:bool = True
    '''Перезатирать html со страницы рейтинга для получения картинок из яндекса'''

    is_ya_using_cookies:bool = False
    '''Флаг, который указывает, нужно ли брать Cookie из ya_parser_headers_gallery, для того чтобы сделать запрос через selenium. Если false, тогда куки будут использовать по умолчанию, и в DEBUG логах запишется значение этих куки, для дальнейшей отладки'''

    load_from_trip:bool = False
    '''делать парсинг по trip advisor или нет. На данный момент отключено (False)
    '''
    load_from_zoon:bool = True
    '''делать парсинг по zoon.ru или нет'''

    load_images_from_ya:bool = True
    '''скачивать фотки или нет'''

    timeout_load_trip_details:int = 120
    '''таймаут для парсинга по trip advisor на странице деталей'''
    timeout_load_zoon_details:int = 120
    '''таймаут для парсинга по zoon на странице деталей'''
    timeout_load_trip_search:int = 120
    '''таймаут для парсинга по trip advisor на странице поиска'''
    timeout_load_zoon_search:int = 120
    '''таймаут для парсинга по zoon на странице поиска'''
    
    timeout_load_ya_image_params:int = 120
    '''таймаут для получения параметров фоток из яндекса'''
    timeout_load_ya_image:int = 120
    '''таймаут для получения фоток из яндекса'''
    top_load_ya_image:int = 10
    '''количество фоток, которые нужно забрать по каждому ресторану'''

    proxy:str = None
    '''domain прокси для парсинга'''
    
    zoon_parser_http_client:str = 'selenium'
    '''клиент для парсинга в zoon, можно использовать **requests**,**cloudscraper** или **selenium**'''

    zoon_parser_selenium_browser:str = 'chrome' #'firefox'
    '''браузер из selenium для парсинга в zoon, можно использовать **chrome**  или **firefox** (но для firefox пока не реализована возможность использовать прокси и не существует параметр для подстановки драйвера)'''

    zoon_parser_selenium_chromedriver_path:str = './lib/chromedriver-linux64-123.0.6312.122/chromedriver'
    '''путь к драйверу до бинарника chromedriver, необходимо иметь туже самую версию, которая установлена на среде где запускается парсинг
    '''



    ya_parser_http_client:str = 'selenium'
    '''клиент для парсинга в yandex, можно использовать **requests** или **selenium**'''

    ya_parser_selenium_browser:str = 'chrome' #'firefox'
    '''браузер из selenium для парсинга в yandex, можно использовать **chrome**  или **firefox** (но для firefox пока не реализована возможность использовать прокси и не существует параметр для подстановки драйвера)'''

    ya_parser_selenium_browser_param_headless:bool = True
    '''указывает нужно ли запускать браузер с параметром `--headless` этот параметр означает запуск браузера в фоновом режиме, по умолчанию True '''

    ya_parser_selenium_chromedriver_path:str = './lib/chromedriver-linux64-123.0.6312.122/chromedriver'
    '''путь к драйверу до бинарника chromedriver, необходимо иметь туже самую версию, которая установлена на среде где запускается парсинг
    '''


    list_replace_type_names:list = field(default_factory=lambda:[ 
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
    ])
    '''замена типов заведений для стандартизации'''

    list_replace_stop_word_adress:list = field(default_factory=lambda:[ 'бульвар'
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
        ,'село'
    ])
    '''удаление слов из адреса, для сравнения адресов'''

    city_list:list = field(default_factory=lambda:[        
        {'name': 'Москва', 'city': 'msk', "is_domain": True, 
        'replaces':['Россия, Центральный округ, Москва','Россия, Центральный округ, Московская Область','Москва, ','Московская область, ',', Москва'], 
        'center_point':(55.755864, 37.617698)},
        
        {'name': 'Московская область', 'city': 'msk', "is_domain": True, 
        'replaces':['Россия, Центральный округ, Москва','Россия, Центральный округ, Московская Область','Москва, ','Московская область, ',', Москва'], 
        'center_point':(55.755864, 37.617698)},
        
        {'name': 'Санкт-Петербург', 'city': 'spb', "is_domain": True, 
        'replaces':['Россия, Северо-Западный округ, Санкт-Петербург','Санкт-Петербург, ',', Санкт-Петербург'], 
        'center_point':(59.938784, 30.314997)},
        {'name': 'Новосибирск', 'city': 'nsk', "is_domain": True, 
        'replaces':['Россия, Сибирский округ, Новосибирская область, Новосибирский район, Новосибирск','Новосибирск, ',', Новосибирск'], 
        'center_point':(55.030204, 82.920430)},
        {'name': 'Екатеринбург', 'city': 'ekb', "is_domain": True, 
        'replaces':['Россия, Уральский округ, Свердловская область, Екатеринбург','Свердловская область, Екатеринбург, ',', Екатеринбург'], 
        'center_point':(56.838011, 60.597474)},
        {'name': 'Казань', 'city': 'kazan', "is_domain": True, 
        'replaces':['Россия, Приволжский округ, Республика Татарстан, Казань','Республика Татарстан, Казань, ',', Казань'], 
        'center_point':(55.796127, 49.106414)},
        {'name': 'Нижний Новгород', 'city': 'nn', "is_domain": True, 
        'replaces':['Россия, Приволжский округ, Нижегородская область, Нижний Новгород','Нижний Новгород, ',', Нижний Новгород'], 
        'center_point':(56.326797, 44.006516)},
        {'name': 'Челябинск', 'city': 'chelyabinsk', "is_domain": True, 
        'replaces':['Россия, Уральский округ, Челябинская область, Челябинск','Челябинск, '], 
        'center_point':(55.159902, 61.402554)},
        {'name': 'Красноярск', 'city': 'krasnoyarsk', "is_domain": True, 
        'replaces':['Россия, Сибирский округ, Красноярский край, Красноярск','Красноярск, ',', Красноярск'], 
        'center_point':(56.010569, 92.852572)},
        {'name': 'Самара', 'city': 'samara', "is_domain": True, 
        'replaces':['Россия, Приволжский округ, Самарская область, Самара','Самара, ',', Самара'], 
        'center_point':(53.195878, 50.100202)},
        {'name': 'Уфа', 'city': 'ufa', "is_domain": True, 
        'replaces':['Россия, Приволжский округ, Республика Башкортостан, Уфа','Республика Башкортостан, Уфа, ',', Уфа'], 
        'center_point':(54.735152, 55.958736)},
        {'name': 'Ростов-на-Дону', 'city': 'rostov', "is_domain": True, 
        'replaces':['Россия, Южный округ, Ростовская область, Ростов-на-Дону','Ростов-на-Дону, ',', Ростов-на-Дону'], 
        'center_point':(47.222078, 39.720358)},
        {'name': 'Омск', 'city': 'omsk', "is_domain": True, 
        'replaces':['Россия, Сибирский округ, Омская область, Омск','Омск, ',', Омск'], 
        'center_point':(54.989347, 73.368221)},
        {'name': 'Краснодар', 'city': 'krasnodar', "is_domain": True, 
        'replaces':['Россия, Южный округ, Краснодарский край, Краснодар','Краснодар, ',', Краснодар'], 
        'center_point':(45.035470, 38.975313)},
        {'name': 'Воронеж', 'city': 'voronezh', "is_domain": True, 
        'replaces':['Россия, Центральный округ, Воронежская область, Воронеж','Воронеж, ',', Воронеж'], 
        'center_point':(51.660781, 39.200296)},
        {'name': 'Пермь', 'city': 'perm', "is_domain": True, 
        'replaces':['Россия, Приволжский округ, Пермский край, Пермь','Пермь, ',', Пермь'], 
        'center_point':(58.010455, 56.229443)},
        {'name': 'Волгоград', 'city': 'volgograd', "is_domain": True, 
        'replaces':['Россия, Южный округ, Волгоградская область, Волгоград','Волгоград, ',', Волгоград'], 
        'center_point':(48.707067, 44.516975)},


        {'name': 'Сочи', 'city': 'sochi', "is_domain": True,'replaces':[
                    'Россия, Южный округ, Краснодарский край, Большой Сочи, Сочи, Адлерский район',
                    'Россия, Южный округ, Краснодарский край, Большой Сочи, Сочи',
                    'Россия, Южный округ, Краснодарский край',
                    'Краснодарский край, городской округ Сочи',
                    'Краснодарский край, Сочи, микрорайон',
                    'Краснодарский край, Сочи, жилой район',
                    'Краснодарский край, Сочи',
                    'Горная Олимпийская деревня',
                    ], 'center_point':(0, 0)},
        {'name': 'Анапа', 'city': 'anapa', "is_domain": True,'replaces':[], 'center_point':(0, 0)},
        {'name': 'Геленджик', 'city': 'gelendzhik', "is_domain": True,'replaces':[], 'center_point':(0, 0)},
        {'name': 'Владивосток', 'city': 'vladivostok', "is_domain": True,'replaces':[], 'center_point':(0, 0)},
        {'name': 'Калининград', 'city': 'kaliningrad', "is_domain": True,'replaces':[], 'center_point':(0, 0)},
        {'name': 'Хабаровск', 'city': 'habarovsk', "is_domain": True,'replaces':[], 'center_point':(0, 0)},
        {'name': 'Иркутск', 'city': 'irkutsk', "is_domain": True,'replaces':[], 'center_point':(0, 0)},

        {'name': 'sochi', 'name_ru':'Сочи', 'city': 'sochi', "is_domain": True, 
        'replaces':['Россия, Южный округ, Краснодарский край, Большой Сочи, Сочи, Адлерский район',
                    'Россия, Южный округ, Краснодарский край, Большой Сочи, Сочи',
                    'Россия, Южный округ, Краснодарский край',
                    'Краснодарский край, городской округ Сочи',
                    'Краснодарский край, Сочи, микрорайон',
                    'Краснодарский край, Сочи, жилой район',
                    'Краснодарский край, Сочи',
                    ], 
        'center_point':(48.707067, 44.516975)},

        {'name':'moscow', 'name_ru':'Москва', 'city':'moscow', 'replaces':[], 'center_point':(0,0)},
        {'name':'sankt-peterburg', 'name_ru':'Санкт-Петербург', 'city':'sankt-peterburg', 'replaces':[], 'center_point':(0,0)},
        {'name':'anapa', 'name_ru':'Анапа', 'city':'anapa', 'replaces':[], 'center_point':(0,0)},
        {'name':'ekaterinburg', 'name_ru':'Екатеринбург', 'city':'ekaterinburg', 'replaces':[], 'center_point':(0,0)},
        {'name':'rostov-na-donu', 'name_ru':'Ростов-на-Дону', 'city':'rostov-na-donu', 'replaces':[], 'center_point':(0,0)},
        {'name':'kazan', 'name_ru':'Казань', 'city':'kazan', 'replaces':[], 'center_point':(0,0)},
        {'name':'krasnodar', 'name_ru':'Краснодар', 'city':'krasnodar', 'replaces':[], 'center_point':(0,0)},
        {'name':'gelendzhik', 'name_ru':'Геленджик', 'city':'gelendzhik', 'replaces':[], 'center_point':(0,0)},
        {'name':'vladivostok', 'name_ru':'Владивосток', 'city':'vladivostok', 'replaces':[], 'center_point':(0,0)},
        {'name':'novosibirsk', 'name_ru':'Новосибирск', 'city':'novosibirsk', 'replaces':[], 'center_point':(0,0)},
        {'name':'samara', 'name_ru':'Самара', 'city':'Самара', 'replaces':[], 'center_point':(0,0)},
        {'name':'nizhnij novgorod', 'name_ru':'Нижний Новгород', 'city':'nizhnij novgorod', 'replaces':[], 'center_point':(0,0)},
        {'name':'irkutsk', 'name_ru':'Иркутск', 'city':'irkutsk', 'replaces':[], 'center_point':(0,0)},
        {'name':'kaliningrad', 'name_ru':'Калининград', 'city':'kaliningrad', 'replaces':[], 'center_point':(0,0)},
        {'name':'krasnoyarsk', 'name_ru':'Красноярск', 'city':'krasnoyarsk', 'replaces':[], 'center_point':(0,0)},
        {'name':'habarovsk', 'name_ru':'Хабаровск', 'city':'habarovsk', 'replaces':[], 'center_point':(0,0)},
        {'name':'voronezh', 'name_ru':'Воронеж', 'city':'voronezh', 'replaces':[], 'center_point':(0,0)},
        {'name':'omsk', 'name_ru':'Омск', 'city':'omsk', 'replaces':[], 'center_point':(0,0)},
        {'name':'chelyabinsk', 'name_ru':'Челябинск', 'city':'chelyabinsk', 'replaces':[], 'center_point':(0,0)},
        {'name':'ufa', 'name_ru':'Уфа', 'city':'ufa', 'replaces':[], 'center_point':(0,0)},
    ])


    ya_parser_headers_gallery:dict = field(default_factory=lambda:{
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Cookie': 'maps_los=0; is_gdpr=0; i=Kxvxo3OPNuCwzeVNRaGrfXfe2s/Em8w7Ity8QoodPsUA07RFNbLEmXwtgpd1EkzE5qULAeFzNWAcTy4I4J4MuHqkaEw=; yandexuid=4786207591695973728; yuidss=4786207591695973728; ymex=2011333729.yrts.1695973729; is_gdpr_b=CKDSYBCS0QEoAg==; _ym_uid=1695973729430834572; _ym_d=1695973730; yashr=2431041841696579811; cycada=Bb2gJVadcsVLrA/D1AidqogIJNFLRDTW1PEs0mFE0Ic=; yp=2014700099.pcs.0#1700837872.hdrc.1#1730876099.p_sw.1699340098#1699445301.szm.1_25:1536x864:1528x716#1730376505.p_cl.1698840504#1730376517.p_undefined.1698840516; bh=EkIiTWljcm9zb2Z0IEVkZ2UiO3Y9IjExOSIsICJDaHJvbWl1bSI7dj0iMTE5IiwgIk5vdD9BX0JyYW5kIjt2PSIyNCIaBSJ4ODYiIg8iMTE5LjAuMjE1MS40NCIqAj8wMgIiIjoJIldpbmRvd3MiQggiMTAuMC4wIkoEIjY0IlJdIk1pY3Jvc29mdCBFZGdlIjt2PSIxMTkuMC4yMTUxLjQ0IiwgIkNocm9taXVtIjt2PSIxMTkuMC42MDQ1LjEwNSIsICJOb3Q/QV9CcmFuZCI7dj0iMjQuMC4wLjAiWgI/MA==; gdpr=0; _ym_isad=2; spravka=dD0xNjk5NDM3MzkyO2k9NDYuNjEuMjQyLjIzO0Q9QzI1MUE0Mzk2RkJDMDNCNzdGODJFOEEyNjVCMjhEOTMzOUFGNzE2RkYyRTI4QjZEMkU1NUI3NEZCRjdEQjAwN0ZBNkExNUJDMkZFQjYxRTJDRUNBNUMwQUM1NTYyMUQyMDJGMTk0RTdEMkZFMDQxQTQ1MzUyQ0EwQ0RBRjdDQzEzODA4MDg5QTgzNzA1MDVBO3U9MTY5OTQzNzM5Mjg4MDEyOTI4MztoPTc2OTEwZGNhN2JiMDdmNzljNjE4NGVmZTFmYTM4MjNm; _yasc=BIB3QCytfG0iYfXyVSu1bsxaqPmF6GdVMY9gOl205Ed5b+kNxDPNfhpoX+v2X5dtYc8sbdg+pH7NctdlJ4Wj; bh=EkAiTWljcm9zb2Z0IEVkZ2UiO3Y9IjExOSIsIkNocm9taXVtIjt2PSIxMTkiLCJOb3Q/QV9CcmFuZCI7dj0iMjQiGgUieDg2IiIPIjExOS4wLjIxNTEuNDQiKgI/MDoJIldpbmRvd3MiQggiMTAuMC4wIkoEIjY0IlJcIk1pY3Jvc29mdCBFZGdlIjt2PSIxMTkuMC4yMTUxLjQ0IiwiQ2hyb21pdW0iO3Y9IjExOS4wLjYwNDUuMTA1IiwiTm90P0FfQnJhbmQiO3Y9IjI0LjAuMC4wIiI=',
        'Device-Memory': '8',
        'Downlink': '10',
        'Dpr': '1.25',
        'Ect': '4g',
        'Rtt': '0',
        'Sec-Ch-Ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'Sec-Ch-Ua-Arch': '"x86"',
        'Sec-Ch-Ua-Bitness': '"64"',
        'Sec-Ch-Ua-Full-Version': '"119.0.2151.44"',
        'Sec-Ch-Ua-Full-Version-List': '"Microsoft Edge";v="119.0.2151.44", "Chromium";v="119.0.6045.105", "Not?A_Brand";v="24.0.0.0"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Model': '""',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Ch-Ua-Platform-Version': '"10.0.0"',
        'Sec-Ch-Ua-Wow64': '?0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
        'Viewport-Width': '1528'
    })

    ya_parser_headers_token:dict = field(default_factory=lambda:{
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Cookie': 'is_gdpr=0; i=Kxvxo3OPNuCwzeVNRaGrfXfe2s/Em8w7Ity8QoodPsUA07RFNbLEmXwtgpd1EkzE5qULAeFzNWAcTy4I4J4MuHqkaEw=; yandexuid=4786207591695973728; yuidss=4786207591695973728; ymex=2011333729.yrts.1695973729; is_gdpr_b=CKDSYBCS0QEoAg==; _ym_uid=1695973729430834572; _ym_d=1695973730; yashr=2431041841696579811; cycada=Bb2gJVadcsVLrA/D1AidqogIJNFLRDTW1PEs0mFE0Ic=; yp=2014700099.pcs.0#1700837872.hdrc.1#1730876099.p_sw.1699340098#1699445301.szm.1_25:1536x864:1528x716#1730376505.p_cl.1698840504#1730376517.p_undefined.1698840516; bh=EkIiTWljcm9zb2Z0IEVkZ2UiO3Y9IjExOSIsICJDaHJvbWl1bSI7dj0iMTE5IiwgIk5vdD9BX0JyYW5kIjt2PSIyNCIaBSJ4ODYiIg8iMTE5LjAuMjE1MS40NCIqAj8wMgIiIjoJIldpbmRvd3MiQggiMTAuMC4wIkoEIjY0IlJdIk1pY3Jvc29mdCBFZGdlIjt2PSIxMTkuMC4yMTUxLjQ0IiwgIkNocm9taXVtIjt2PSIxMTkuMC42MDQ1LjEwNSIsICJOb3Q/QV9CcmFuZCI7dj0iMjQuMC4wLjAiWgI/MA==; gdpr=0; bh=EkAiTWljcm9zb2Z0IEVkZ2UiO3Y9IjExOSIsIkNocm9taXVtIjt2PSIxMTkiLCJOb3Q/QV9CcmFuZCI7dj0iMjQiGgUieDg2IiIPIjExOS4wLjIxNTEuNDQiKgI/MDoJIldpbmRvd3MiQggiMTAuMC4wIkoEIjY0IlJcIk1pY3Jvc29mdCBFZGdlIjt2PSIxMTkuMC4yMTUxLjQ0IiwiQ2hyb21pdW0iO3Y9IjExOS4wLjYwNDUuMTA1IiwiTm90P0FfQnJhbmQiO3Y9IjI0LjAuMC4wIiI=; _ym_visorc=b; _yasc=vbpN6auE2EGGo2YmK7QsCH4OKXhYGrtm69lJ1sm8PYbDLVKtJKhIhBvuxn9nG//I9VGC908lY5tGSdZsmeLK; _ym_isad=2; spravka=dD0xNjk5NDM3MzkyO2k9NDYuNjEuMjQyLjIzO0Q9QzI1MUE0Mzk2RkJDMDNCNzdGODJFOEEyNjVCMjhEOTMzOUFGNzE2RkYyRTI4QjZEMkU1NUI3NEZCRjdEQjAwN0ZBNkExNUJDMkZFQjYxRTJDRUNBNUMwQUM1NTYyMUQyMDJGMTk0RTdEMkZFMDQxQTQ1MzUyQ0EwQ0RBRjdDQzEzODA4MDg5QTgzNzA1MDVBO3U9MTY5OTQzNzM5Mjg4MDEyOTI4MztoPTc2OTEwZGNhN2JiMDdmNzljNjE4NGVmZTFmYTM4MjNm',
        'Device-Memory': '8',
        'Downlink': '10',
        'Dpr': '1.25',
        'Ect': '4g',
        'If-None-Match': 'W/"43-aTmVzDxL8/BvDxJrIgmtdcB2zz4"',
        'Rtt': '250',
        'Sec-Ch-Ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'Sec-Ch-Ua-Arch': '"x86"',
        'Sec-Ch-Ua-Bitness': '"64"',
        'Sec-Ch-Ua-Full-Version': '"119.0.2151.44"',
        'Sec-Ch-Ua-Full-Version-List': '"Microsoft Edge";v="119.0.2151.44", "Chromium";v="119.0.6045.105", "Not?A_Brand";v="24.0.0.0"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Model': '""',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Ch-Ua-Platform-Version': '"10.0.0"',
        'Sec-Ch-Ua-Wow64': '?0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
        'Viewport-Width': '1528'
    })

    ta_parser_headers:dict = field(default_factory=lambda:{})
    ta_parser_headers_search:dict = field(default_factory=lambda:{})

    ya_parser_headers_raiting:dict = field(default_factory=lambda:{
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
        'Origin': 'https://yandex.ru',
        'Referer': 'https://yandex.ru/',
        'Sec-Ch-Ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    })

    zoon_parser_headers:dict = field(default_factory=lambda:{
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
        'Cache-Control': 'max-age=0',
        'Cookie': 'locale=ru_RU; AATestGlobal=variation; anon_id=20230920095826SWst.2ddd; _ga=GA1.2.1291800659.1695193108; _ym_uid=1695193108677982975; _ym_d=1695193108; sid=98be808e6516d0244bfc9617793338; _gid=GA1.2.1208684991.1695993893; _ym_isad=2; city=msk; captcha_pass=eb498b420348e75212393672af8aa661; _gat=1; _ga_KK9RGD935B=GS1.2.1695999086.30.0.1695999086.60.0.0',
        'Referer': 'https://zoon.ru/search/',
        'Sec-Ch-Ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    })

    zoon_parser_headers_search:dict = field(default_factory=lambda:{
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Length': '183',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Cookie': 'anon_id=202405271130152nKR.0227; _ym_uid=1716798616133068309; _ym_d=1716798616; _ga=GA1.2.1399164107.1716798616; AATestGlobal=control; city=msk; _ga_KK9RGD935B=GS1.2.1721218245.4.1.1721218286.19.0.0; locale=ru_RU; sid=31dcf9a466990a0674358796234063',
        'Origin': 'https://zoon.ru',
        'Priority': 'u=1, i',
        'Referer': 'https://zoon.ru/ekb/restaurants/?search_query_form=1&center%5B%5D=56.81553064458854&center%5B%5D=60.72317535354089&zoom=11',
        'Sec-Ch-Ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    })


   

if __name__ == '__main__':
  #save to file:
  p = Params()
  print(type(p.zoon_parser_headers_search))
  #p.base_path = '/1/'
  print(p.yandex_data_file)
  #print(p.all_trip_details_file)
  with open('params.json','w',encoding='UTF-8') as f:
    json.dump(p,f,default=lambda o: o.__dict__,ensure_ascii=False,indent=2)
  

  #read from file
#   p = Params()
#   with open('params.json','r',encoding='UTF-8') as f:
#     p = json.load(f)
#   print(type(p),type(p.city_list),type(p.city_list[0]))
#   print(type(p.zoon_parser_headers_search),p.zoon_parser_headers_search)
#   print('done')
    
    from pydoc_markdown.interfaces import Context
    from pydoc_markdown.contrib.loaders.python import PythonLoader
    from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer

    context = Context(directory='.')
    loader = PythonLoader(packages=['params'],modules=['params'])
    renderer = MarkdownRenderer(
    render_module_header=False,
    insert_header_anchors= False,
    html_headers= False,
    code_headers= True,
    descriptive_class_title = False,
    descriptive_module_title= False,
    add_module_prefix= False,
    add_method_class_prefix= False,
    add_member_class_prefix= False,
    add_full_prefix= False,
    sub_prefix= False,
    data_code_block= False,
    data_expression_maxlength = 2,
    classdef_code_block= False,
    classdef_with_decorators= False,
    signature_python_help_style= False,
    signature_code_block= False,
    signature_in_header= False,
    signature_with_vertical_bar= True,
    signature_with_def= False,
    signature_class_prefix= False,
    signature_with_decorators= False,
    render_toc=False,
    format_code=False,
    header_level_by_type = {"Method": 4,
                "Function": 4,
                "Variable": 4,
                }
    
    )

    loader.init(context)
    renderer.init(context)

    modules = loader.load()
    result = renderer.render_to_string(modules)
    #print(len(result))

    from pathlib import Path

    path = Path('docs') / f'params.md'
    import os
    if os.path.isfile(path):
        os.remove(path)
    already_added_lines = []
    with open(path,'w',encoding='UTF-8') as f:
        for line in result.splitlines():
            if line in already_added_lines: continue
            if not line.startswith('## '):
                f.write(line + '\n')
                already_added_lines.append(line)
