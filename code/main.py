import requests
from telebot import asyncio_filters, types, asyncio_helper
from telebot.async_telebot import AsyncTeleBot
# list of storages, you can use any storage
from telebot.asyncio_storage import StateMemoryStorage

from gpt import send_request
from redis_connect import redis_connect, set_detail, get_detail, initialize_detail
# new feature for states.
from telebot.asyncio_handler_backends import State, StatesGroup

bot = AsyncTeleBot("6017081313:AAEOcs4hC7rMepl2f2X6pfpqqNVQr1afaz8", state_storage=StateMemoryStorage())
photo_list = []
r = redis_connect()


class MyStates(StatesGroup):
    start = State()
    photo_0 = State()
    photo_1 = State()
    photo_finished = State()
    location_finished = State()
    algae_0 = State()
    algae_1 = State()
    algae_2 = State()
    algae_3 = State()
    foam_0 = State()
    foam_1 = State()
    foam_2 = State()
    oil_0 = State()
    oil_1 = State()
    litters_0 = State()
    litters_1 = State()
    odours_0 = State()
    odours_1 = State()
    drains_0 = State()
    drains_1 = State()
    drains_2 = State()
    drains_3 = State()
    drains_4 = State()
    drains_5 = State()
    drains_6 = State()
    drains_7 = State()
    fish_0 = State()
    fish_1 = State()
    fish_2 = State()
    fish_3 = State()
    fish_4 = State()


@bot.message_handler(commands=['start'])
async def send_welcome(message):
    # file_path = await bot.get_file(
    #     'AgACAgUAAxkBAAIB4GRrr_HBo-CnHcdc0jkp1tNdjc3KAAKStzEb_T5gV68UIrltBsg-AQADAgADeQADLwQ')
    # downloaded_file = await bot.download_file(file_path.file_path)
    # with open('file.jpg', 'wb') as new_file:
    #     new_file.write(downloaded_file)
    # print(message.chat.id)
    print(await bot.get_state(message.from_user.id, message.chat.id))
    await bot.reply_to(message, "👋Ciao! Welcome to Simile Bot. \nMaybe you can upload a photo of lake now?")
    await bot.set_state(message.from_user.id, MyStates.start, message.chat.id)


@bot.message_handler(commands=['continue'])
async def to_continue(message):
    if get_detail(message.from_user.id) is None:
        await bot.send_message(message.chat.id, "🙏Sorry, you have no unfinished report, /start for a new report.")
        return
    await bot.send_message(message.chat.id, "‼️Unfinished report detected! Click the detail you want to "
                                            "describe.\n/algae /foam /oilStains /litters /odours /drains /fish /birds"
                                            " /molluscs /crustaceans /turtles")
    await bot.set_state(message.from_user.id, MyStates.location_finished, message.chat.id)


@bot.message_handler(content_types=['photo'], state=MyStates.photo_1)
async def handle_user_pic_2(message):
    r.hset(message.chat.id, mapping={'photo_2': message.photo[-1].file_id})
    await bot.set_state(message.from_user.id, MyStates.photo_finished, mesnumsage.chat.id)
    await bot.reply_to(message, "Could you please send me your current location?💠")


@bot.message_handler(content_types=['photo'], state=MyStates.photo_0)
async def handle_user_pic_1(message):
    await bot.set_state(message.from_user.id, MyStates.photo_1, message.chat.id)
    r.hset(message.chat.id, mapping={'photo_1': message.photo[-1].file_id})
    await bot.send_message(message.from_user.id, "🧩Send another photo or click /photo_finished")


@bot.message_handler(content_types=['photo'], state=MyStates.start)
async def handle_user_pic_0(message):
    await bot.set_state(message.from_user.id, MyStates.photo_0, message.chat.id)
    r.hset(message.chat.id, mapping={'photo_0': message.photo[-1].file_id})
    await bot.send_message(message.from_user.id, "🧩Send another photo or click /photo_finished")


# get weather condition through latitude and longitude by openweathermap api
def get_weather_condition(latitude, longitude):
    import requests
    import json
    url = "https://api-simile.como.polimi.it/v1/misc/weather?lat={lat}&lon={lon}".format(lat=latitude, lon=longitude)
    response = requests.request("GET", url, headers={}, data={})
    # jsonify
    weather_condition = json.loads(response.text)
    return weather_condition


# state can be accepted if it is in photo_0 or photo_1 or photo_finished
@bot.message_handler(commands=['photo_finished'], state=[MyStates.photo_0, MyStates.photo_1, MyStates.photo_finished])
async def handle_photo_finished(message):
    print(message.chat.id)
    # set state photo_finished
    await bot.set_state(message.from_user.id, MyStates.photo_finished, message.chat.id)
    await bot.send_message(message.chat.id, "🏬Could you please send me your current location?")


