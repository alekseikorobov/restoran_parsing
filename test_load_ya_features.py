
import common.common as common
import time

class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)
driver = common.get_global_driver(Struct( **{
  'proxy':None,
  'zoon_parser_selenium_browser':'chrome',
  'zoon_parser_selenium_chromedriver_path':"c:/work/restoran_to_dadm/lib/chromedriver-win64-126.0.6478.182/chromedriver.exe",
  'log_level_selenium':'INFO',
  'ya_parser_selenium_browser_param_headless':True,
}))

full_url = 'https://yandex.ru/maps/org/svoya_kompaniya/1094622728/?tab=features'
full_url = 'https://yandex.ru/maps/org/svoya_kompaniya/1094622728/features/'
full_url = 'https://yandex.ru/maps/org/svoya_kompaniya/1094622728/'

driver.get(full_url)
html_result = driver.page_source

with open('test.html','w',encoding='UTF-8') as f:
  f.write(html_result)

#time.sleep(100000)

print('done')