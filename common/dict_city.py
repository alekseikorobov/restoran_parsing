

def get_line_by_city_name(city_name, city_list):
    city_line = next(filter(lambda x:x['name'] == city_name, city_list),None)
    assert city_line is not None, f"not found {city_name=}"
    return city_line

def get_line_by_city_code(city_code, city_list):
    city_line = next(filter(lambda x:x['city'] == city_code, city_list),None)
    assert city_line is not None, f"not found {city_code=}"
    return city_line

def check_city(city_code, city_list):
    city_line = next(filter(lambda x:x['city'] == city_code, city_list),None)
    return city_line is not None