@bot.message_handler(content_types=['location'], state=MyStates.photo_finished)
async def handle_location(message):
    initialize_detail(message.from_user.id)
    print("{0}, {1}".format(message.location.latitude, message.location.longitude))
    weather_condition = get_weather_condition(message.location.latitude, message.location.longitude)
    if weather_condition['meta']['code'] != 200:
        await bot.send_message(message.chat.id, "‼Sorry, we can't get weather condition for you.")
        return
    weather_condition = weather_condition['data']
    r.hset(message.chat.id, mapping={'latitude': message.location.latitude, 'longitude': message.location.longitude,
                                     'sky': weather_condition['sky'], 'temperature': weather_condition['temperature'],
                                     'wind': weather_condition['wind']})
    await bot.set_state(message.from_user.id, MyStates.location_finished, message.chat.id)
    await bot.send_message(message.chat.id, "🌡️The weather condition is {0}, temperature is {1} celsius degree and wind "
                                            "is {2}".format(weather_condition['sky'], weather_condition['temperature'],
                                                            weather_condition['wind']))
    await bot.send_message(message.chat.id,
                           "✔️Now you have successfully uploaded the photos and location. It is time to add details and measurements. Click /details to see the list. If you have no detail want to submit, click /submit")


@bot.message_handler(commands=['details'], state=MyStates.location_finished)
async def handle_list(message):
    await bot.send_message(message.chat.id,
                           "ℹ️Click the detail you want to describe.\n/algae /foam /oilStains /litters /odours /drains /fish")


@bot.message_handler(commands=['detail'], state=MyStates.location_finished)
async def handle_list(message):
    await bot.send_message(message.chat.id,
                           "ℹ️Click the detail you want to describe.\n/algae /foam /oilStains /litters /odours /drains /fish")


@bot.message_handler(commands=['algae'], state=MyStates.location_finished)
async def handle_algae_0(message):
    markup = types.ReplyKeyboardMarkup()
    markup.add('<5 sq.m', '5-20 sq.m', '>20 sq.m')
    await bot.set_state(message.from_user.id, MyStates.algae_0, message.chat.id)
    await bot.send_message(message.chat.id, "You want to talk about algae! What is the extension of the algae?",
                           reply_markup=markup)


@bot.message_handler(content_types=['text'], state=MyStates.algae_0)
async def handle_algae_1(message):
    detail = get_detail(message.from_user.id)
    detail['algae']['checked'] = True
    if message.text == '<5 sq.m':
        detail['algae']['extension'] = {'code': 1, 'description': '< 5 sq. m'}
    elif message.text == '5-20 sq.m':
        detail['algae']['extension'] = {'code': 2, 'description': '5 - 20 sq. m'}
    elif message.text == '>20 sq.m':
        detail['algae']['extension'] = {'code': 3, 'description': '> 20 sq. m'}
    else:
        await bot.send_message(message.chat.id, "Please choose the extension of the algae")
        return
    set_detail(message.from_user.id, detail)
    markup = types.ReplyKeyboardMarkup()
    markup.add('Scattered', 'Compact', 'Grouped', 'Surface stripes')
    await bot.set_state(message.from_user.id, MyStates.algae_1, message.chat.id)
    await bot.send_message(message.chat.id, "Please choose the looking of the algae.", reply_markup=markup)


@bot.message_handler(content_types=['text'], state=MyStates.algae_1)
async def handle_algae_2(message):
    detail = get_detail(message.from_user.id)
    if message.text == 'Scattered':
        detail['algae']['look'] = {'code': 1, 'description': 'Scattered'}
    elif message.text == 'Compact':
        detail['algae']['look'] = {'code': 2, 'description': 'Compact'}
    elif message.text == 'Grouped':
        detail['algae']['look'] = {'code': 3, 'description': 'Grouped'}
    elif message.text == 'Surface stripes':
        detail['algae']['look'] = {'code': 4, 'description': 'Surface stripes'}
    else:
        await bot.send_message(message.chat.id, "Please choose the looking of the algae")
        return
    set_detail(message.from_user.id, detail)
    markup = types.ReplyKeyboardMarkup()
    markup.add('red', 'blue', 'green', 'grey', 'brown')
    await bot.set_state(message.from_user.id, MyStates.algae_2, message.chat.id)
    await bot.send_message(message.chat.id, "Please choose the colour of the algae.", reply_markup=markup)


