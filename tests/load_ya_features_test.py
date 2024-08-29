

#https://avatars.mds.yandex.net/get-altay/4737312/2a0000017abf099a6142bcc666c109dccd85/XXXL

import unittest
import numpy as np
import sys
sys.path.append('..')
import ya_parser.load_ya_features as load_ya_features
import json

class LoadYaFeaturesTest(unittest.TestCase):
  
  def my_assertEqual_action(self,func,case_list):
    for param,result in case_list:
      fact_result = func(param)
      self.assertEqual(result,fact_result)


  def test_ya_feature_service_selector(self):
    
    _load_ya_features = load_ya_features.LoadYaFeatures({})
    
    self.my_assertEqual_action(_load_ya_features.ya_feature_service_selector,case_list=[
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

  def test_get_params_1(self):
    _load_ya_features = load_ya_features.LoadYaFeatures({})
    html_files = [
      'data_unit_test/yandex_features/html/test/1004067747.html',
      'data_unit_test/yandex_features/html/test/1038599331.html',
      'data_unit_test/yandex_features/html/test/1051904212.html',
      'data_unit_test/yandex_features/html/test/1094622728.html',
      'data_unit_test/yandex_features/html/test/1118056242.html',
      'data_unit_test/yandex_features/html/test/1190590178.html',
      'data_unit_test/yandex_features/html/test/1227135267.html',
      'data_unit_test/yandex_features/html/test/1393651891.html',
      'data_unit_test/yandex_features/html/test/1681677798.html',
      'data_unit_test/yandex_features/html/test/44285147668.html',
      'data_unit_test/yandex_features/html/test/63055610828.html',
      'data_unit_test/yandex_features/html/test/196589415833.html',
    ]
    for html_file in html_files:
      with open(html_file,'r',encoding='UTF-8') as f:
        html_str = f.read()
        json_res = _load_ya_features.get_feature_from_html_json(html_str,"")
        
        p = _load_ya_features.extract_key("Цены/other/@Средний счёт",json_res)
        c = _load_ya_features.extract_key("Общая информация/other/@Кухня",json_res)
        print(html_file,p,c)

  def test_get_params(self):
    _load_ya_features = load_ya_features.LoadYaFeatures({})
    json_file = 'data_unit_test/yandex_features/html/1094622728.json'
    with open(json_file,'r',encoding='UTF-8') as f:
      result = json.load(f)
      
      for key, expect_value in [
        ("Цены/other/@Средний счёт","от 900 ₽"),
        ("Общая информация/other/@Кухня","европейская, итальянская, тайская, русская, японская, азиатская, домашняя, смешанная, вегетарианская"),
      ]:
        fact_value = _load_ya_features.extract_key(key,result)
        assert fact_value == expect_value
        
      fact_value = _load_ya_features.extract_list('Общая информация/list/*',result)
      fact_value = ','.join(fact_value)
      expect_value = 'Доставка еды,Еда навынос,Оплата картой,Wi-Fi,Кофе с собой,Детское меню,Завтрак,Бизнес-ланч'
      assert fact_value == expect_value,f'{fact_value=}, {expect_value=}'
      
  def test_check_html_features(self):
    _load_ya_features = load_ya_features.LoadYaFeatures({})
    
    html_files = [
      ('data_unit_test/yandex_features/html/1004067747.html',load_ya_features.StatusCheckHtml.ERROR_CAPCHA),
      ('data_unit_test/yandex_features/html/1051904212.html',load_ya_features.StatusCheckHtml.OK),
    ]
    
    for html_file, expect_status in html_files:
      with open(html_file,'r',encoding='UTF-8') as f:
        html_str = f.read()
        
        fact_status,_ = _load_ya_features.check_html_features(html_str)
        
        assert fact_status == expect_status
  
  def test_get_headers_from_line(self):
    _load_ya_features = load_ya_features.LoadYaFeatures({})
    
    test_cases = [
      ('a1234',f"not exits : line='a1234'",None),
      ('a:1234','a','1234'),
      ('a:','a',None),
      (':a',None,'a'),
      ('a:1234:123','a','1234:123'),
      ('',None,None),
      ('   ',None,None),
      (None,None,None),
      ('a:1234   ','a','1234'),
      ('a:    1234   ','a','1234'),
      ('    a:1234   ','a','1234'),
      ('    a     :1234   ','a','1234'),
    ]
    for line,k_expect,v_expect in test_cases:
      try:
        k_fact, v_fact = _load_ya_features.get_headers_from_line(line)
        assert k_fact == k_expect,f'{k_fact=} != {k_expect=}'
        assert v_fact == v_expect,f'{v_fact=} != {v_expect=}'
      except AttributeError as e:
        message_expect = k_expect
        message_fact = str(e)
        assert message_fact == message_expect,f'{message_fact=} != {message_expect=}'


  def test_get_headers_from_lines(self):
    _load_ya_features = load_ya_features.LoadYaFeatures({})
    
    test_cases = [      
      (['a1:1234','a2:1234:123'],{'a1':'1234','a2':'1234:123'}),
      (['a1:1234','a2:1234:123','a2:1234123'],'key a2 already exists in dict'),
      (['a11234'],"not exits : line='a11234'"),
      (['a1:1234',''],{'a1':'1234'}),
      (['a1:1234',':a'],{'a1':'1234'}),
      (['a1:1234','a:'],{'a1':'1234'}),
    ]
    for lines, headers_expect in test_cases:
      try:
        headers_fact = _load_ya_features.get_headers_from_lines(lines)
        assert headers_fact == headers_expect,f'{headers_fact=} != {headers_expect=}'
      except AttributeError as e:
        message_expect = headers_expect
        message_fact = str(e)
        assert message_fact == message_expect,f'{message_fact=} != {message_expect=}'
        print(message_fact)
      
    
    
  
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


