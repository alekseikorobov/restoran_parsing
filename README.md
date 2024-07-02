

* Получение данных начинается по запуску файла [LoadData.py](LoadData.py)
* внутри прописано что на вход подается файл [tables/tran_yandex_data.xlsx](tables/tran_yandex_data.xlsx)
* на выходе получаем два файла:
  * [tables\zoon_details.xlsx](tables\zoon_details.xlsx)
  * [tables\trip_details.xlsx](tables\trip_details.xlsx)
* Для получения картинок сначала запускается файл [load_image_param_from_ya.py](load_image_param_from_ya.py)
* После этого запускается файл [load_image_from_ya.py](load_image_from_ya.py)
* есть небольшое количество тестов в файле [unit_test.py](unit_test.py)
* файл [dict\validate_map_rest.xlsx](dict\validate_map_rest.xlsx) - собран вручную для корректировки полученных данных (приоритезация или выборка для итоговых значений полученных из внешних источников), в дальнейшем планируется дополняться