@bot.message_handler(content_types=['text'], state=MyStates.algae_2)
async def handle_algae_3(message):
    detail = get_detail(message.from_user.id)
    if message.text == 'red':
        detail['algae']['colour'] = {'code': 1, 'description': 'Red'}
    elif message.text == 'blue':
        detail['algae']['colour'] = {'code': 2, 'description': 'Blu'}
    elif message.text == 'green':
        detail['algae']['colour'] = {'code': 3, 'description': 'Green'}
    elif message.text == 'grey':
        detail['algae']['colour'] = {'code': 4, 'description': 'Grey'}
    elif message.text == 'brown':
        detail['algae']['colour'] = {'code': 5, 'description': 'Brown'}
    else:
        await bot.send_message(message.chat.id, "Please choose the colour of the algae")
        return
    set_detail(message.from_user.id, detail)
    markup = types.ReplyKeyboardMarkup()
    markup.add('Yes', 'No')
    await bot.set_state(message.from_user.id, MyStates.algae_3, message.chat.id)
    await bot.send_message(message.chat.id, "And is the algae iridescent?", reply_markup=markup)


@bot.message_handler(content_types=['text'], state=MyStates.algae_3)
async def handle_algae_4(message):
    detail = get_detail(message.from_user.id)
    if message.text == 'Yes':
        detail['algae']['iridescent'] = True
    elif message.text == 'No':
        detail['algae']['iridescent'] = False
    else:
        await bot.send_message(message.chat.id, "Please choose whether the algae is iridescent")
        return
    set_detail(message.from_user.id, detail)
    await bot.set_state(message.from_user.id, MyStates.location_finished, message.chat.id)
    await bot.send_message(message.chat.id,
                           "Algae information is finished! /details to describe more details, /submit to submit the information.",
                           reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['foam'], state=MyStates.location_finished)
async def handle_foam_0(message):
    markup = types.ReplyKeyboardMarkup()
    markup.add('<5 sq.m', '5-20 sq.m', '>20 sq.m')
    await bot.set_state(message.from_user.id, MyStates.foam_0, message.chat.id)
    await bot.send_message(message.chat.id, "You want to talk about foams! What is the extension of the foams?",
                           reply_markup=markup)


@bot.message_handler(content_types=['text'], state=MyStates.foam_0)
async def handle_foam_1(message):
    detail = get_detail(message.from_user.id)
    detail['foams']['checked'] = True
    if message.text == '<5 sq.m':
        detail['foams']['extension'] = {'code': 1, 'description': '< 5 sq. m'}
    elif message.text == '5-20 sq.m':
        detail['foams']['extension'] = {'code': 2, 'description': '5 - 20 sq. m'}
    elif message.text == '>20 sq.m':
        detail['foams']['extension'] = {'code': 3, 'description': '> 20 sq. m'}
    else:
        await bot.send_message(message.chat.id, "Please choose the extension of the foam")
        return
    set_detail(message.from_user.id, detail)
    markup = types.ReplyKeyboardMarkup()
    markup.add('Scattered', 'Compact', 'Linear')
    await bot.set_state(message.from_user.id, MyStates.foam_1, message.chat.id)
    await bot.send_message(message.chat.id, "Please choose the looking of the foams.", reply_markup=markup)


@bot.message_handler(content_types=['text'], state=MyStates.foam_1)
async def handle_foam_2(message):
    detail = get_detail(message.from_user.id)
    if message.text == 'Scattered':
        detail['foams']['look'] = {'code': 1, 'description': 'Scattered'}
    elif message.text == 'Compact':
        detail['foams']['look'] = {'code': 2, 'description': 'Compact'}
    elif message.text == 'Linear':
        detail['foams']['look'] = {'code': 3, 'description': 'Linear'}
    else:
        await bot.send_message(message.chat.id, "Please choose the looking of the foam")
        return
    set_detail(message.from_user.id, detail)
    markup = types.ReplyKeyboardMarkup()
    markup.add('< 3 cm', '3 - 20 cm', '> 20 cm')
    await bot.set_state(message.from_user.id, MyStates.foam_2, message.chat.id)
    await bot.send_message(message.chat.id, "Please choose the height of the algae.", reply_markup=markup)


@bot.message_handler(content_types=['text'], state=MyStates.foam_2)
async def handle_foam_3(message):
    detail = get_detail(message.from_user.id)
    if message.text == '< 3 cm':
        detail['foams']['height'] = {'code': 1, 'description': '< 3 cm'}
    elif message.text == '3 - 20 cm':
        detail['foams']['3 - 20 cm'] = {'code': 2, 'description': '3 - 20 cm'}
    elif message.text == '> 20 cm':
        detail['foams']['height'] = {'code': 3, 'description': '> 20 cm'}
    else:
        await bot.send_message(message.chat.id, "Please choose the height of the algae")
        return
    set_detail(message.from_user.id, detail)
    await bot.set_state(message.from_user.id, MyStates.location_finished, message.chat.id)
    await bot.send_message(message.chat.id,
                           "Foams information is finished! /details to describe more , /submit to submit the information.",
                           reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['oilStains'], state=MyStates.location_finished)
