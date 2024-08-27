

#https://avatars.mds.yandex.net/get-altay/4737312/2a0000017abf099a6142bcc666c109dccd85/XXXL

import unittest
import numpy as np
import ya_parser.load_ya_features as load_ya_features
import json

class LoadYaFeaturesTest(unittest.TestCase):
  
  def my_assertEqual_action(self,func,case_list):
    for param,result in case_list:
      fact_result = func(param)
      self.assertEqual(result,fact_result)


  def test_ya_feature_service_selector(self):
    
    self.my_assertEqual_action(load_ya_features.ya_feature_service_selector,case_list=[
      ([
        'Услуги и удобства:Прачечная',
        'Питание:Ресторан',
      ],'Прачечная,Ресторан'),
      
      ([
        'Услуги и удобства:Прачечная1',
        'Питание:Ресторан1',
      ],''),
      
      ([
        'Услуги и удобства:Трансфер',
        'main_info:Трансфер',
      ],'Трансфер'),
      
      ([
        'Услуги и удобства:Круглосуточная стойка регистрации',
        'Услуги и удобства:Возможно проживание с животными',
        'Красота и здоровье:Spa',
      ],'Круглосуточная регистрация,Проживание с животными,Спа'),
      
      ([
        'Услуги и удобства:Круглосуточная стойка регистрации',
        'Инфраструктура:Парковка',
        'Услуги и удобства:Камера хранения',
        'Услуги и удобства:Прачечная',
        'Питание:Ресторан',
        'main_info:Завтрак',
        'Услуги и удобства:Трансфер',
        'Питание:Бар',
        'Бизнес-услуги:Конференц-зал',
        'Услуги и удобства:Возможно проживание с животными',
        'Услуги и удобства:Банкетный зал',
        'Красота и здоровье:Сауна',
        'Спорт и развлечения:Тренажёрный зал',
        'Спорт и развлечения:Бассейн',
        'Красота и здоровье:Spa',
        'main_info:Рядом с морем',
        'main_info:Трансфер',
      ],'Банкетный зал,Бар,Бассейн,Завтрак,Камера хранения,Конференц-зал,Круглосуточная регистрация,Парковка,Прачечная,'+
        'Проживание с животными,Ресторан,Рядом с морем,Сауна,Спа,Трансфер,Тренажёрный зал'),

      ('',''),
      (None,None),

    ])  


  def test_get_params(self):
    _load_ya_features = load_ya_features.LoadYaFeatures({})
    json_file = 'data_unit_test/yandex_features/html/1094622728.json'
    with open(json_file,'r',encoding='UTF-8') as f:
      result = json.load(f)

      expect_value = "от 900 ₽"

      fact_value = _load_ya_features.extract_key("Цены/other/@Средний счёт",result)
      assert fact_value == expect_value

  def test_get_json(self):

    _load_ya_features = load_ya_features.LoadYaFeatures({})

    html_file = 'data_unit_test/yandex_features/html/1094622728.html'
    json_file = 'data_unit_test/yandex_features/html/1094622728.json'
    html_files = [
        html_file
    ]

    for html_file in html_files:
      with open(html_file,'r',encoding='UTF-8') as f:
        html_str = f.read()
        json_res = _load_ya_features.get_feature_from_html_json(html_str,"")
      json_file = html_file.replace('.html','.json')
      with open(json_file,'w',encoding='UTF-8') as f:
        json.dump(json_res,f,ensure_ascii=False,indent=4)


if __name__ == '__main__':
    unittest.main()


