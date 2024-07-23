

## Описание

Получение данных начинается по запуску файла [LoadData.py](LoadData.py)

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
### Описание всех параметров из файла [params.json](params.json) тут [docs/params.md](./docs/params.md)

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

## Пример запуска:


проверка:
```sh
find /base/path/folder
params.json
tables/dm_rest_yandex_data.parquet
```

выполенение:
```sh
python ./LoadData.py -b /base/path/folder -p 10.10.10.10
```
результат:
```sh
tree /base/path/folder

│   params.json
│
├───data
│   ├───images
│   │       1004067747_10878016_2a0000018c9be86d7b5616682494c0d72245.jpg
│   │       1004067747_11395962_2a0000018cb360fafe75e95f171d108e7082.jpg
│   ├───yandex_r
│   │   ├───ekb
│   │   └───volgograd
│   │       ├───gallery_html
│   │       │       1681677798.html
│   │       │
│   │       ├───gallery_json
│   │       │       1681677798.json
│   │       │
│   │       ├───gallery_param_json
│   │       │       1681677798.json
│   │       │
│   │       └───html
│   │               1681677798.html
│   │
│   └───zoon
│       ├───ekb
│       └───msk
│           ├───pages
│           │       kalyannaya_barviha_lounge_krasnaya_ploschad
│           │       restoran_mindal_v_sergievom_posade
│           ├───pages_json
│           │       kalyannaya_barviha_lounge_krasnaya_ploschad.json
│           │       restoran_mindal_v_sergievom_posade.json
│           └───search_p
│                   18_55.666788_37.551627.json
│                   18_55.666883_37.551879.json
│
├───logs
│       all_logs_20240704.log
└───tables
        dm_rest_yandex_data.parquet
        ya_image_params.hd
        zoon_details.parquet
        zoon_search.hd
        zoon_select_best.hd

```