async def handle_oil_0(message):
    markup = types.ReplyKeyboardMarkup()
    markup.add('<5 sq.m', '5-20 sq.m', '>20 sq.m')
    await bot.set_state(message.from_user.id, MyStates.oil_0, message.chat.id)
    await bot.send_message(message.chat.id,
                           "You want to talk about oil stains! What is the extension of the oil stain?",
                           reply_markup=markup)


@bot.message_handler(content_types=['text'], state=MyStates.oil_0)
async def handle_oil_1(message):
    detail = get_detail(message.from_user.id)
    detail['oils']['checked'] = True
    if message.text == '<5 sq.m':
        detail['oils']['extension'] = {'code': 1, 'description': '< 5 sq. m'}
    elif message.text == '5-20 sq.m':
        detail['oils']['extension'] = {'code': 2, 'description': '5 - 20 sq. m'}
    elif message.text == '>20 sq.m':
        detail['oils']['extension'] = {'code': 3, 'description': '> 20 sq. m'}
    else:
        await bot.send_message(message.chat.id, "Please choose the extension of the oil stain")
        return
    set_detail(message.from_user.id, detail)
    markup = types.ReplyKeyboardMarkup()
    markup.add('On surface', 'In depth')
    await bot.set_state(message.from_user.id, MyStates.oil_1, message.chat.id)
    await bot.send_message(message.chat.id, "Please choose the type of the oil stains.", reply_markup=markup)


@bot.message_handler(content_types=['text'], state=MyStates.oil_1)
async def handle_oil_2(message):
    detail = get_detail(message.from_user.id)
    if message.text == 'On surface':
        detail['oils']['type'] = {'code': 1, 'description': 'On surface'}
    elif message.text == 'In depth':
        detail['oils']['type'] = {'code': 2, 'description': 'In depth'}
    else:
        await bot.send_message(message.chat.id, "Please choose the type of the oil")
        return
    set_detail(message.from_user.id, detail)
    await bot.set_state(message.from_user.id, MyStates.location_finished, message.chat.id)
    await bot.send_message(message.chat.id,
                           "Oil stains information is finished! /details to describe more details, /submit to submit the information",
                           reply_markup=types.ReplyKeyboardRemove())
    print(detail)


@bot.message_handler(commands=['litters'], state=MyStates.location_finished)
async def handle_litters_0(message):
    markup = types.ReplyKeyboardMarkup()
    markup.add('1', '2 - 20', '> 20')
    await bot.set_state(message.from_user.id, MyStates.litters_0, message.chat.id)
    await bot.send_message(message.chat.id,
                           "You want to talk about litters! What is the quantity of the litters?",
                           reply_markup=markup)


@bot.message_handler(content_types=['text'], state=MyStates.litters_0)
async def handle_litters_1(message):
    detail = get_detail(message.from_user.id)
    detail['litters']['checked'] = True
    if message.text == '1':
        detail['litters']['quantity'] = {'code': 1, 'description': '1'}
    elif message.text == '2 - 20':
        detail['litters']['quantity'] = {'code': 2, 'description': '2 - 20'}
    elif message.text == '> 20':
        detail['litters']['quantity'] = {'code': 3, 'description': '> 20'}
    else:
        await bot.send_message(message.chat.id, "Please choose the quantity of the litters")
        return
    set_detail(message.from_user.id, detail)
    markup = types.ReplyKeyboardMarkup()
    markup.add('Plastic', 'Glass / Ceramic', 'Metal', 'Paper / Cardboard', 'Textiles', 'Rubber', 'Treated wood',
               'Bricks', 'Vegetal debris', 'Decaying organic material')
    await bot.set_state(message.from_user.id, MyStates.litters_1, message.chat.id)
    await bot.send_message(message.chat.id, "Please choose the type of the litters.", reply_markup=markup)


