
#### `base_path`
Базовый путь к файлам, используется как раметр $base_path
#### `yandex_data_file`
Возвращает _yandex_data_file с подстановкой параметра base_path
#### `temp_zoon_search_file`
Возвращает _temp_zoon_search_file с подстановкой параметра base_path
#### `temp_select_best_zoon_search_file`
Возвращает _temp_select_best_zoon_search_file с подстановкой параметра base_path
#### `zoon_details_file`
Возвращает _zoon_details_file с подстановкой параметра base_path
#### `temp_trip_search_file`
Возвращает _temp_trip_search_file с подстановкой параметра base_path
#### `temp_select_best_trip_search_file`
Возвращает _temp_select_best_trip_search_file с подстановкой параметра base_path
#### `trip_details_file`
Возвращает _trip_details_file с подстановкой параметра base_path
#### `cache_data_folder`
Возвращает _cache_data_folder с подстановкой параметра base_path
#### `ya_image_params_file`
Возвращает _ya_image_params_file с подстановкой параметра base_path
#### `ya_images_folder`
Возвращает _ya_images_folder с подстановкой параметра base_path
#### `logs_path`
Возвращает _logs_path с подстановкой параметра base_path и date_now в заданом формате параметра date_time_format
#### `date_time_format`
Параметр для форматирования даты логирования, по умолчанию %Y%m%d_%H%M%S
#### `_yandex_data_file`
таблица входного фала для поиска
#### `_temp_zoon_search_file`
временный файл результата парсинга со страницы поиска из zoon.ru
#### `_temp_select_best_zoon_search_file`
временный файл результата выбора лучшего соответствия между данными из яндекса и zoon.ru со страницы поиска
#### `_zoon_details_file`
выходной файл результата парсинга из zoon.ru
#### `_temp_trip_search_file`
#### `_temp_select_best_trip_search_file`
#### `_trip_details_file`
#### `_ya_image_params_file`
параметры (+ прямые ссылки) по картинкам из яндекса
#### `_logs_path`
файл логов результата работы парсинга
#### `_cache_data_folder`
папка с кешированными данным во время поиска, такие как html и json, необходимо для того чтобы запрос в сторонние сервисы делать только единожды, экономия трафика и времени работы. Нужно удалять вручную если необходимо сделать обновление данных
#### `_ya_images_folder`
Папка с картинками jpg из яндекс
#### `log_level`
уроверь логирования DEBUG, INFO, WARN, ERROR
#### `log_level_selenium`
уроверь логирования для селениум, отличается от logging: DEBUG - это трассировочные логи, пишет очень много данных включая результаты полученных html, INFO - как debug режим пишет только основную информацию, WARN - только предупреждения и ошибки, ERROR - только ошибки
#### `zoon_details_replace_json`
перезаписать json деталей из html по zoon (если были правки парсинга в zoon_parser\parse_data.py, методе get_details_json)
#### `zoon_details_debug_log`
детальные логи при парсинге zoon
#### `is_replace_file`
если True, то перед запускам удаляются временые таблицы результатов парсинга
#### `is_zoon_search_replace_html_request`
перезатирать html из кеша (то есть запрос на сайт zoon будет всегда)
#### `is_zoon_search_replace_json_request`
перезатирать JSON из кеша (то есть послу получения HTML парсится json и он будет перезатерт)
#### `is_ya_param_replace_json_request`
Перезатирать json c параметрами для получения картинок из яндекса
#### `is_ya_param_g_replace_json_request`
Перезатирать json c параметрами из Галереии для получения картинок из яндекса
#### `is_ya_param_g_replace_html_request`
Перезатирать HTML c параметрами из Галереии для получения картинок из яндекса
#### `is_ya_rating_replace_html_request`
Перезатирать html со страницы рейтинга для получения картинок из яндекса
#### `is_ya_using_cookies`
Флаг, который указывает, нужно ли брать Cookie из ya_parser_headers_gallery, для того чтобы сделать запрос через selenium. Если false, тогда куки будут использовать по умолчанию, и в DEBUG логах запишется значение этих куки, для дальнейшей отладки
#### `load_from_trip`
делать парсинг по trip advisor или нет. На данный момент отключено (False)
#### `load_from_zoon`
делать парсинг по zoon.ru или нет
#### `load_images_from_ya`
скачивать фотки или нет
#### `timeout_load_trip_details`
таймаут для парсинга по trip advisor на странице деталей
#### `timeout_load_zoon_details`
таймаут для парсинга по zoon на странице деталей
#### `timeout_load_trip_search`
таймаут для парсинга по trip advisor на странице поиска
#### `timeout_load_zoon_search`
таймаут для парсинга по zoon на странице поиска
#### `timeout_load_ya_image_params`
таймаут для получения параметров фоток из яндекса
#### `timeout_load_ya_image`
таймаут для получения фоток из яндекса
#### `top_load_ya_image`
количество фоток, которые нужно забрать по каждому ресторану
#### `proxy`
domain прокси для парсинга
#### `zoon_parser_http_client`
клиент для парсинга в zoon, можно использовать **requests**,**cloudscraper** или **selenium**
#### `zoon_parser_selenium_browser`
браузер из selenium для парсинга в zoon, можно использовать **chrome**  или **firefox** (но для firefox пока не реализована возможность использовать прокси и не существует параметр для подстановки драйвера)
#### `zoon_parser_selenium_chromedriver_path`
путь к драйверу до бинарника chromedriver, необходимо иметь туже самую версию, которая установлена на среде где запускается парсинг
#### `ya_parser_http_client`
клиент для парсинга в yandex, можно использовать **requests** или **selenium**
#### `ya_parser_selenium_browser`
браузер из selenium для парсинга в yandex, можно использовать **chrome**  или **firefox** (но для firefox пока не реализована возможность использовать прокси и не существует параметр для подстановки драйвера)
#### `ya_parser_selenium_browser_param_headless`
указывает нужно ли запускать браузер с параметром `--headless` этот параметр означает запуск браузера в фоновом режиме, по умолчанию True
#### `ya_parser_selenium_chromedriver_path`
#### `list_replace_type_names`
замена типов заведений для стандартизации
#### `list_replace_stop_word_adress`
удаление слов из адреса, для сравнения адресов
#### `city_list`
#### `ya_parser_headers_gallery`
#### `ya_parser_headers_token`
#### `ta_parser_headers`
#### `ta_parser_headers_search`
#### `ya_parser_headers_raiting`
#### `zoon_parser_headers`
#### `zoon_parser_headers_search`
