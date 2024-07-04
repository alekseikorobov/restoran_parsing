

* Получение данных начинается по запуску файла [LoadData.py](LoadData.py)

```sh
python LoadData.py -h
usage: parsing restaurants [-h] [-b BASE_PATH] [-p PROXY] [-r]

options:
  -h, --help            show this help message and exit
  -b BASE_PATH, --base_path BASE_PATH
                        Базовый путь для всех файлов, откуда забираются данные для парсинга и куда кладутся вспомогательные и выходные файлы. Если не указано, используйте      
                        base_path из params.json.
  -p PROXY, --proxy PROXY
                        Прокси для всех http-запросов requests. См. proxy в params.json. По умолчанию None
  -r, --replace         если использовать этот флаг, то все файлы будут удалены перед запуском. По умолчанию false
```
по базовому пути ``base_path`` создаются следующие папки
* tables - в этой папке содержится входые и выходные данные
  * входной файл указан в параметрах в переменной ``_yandex_data_file``
  * выходной файл по сервису zoon из переменной ``_zoon_details_file``
* data
  * zoon - кеш данных скаченных html файлов из сервиса zoon.ru
  * yandex_r - кеш данных скаченных html файлов из рейтинга yndex.ru
  * images - фотографии из яндекса указаны в переменной ``_ya_images_folder``
* logs - папка с логами по маске названия из переменной ``_logs_path``

По указанному базовому пути ``base_path`` так же должен находиться файл со всеми параметрами ``params.json``