@bot.message_handler(content_types=['text'], state=MyStates.litters_1)
async def handle_litters_2(message):
    detail = get_detail(message.from_user.id)
    if message.text == 'Plastic':
        detail['litters']['type'] = {'code': 1, 'description': 'Plastic'}
    elif message.text == 'Glass / Ceramic':
        detail['litters']['type'] = {'code': 2, 'description': 'Glass / Ceramic'}
    elif message.text == 'Metal':
        detail['litters']['type'] = {'code': 3, 'description': 'Metal'}
    elif message.text == 'Paper / Cardboard':
        detail['litters']['type'] = {'code': 4, 'description': 'Paper / Cardboard'}
    elif message.text == 'Textiles':
        detail['litters']['type'] = {'code': 5, 'description': 'Textiles'}
    elif message.text == 'Rubber':
        detail['litters']['type'] = {'code': 6, 'description': 'Rubber'}
    elif message.text == 'Treated wood':
        detail['litters']['type'] = {'code': 7, 'description': 'Treated wood'}
    elif message.text == 'Bricks':
        detail['litters']['type'] = {'code': 8, 'description': 'Bricks'}
    elif message.text == 'Vegetal debris':
        detail['litters']['type'] = {'code': 9, 'description': 'Vegetal debris'}
    elif message.text == 'Decaying organic material':
        detail['litters']['type'] = {'code': 10, 'description': 'Decaying organic material'}
    else:
        await bot.send_message(message.chat.id, "Please choose the type of the litters")
        return
    set_detail(message.from_user.id, detail)
    await bot.set_state(message.from_user.id, MyStates.location_finished, message.chat.id)
    await bot.send_message(message.chat.id,
                           "Litters information is finished! /details to describe more details, /submit to submit the information.",
                           reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['odours'], state=MyStates.location_finished)
async def handle_odours_0(message):
    markup = types.ReplyKeyboardMarkup()
    markup.add('Slight', 'Medium', 'Strong')
    await bot.set_state(message.from_user.id, MyStates.odours_0, message.chat.id)
    await bot.send_message(message.chat.id,
                           "You want to talk about odours! What is the intensity of the odours?",
                           reply_markup=markup)


@bot.message_handler(content_types=['text'], state=MyStates.odours_0)
async def handle_odours_1(message):
    detail = get_detail(message.from_user.id)
    detail['odours']['checked'] = True
    if message.text == 'Slight':
        detail['odours']['intensity'] = {'code': 1, 'description': message.text}
    elif message.text == 'Medium':
        detail['odours']['intensity'] = {'code': 2, 'description': message.text}
    elif message.text == 'Strong':
        detail['odours']['intensity'] = {'code': 3, 'description': message.text}
    else:
        await bot.send_message(message.chat.id, "Please choose the intensity of the odours")
        return
    set_detail(message.from_user.id, detail)
    markup = types.ReplyKeyboardMarkup()
    markup.add('Fish', 'Mold', 'Hydrocarbon', 'Solvent', 'Sewer', 'Decaying material')
    await bot.set_state(message.from_user.id, MyStates.odours_1, message.chat.id)
    await bot.send_message(message.chat.id, "Please choose the origin of the odours.", reply_markup=markup)


@bot.message_handler(content_types=['text'], state=MyStates.odours_1)
async def handle_odours_2(message):
    detail = get_detail(message.from_user.id)
    if message.text == 'Fish':
        detail['odours']['origin'] = {'code': 1, 'description': message.text}
    elif message.text == 'Mold':
        detail['odours']['origin'] = {'code': 2, 'description': message.text}
    elif message.text == 'Hydrocarbon':
        detail['odours']['origin'] = {'code': 3, 'description': message.text}
    elif message.text == 'Solvent':
        detail['odours']['origin'] = {'code': 4, 'description': message.text}
    elif message.text == 'Sewer':
        detail['odours']['origin'] = {'code': 5, 'description': message.text}
    elif message.text == 'Decaying material':
        detail['odours']['origin'] = {'code': 6, 'description': message.text}
    else:
        await bot.send_message(message.chat.id, "Please choose the origin of the odours")
        return
    set_detail(message.from_user.id, detail)
    await bot.set_state(message.from_user.id, MyStates.location_finished, message.chat.id)
    await bot.send_message(message.chat.id,
                           "Odours information is finished! /details to describe more details, /submit to submit the information.",
                           reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['drains'], state=MyStates.location_finished)
async def handle_drains_0(message):
    markup = types.ReplyKeyboardMarkup()
    markup.add('Yes', 'No')
    await bot.set_state(message.from_user.id, MyStates.drains_0, message.chat.id)
    await bot.send_message(message.chat.id,
                           "You want to talk about drains! Is it active now?",
                           reply_markup=markup)


@bot.message_handler(content_types=['text'], state=MyStates.drains_0)
async def handle_drains_1(message):
    detail = get_detail(message.from_user.id)
    detail['outlets']['checked'] = True
    if message.text == 'Yes':
        detail['outlets']['inPlace'] = True
    elif message.text == 'No':
        detail['outlets']['inPlace'] = False
    else:
        await bot.send_message(message.chat.id, "Please describe if the drains are active now")
        return
    set_detail(message.from_user.id, detail)
    markup = types.ReplyKeyboardMarkup()
    markup.add('Visible', 'Submerged')
    await bot.set_state(message.from_user.id, MyStates.drains_1, message.chat.id)
    await bot.send_message(message.chat.id, "Please choose the terminal of the drains.", reply_markup=markup)


