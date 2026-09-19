import json
import time
from json import JSONDecoder
import threading
from datetime import datetime

import telebot
import os
import requests
from dotenv import load_dotenv

from telebot import types

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

users = []
thread = None

BotToken = os.getenv("TOKEN")
bot = telebot.TeleBot(BotToken)

EIGHT_DAYS_ECONOM='{"departure":6,"destination":[106],"date":{"from":"10.10.2026","till":"10.10.2026"},"nights":{"from":8,"till":8,"min":1,"max":28},"adults":2,"children":[],"touroperators":[],"stars":[1,2,3,4,5],"hotels":[8357,3087,49610],"resorts":[],"subResorts":[],"mealType":0,"hotelStatus":false,"firstCoastline":false,"minCost":0,"maxCost":99999999,"cid":1,"sourceCurrency":"RUB","offerCurrency":"RUB","source":"search_online_page","debug":0,"page":1}'
TEN_DAYS_LUX='{"departure":6,"destination":[106],"date":{"from":"10.10.2026","till":"10.10.2026"},"nights":{"from":10,"till":10,"min":1,"max":28},"adults":2,"children":[],"touroperators":[],"stars":[1,2,3,4,5],"hotels":[3092,49610],"resorts":[],"subResorts":[],"mealType":0,"hotelStatus":false,"firstCoastline":false,"minCost":0,"maxCost":99999999,"cid":1,"sourceCurrency":"RUB","offerCurrency":"RUB","source":"search_online_page","debug":0,"page":1}'

@bot.message_handler(commands=['start'])
def welcome(message):
    global users

    if message.chat.id not in users:
        users.append(message.chat.id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Узнать текущую стоимость")

    markup.add(item1)

    init_thread_loop()
    bot.send_message(message.chat.id, f"Вы подписаны на уведомления об изменении стоимости туров в Китай, Хайнань. \n\nВ отели \n\nMINGSHEN GOLF \n\nMARINA SPA \n\nWYNDHAM".format(message.from_user, bot.get_me()), parse_mode = 'html',  reply_markup=markup)



@bot.message_handler(content_types=['text'])
def lalala(message):
    if message.text == "Узнать текущую стоимость":
        bot.send_message(message.chat.id, 'Загружаем...'.format(message.from_user, bot.get_me()), parse_mode = 'html')

        text = gen_msg()

        bot.send_message(message.chat.id, text.format(message.from_user, bot.get_me()), parse_mode = 'html')



def check_price(body, days):
    response = requests.post('https://search.bankturov.ru/api/v3/search', data=body)
    response = json.loads(response.text)
    hotels = []
    names = []
    list = response['data']['rows'][:100]
    for obj in list:
        key = f"{obj['residenses']['hotel_name']}_{obj['date']}"
        if key not in names:
            names.append(key)
            hotels.append(obj)

    prices = []
    for obj in hotels:
        val = f"ВЫЛЕТ - {obj['date']} / {days} дней: {obj['residenses']['hotel_name']} - {obj['costValues']['RUB']['rounded']}руб."
        # val = { "name": obj['residenses']['hotel_name'], "price": obj['costValues']['RUB']['rounded'] }
        prices.append(val)

    return prices


def gen_msg():
    pricesEight = check_price(EIGHT_DAYS_ECONOM, 8)
    pricesTen = check_price(TEN_DAYS_LUX, 10)
    prices = pricesEight + pricesTen
    text = ''

    for line in prices:
        text = text + line + '\n\n'

    now = datetime.now()
    formatted_datetime = now.strftime("%Y-%m-%d %H:%M")

    return f"❗Обновление от {formatted_datetime} ❗ \n\n {text}."

def timer_loop(interval):
    while True:
        text = gen_msg()

        for usr_id in users:
            bot.send_message(usr_id, text, parse_mode='html')

        time.sleep(interval)

def init_thread_loop():
    global thread
    interval = 14400  # Интервал в секундах
    if thread is not None:
        return
    thread = threading.Thread(target=timer_loop, args=(interval,))
    thread.daemon = True  # Поток завершится, если основная программа завершится
    thread.start()

# RUN

def _main_():
    while True:
        try:
            bot.infinity_polling()
        except:
            continue