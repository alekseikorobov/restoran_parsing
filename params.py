from dataclasses import dataclass, field

@dataclass
class Params:
    def __init__(self, **entries):
        self.__dict__.update(entries)
    #входной фал для поиска
    yandex_data_file: str = 'tables\\dm_rest_yandex_data.parquet'
    temp_zoon_search_file: str = 'tables\\zoon_search.hd'
    temp_select_best_zoon_search_file: str = 'tables\\zoon_select_best.hd'

    #выходной файл по zoon
    zoon_details_file: str = 'tables\\zoon_details.parquet'
    temp_trip_search_file: str = 'tables\\trip_search.hd'
    temp_select_best_trip_search_file: str = 'tables\\trip_select_best.hd'
    trip_details_file: str = 'tables\\trip_details.parquet'
    
    all_trip_search_file: str = 'tables\\all_trip_search.hd'
    all_trip_details_file: str = 'tables\\all_trip_details.hd'
    all_zoon_details_file: str = 'tables\\all_zoon_details.hd'
    all_zoon_search_file: str = 'tables\\all_zoon_search.hd'
    using_all_db = True

    logs_path: str = 'logs/all_logs_$date_now.log'
    
    # перезаписать json деталей из html по zoon (если были правки парсинга в zoon_parser\parse_data.py, методе get_details_json)
    zoon_details_replace_json = False
    
    zoon_details_debug_log = False

    # делать удаление перед записью или нет
    is_replace_file = False

    using_all_db:bool = False
    load_from_trip:bool = False

    timeout_load_trip_details:int = 120
    timeout_load_zoon_details:int = 120
    timeout_load_trip_search:int = 120
    timeout_load_zoon_search:int = 120

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

    city_list:list = field(default_factory=lambda:[        
        {'name': 'Москва', 'city': 'msk', "is_domain": False, 
        'replaces':['Россия, Центральный округ, Москва','Россия, Центральный округ, Московская Область','Москва, ','Московская область, ',', Москва'], 
        'center_point':(55.755864, 37.617698)},
        
        {'name': 'Московская область', 'city': 'msk', "is_domain": False, 
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
        {'name': 'Самара', 'city': 'samara', "is_domain": False, 
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
        {'name': 'Воронеж', 'city': 'voronezh', "is_domain": False, 
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


   
import json
if __name__ == '__main__':
  #save to file:
  # p = Params()
  # print(p.all_trip_details_file)
  # with open('params.json','w',encoding='UTF-8') as f:
  #   json.dump(p,f,default=lambda o: o.__dict__,ensure_ascii=False,indent=2)
  

  #read from file
  p = Params()
  with open('params.json','r',encoding='UTF-8') as f:
    p = json.load(f)
  print('done')