@bot.message_handler(content_types=['text'], state=MyStates.drains_1)
async def handle_drains_2(message):
    detail = get_detail(message.from_user.id)
    if message.text == 'Visible':
        detail['outlets']['terminal'] = {'code': 1, 'description': message.text}
    elif message.text == 'Submerged':
        detail['outlets']['terminal'] = {'code': 2, 'description': message.text}
    else:
        await bot.send_message(message.chat.id, "Please choose the terminal of the drains")
        return
    set_detail(message.from_user.id, detail)
    markup = types.ReplyKeyboardMarkup()
    markup.add('Red', 'Blu', 'Green', 'Grey', 'Brown', 'Yellow', 'White')
    await bot.set_state(message.from_user.id, MyStates.drains_2, message.chat.id)
    await bot.send_message(message.chat.id, "Please choose the color of the drains.", reply_markup=markup)


@bot.message_handler(content_types=['text'], state=MyStates.drains_2)
async def handle_drains_3(message):
    detail = get_detail(message.from_user.id)
    _list = ['Red', 'Blu', 'Green', 'Grey', 'Brown', 'Yellow', 'White']
    if message.text in _list:
        detail['outlets']['terminal'] = {'code': _list.index(message.text) + 1, 'description': message.text}
    else:
        await bot.send_message(message.chat.id, "Please choose the color of the drains")
        return
    set_detail(message.from_user.id, detail)
    markup = types.ReplyKeyboardMarkup()
    markup.add('Yes', 'No')
    await bot.set_state(message.from_user.id, MyStates.drains_3, message.chat.id)
    await bot.send_message(message.chat.id, "Are the drains vapour?", reply_markup=markup)


@bot.message_handler(content_types=['text'], state=MyStates.drains_3)
async def handle_drains_4(message):
    detail = get_detail(message.from_user.id)
    if message.text == 'Yes':
        detail['outlets']['vapour'] = True
    elif message.text == 'No':
        detail['outlets']['vapour'] = False
    else:
        await bot.send_message(message.chat.id, "Please describe if the drains are vapour")
        return
    set_detail(message.from_user.id, detail)
    markup = types.ReplyKeyboardMarkup()
    markup.add('Yes', 'No')
    await bot.set_state(message.from_user.id, MyStates.drains_4, message.chat.id)
    await bot.send_message(message.chat.id, "Is there any signage?", reply_markup=markup)


@bot.message_handler(content_types=['text'], state=MyStates.drains_4)
async def handle_drains_4(message):
    detail = get_detail(message.from_user.id)
    if message.text == 'Yes':
        detail['outlets']['signage'] = True
        await bot.set_state(message.from_user.id, MyStates.drains_5, message.chat.id)
        await bot.send_message(message.chat.id, "Please send a photo of the signage, if you don't have one, please "
                                                "send /drains_skip_photo", reply_markup=types.ReplyKeyboardRemove())
    elif message.text == 'No':
        detail['outlets']['signage'] = False
        await bot.set_state(message.from_user.id, MyStates.drains_6, message.chat.id)
        markup = types.ReplyKeyboardMarkup()
        markup.add('Yes', 'No')
        await bot.send_message(message.chat.id, "Is there any productive activity nearby?", reply_markup=markup)
    else:
        await bot.send_message(message.chat.id, "Please describe if there is any signage")
        return
    set_detail(message.from_user.id, detail)


@bot.message_handler(content_types=['photo'], state=MyStates.drains_5)
async def handle_drains_5(message):
    detail = get_detail(message.from_user.id)
    file_id = message.photo[-1].file_id
    detail['outlets']['signagePhoto'] = file_id
    set_detail(message.from_user.id, detail)
    markup = types.ReplyKeyboardMarkup()
    markup.add('Yes', 'No')
    await bot.send_message(message.chat.id, "Is there any productive activity nearby?", reply_markup=markup)
    await bot.set_state(message.from_user.id, MyStates.drains_6, message.chat.id)


@bot.message_handler(commands=['drains_skip_photo'], state=MyStates.drains_5)
async def handle_drains_6(message):
    detail = get_detail(message.from_user.id)
    detail['outlets']['signagePhoto'] = None
    set_detail(message.from_user.id, detail)
    markup = types.ReplyKeyboardMarkup()
    markup.add('Yes', 'No')
    await bot.send_message(message.chat.id, "Is there any productive activity nearby?", reply_markup=markup)
    await bot.set_state(message.from_user.id, MyStates.drains_6, message.chat.id)


