import json

import redis


def redis_connect():
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    return r


# get weather condition through latitude and longitude by openweathermap api
def get_weather_condition(latitude, longitude):
    import requests
    import json
    url = "https://api-simile.como.polimi.it/v1/misc/weather?lat={lat}&lon={lon}".format(lat=latitude, lon=longitude)
    response = requests.request("GET", url, headers={}, data={})
    print(response.text)


def get_detail(userid):
    r = redis_connect()
    try:
        return json.loads(r.get(str(userid)+'_detail'))
    except TypeError:
        return None


def set_detail(userid, detail):
    r = redis_connect()
    return r.set(str(userid)+'_detail', json.dumps(detail))


def initialize_detail(userid):
    r = redis_connect()
    # return string
    return r.set(str(userid)+'_detail', json.dumps({
        "algae": {"checked": False, "extension": {"code": 0, "description": "string"},
                  "look": {"code": 0, "description": "string"}, "colour": {"code": 0, "description": "string"},
                  "iridescent": True}, "foams": {"checked": False, "look": {"code": 0, "description": "string"},
                                                 "extension": {"code": 0, "description": "string"},
                                                 "height": {"code": 0, "description": "string"}},
        "oils": {"checked": False, "type": {"code": 0, "description": "string"},
                 "extension": {"code": 0, "description": "string"}},
        "litters": {"checked": False, "quantity": {"code": 0, "description": "string"},
                    "type": [{"code": 0, "description": "string"}]},
        "odours": {"checked": False, "origin": [{"code": 0, "description": "string"}],
                   "intensity": {"code": 0, "description": "string"}},
        "outlets": {"checked": False, "inPlace": True, "terminal": {"code": 0, "description": "string"},
                    "colour": {"code": 0, "description": "string"}, "vapour": True, "signage": True,
                    "signagePhoto": "string", "prodActNearby": True, "prodActNearbyDetails": "string"},
        "fauna": {"checked": False, "fish": {"checked": False, "number": 0, "deceased": True,
                                             "abnormal": {"checked": True, "details": "string"},
                                             "alien": {"checked": True,
                                                       "species": [{"code": 0, "description": "string"}]}},
                  "birds": {"checked": False, "number": 0, "deceased": True,
                            "abnormal": {"checked": True, "details": "string"},
                            "alien": {"checked": False, "species": [{"code": 0, "description": "string"}]}},
                  "molluscs": {"checked": False, "number": 0, "deceased": True,
                               "abnormal": {"checked": True, "details": "string"},
                               "alien": {"checked": True, "species": [{"code": 0, "description": "string"}]}},
                  "crustaceans": {"checked": False, "number": 0, "deceased": True,
                                  "abnormal": {"checked": True, "details": "string"},
                                  "alien": {"checked": True, "species": [{"code": 0, "description": "string"}]}},
                  "turtles": {"checked": False, "number": 0, "deceased": True,
                              "abnormal": {"checked": True, "details": "string"},
                              "alien": {"checked": True, "species": [{"code": 0, "description": "string"}]}}}}))


if __name__ == '__main__':
    r = redis_connect()
    #get_detail(123)
    # r.hset('5267452153', mapping={'test': 'test'})
    # print(r.hgetall('1557079457'))
    # # to string
    # photo_1 = r.hgetall('1557079457')[b'photo_0'].decode('utf-8')
    # print(photo_1)
    #
    # # r.delete('5267452153')
    # # get_weather_condition(40.7128, -74.0060)