@bot.message_handler(content_types=['text'], state=MyStates.drains_6)
async def handle_drains_7(message):
    detail = get_detail(message.from_user.id)
    if message.text == 'Yes':
        detail['outlets']['prodActNearby'] = True
        await bot.set_state(message.from_user.id, MyStates.drains_7, message.chat.id)
        await bot.send_message(message.chat.id, "Describe the productive activity nearby!",
                               reply_markup=types.ReplyKeyboardRemove())
    elif message.text == 'No':
        detail['outlets']['prodActNearby'] = False
        await bot.set_state(message.from_user.id, MyStates.location_finished, message.chat.id)
        await bot.send_message(message.chat.id,
                               "Drains information is finished! /details to describe more details, /submit to submit the information.",
                               reply_markup=types.ReplyKeyboardRemove())
    else:
        await bot.send_message(message.chat.id, "Please describe if there is any productive activity nearby")
        return
    set_detail(message.from_user.id, detail)


@bot.message_handler(content_types=['text'], state=MyStates.drains_7)
async def handle_drains_8(message):
    detail = get_detail(message.from_user.id)
    detail['outlets']['prodActNearbyDetails'] = message.text
    await bot.set_state(message.from_user.id, MyStates.location_finished, message.chat.id)
    await bot.send_message(message.chat.id,
                           "Drains information is finished! /details to describe more details,, /submit to submit the information.",
                           reply_markup=types.ReplyKeyboardRemove())
    set_detail(message.from_user.id, detail)
    print(get_detail(message.from_user.id))


# about fish
@bot.message_handler(commands=['fish'], state=MyStates.location_finished)
async def handle_fish_0(message):
    await bot.send_message(message.chat.id, "You want to talk about fish? How many fish are there in the area?",
                           reply_markup=types.ReplyKeyboardRemove())
    await bot.set_state(message.from_user.id, MyStates.fish_0, message.chat.id)


# handle fish_0 only accepting digit only
@bot.message_handler(content_types=['text'], state=MyStates.fish_0)
async def handle_fish_1(message):
    if message.text.isdigit():
        detail = get_detail(message.from_user.id)
        detail['fauna']['checked'] = True
        detail['fauna']['fish']['checked'] = True
        detail['fauna']['fish']['number'] = int(message.text)
        set_detail(message.from_user.id, detail)
        markup = types.ReplyKeyboardMarkup()
        markup.add('Yes', 'No')
        await bot.set_state(message.from_user.id, MyStates.fish_1, message.chat.id)
        await bot.send_message(message.chat.id, "Are they deceased?", reply_markup=markup)
    else:
        await bot.send_message(message.chat.id, "Please enter a valid number")
        return


@bot.message_handler(content_types=['text'], state=MyStates.fish_1)
async def handle_fish_2(message):
    detail = get_detail(message.from_user.id)
    if message.text == 'Yes':
        detail['fauna']['fish']['deceased'] = True
    elif message.text == 'No':
        detail['fauna']['fish']['deceased'] = False
    else:
        await bot.send_message(message.chat.id, "Please enter Yes or No")
        return
    set_detail(message.from_user.id, detail)
    await bot.set_state(message.from_user.id, MyStates.fish_2, message.chat.id)
    markup = types.ReplyKeyboardMarkup()
    markup.add('Yes', 'No')
    await bot.send_message(message.chat.id, "Is there any abnormal behaviours?", reply_markup=markup)


@bot.message_handler(content_types=['text'], state=MyStates.fish_2)
async def handle_fish_3(message):
    detail = get_detail(message.from_user.id)
    if message.text == 'Yes':
        detail['fauna']['fish']['abnormal']['checked'] = True
        await bot.set_state(message.from_user.id, MyStates.fish_3, message.chat.id)
        await bot.send_message(message.chat.id, "Describe the abnormal behaviour",
                               reply_markup=types.ReplyKeyboardRemove())
    elif message.text == 'No':
        detail['fauna']['fish']['abnormal']['checked'] = False
        await bot.set_state(message.from_user.id, MyStates.fish_4, message.chat.id)
        markup = types.ReplyKeyboardMarkup()
        markup.add('Yes', 'No')
        await bot.send_message(message.chat.id, "Is there any alien species like Stone moroko?", reply_markup=markup)
    else:
        await bot.send_message(message.chat.id, "Please enter Yes or No")
        return
    set_detail(message.from_user.id, detail)


@bot.message_handler(content_types=['text'], state=MyStates.fish_3)
async def handle_fish_4(message):
    detail = get_detail(message.from_user.id)
    detail['fauna']['fish']['abnormal']['details'] = message.text
    set_detail(message.from_user.id, detail)
    await bot.set_state(message.from_user.id, MyStates.fish_4, message.chat.id)
    markup = types.ReplyKeyboardMarkup()
    markup.add('Yes', 'No')
    await bot.send_message(message.chat.id, "Is there any alien species like Stone moroko?", reply_markup=markup)


@bot.message_handler(content_types=['text'], state=MyStates.fish_4)
async def handle_fish_5(message):
    detail = get_detail(message.from_user.id)
    if message.text == 'Yes':
        detail['fauna']['fish']['alien']['checked'] = True
        detail['fauna']['fish']['alien']['species'] = [{'code': 1, 'description': 'Stone moroko'}]
    elif message.text == 'No':
        detail['fauna']['fish']['alien']['checked'] = False
    else:
        await bot.send_message(message.chat.id, "Please enter Yes or No")
        return
    set_detail(message.from_user.id, detail)
    await bot.set_state(message.from_user.id, MyStates.location_finished, message.chat.id)
    await bot.send_message(message.chat.id,
                           "Fish information is finished! /details to describe more details, /submit to submit the information.",
                           reply_markup=types.ReplyKeyboardRemove())


# about /submit
@bot.message_handler(commands=['submit'], state=MyStates.location_finished)
async def handle_submit(message):
    info = get_detail(message.from_user.id)
    await bot.send_message(message.chat.id, "Your submission is successful!")
    #await bot.send_message(message.chat.id, info)

@bot.message_handler(commands=['help'])
async def handle_submit(message):
    await bot.send_message(message.chat.id, "At the first start of the chat, a short description of the Bot will appear, with a welcome message. To activate the chat the user is asked to use the button /start. On startup, a MENU will be available in which it will be possible to activate the data collection for a new report or to delete the current one.")


# @bot.message_handler(content_types=['text'], state=MyStates.algae_0)
# async def handle_algae_1(message):
#     schema = {'type': 'object',
#               'properties': {'checked': {'type': 'boolean', 'description': 'whether or not there is algae'},
#                              'iridescent': {'type': 'boolean', 'description': 'whether or not it is iridescent'},
#                              'extension': {'type': 'int',
#                                            'description': 'the extension of the algae\n1,less than 5 sqm\n2, 5 to 20 sqm\n3, greater than 20 sqm\n-1,not mentioned or not any of them'},
#                              'look': {'type': 'int',
#                                       'description': '1,Scattered\n2,Compact\n3,Grouped\n4,Surfaces stripes\n-1,not mentioned or not any of them'},
#                              'colour': {'type': 'int',
#                                         'description': 'the colour of the algae,1,Red\n2,Blue\n3,Green\n4,Grey\n5,Brown\n-1,not mentioned'}},
#               'required': ['checked', 'extension', 'look', 'colour'], 'additionalProperties': False,
#               '$schema': 'http://json-schema.org/draft-07/schema#'}
#     result = send_request(schema, description=message.text)
#     result_schema = {'colour': {'1': 'Red', '2': 'Blue', '3': 'Green', '4': 'Grey', '5': 'Brown'},
#                      'look': {'1': 'Scattered', '2': 'Compact', '3': 'Grouped', '4': 'Surfaces stripes'},
#                      'extension': {'1': 'less than 5 sqm', '2': '5 to 20 sqm', '3': 'greater than 20 sqm'},
#                      'iridescent': {'True': 'true', 'False': 'false'}}
#     result_str = 'You mean:\n'
#     msg_completed = True
#     if result[1] != -1:
#         for key in result_schema:
#             if result[0][key] == -1:
#                 msg_completed = False
#                 result_str += 'The {0} is not mentioned\n'.format(key)
#             else:
#                 result_str += 'The {0} is {1}\n'.format(key, result_schema[key][str(result[0][key])])
#     print(result)
#     await bot.send_message(message.chat.id, result_str)


@bot.message_handler(state="*", commands='cancel')
async def any_state(message):
    """
    Cancel state
    """
    await bot.send_message(message.chat.id, "Your state was cancelled.")
    await bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state="*", func=lambda m: True)
async def echo_all(message):
    print('wrong state')


async def start():
    await bot.set_my_commands(
        commands=[
            types.BotCommand('start', 'Start the bot'),
            types.BotCommand('continue', 'Continue on your previous work'),
            types.BotCommand('details', 'Provide the details of the lake after you provided the necessary information'),
            types.BotCommand('help', 'Provide guide of using this bot'),
        ]
    )
    await bot.polling(none_stop=True)


if __name__ == '__main__':
    # set proxy
    # asyncio_helper.proxy = 'http://127.0.0.1:10809'  # url
    # register filters
    bot.add_custom_filter(asyncio_filters.StateFilter(bot))
    import asyncio

    asyncio.run(start())
