import telebot
from telebot import types
import os
import codecs
import requests
from functools import wraps
from jinja2 import Template
from datetime import date
from geopy.geocoders import Nominatim
import pycountry
import logging


token = os.getenv('API_BOT_TOKEN')
bot = telebot.TeleBot(token)


commands = {'start': 'Start using chatbot',
            'statistics': 'COVID-19 statistics in the world for today',
             'country': 'COVID-19 statistics in specified country',
            'help': 'Some useful info about chatbot',
            'contacts': 'Developers contacts'}


user_steps = {}
known_users = []


def get_user_step(uid):
    if uid in user_steps:
        return user_steps[uid]
    else:
        known_users.append(uid)
        user_steps[uid] = 0
        return user_steps[uid]


def send_action(action):
    def decorator(func):
        @wraps(func)
        def command_func(message, *args, **kwargs):
            bot.send_chat_action(message.chat.id, action)
            return func(message, *args, **kwargs)
        return command_func
    return decorator


@bot.message_handler(commands=['start'])
@send_action('typing')
def start_command_handler(message):

    logging.info("/start command from user {0} ({1} {2})"
                 .format(message.chat.username,
                         message.chat.first_name, message.chat.last_name))

    cid = message.chat.id
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_geo = types.KeyboardButton(text='send location', request_location=True)
    markup.add(btn_geo)
    bot.send_message(cid, 'Hi, {0}! Please, choose command from the list'
                     .format(message.chat.username),
                     reply_markup=markup)
    help_command_handler(message)


@bot.message_handler(commands=['country'])
@send_action('typing')
def country_command_handler(message):

    logging.info("/country command from user {0} ({1} {2})"
                 .format(message.chat.username,
                         message.chat.first_name, message.chat.last_name))

    cid = message.chat.id

    send = bot.send_message(cid, 'Please, enter country name.'.format(message.chat.username))
    bot.register_next_step_handler(send, get_country_name)


def get_country_name(message):
    cid = message.chat.id
    country_name = message.text.strip()

    statistics = get_info_by_country_name(country_name)

    if statistics is None:
        with codecs.open('template/not_found.html', 'r', encoding='UTF-8') as file:
            template = Template(file.read())
        bot.send_message(cid, template.render(), parse_mode='HTML')
        return

    reply = get_statistics_reply(statistics)
    bot.send_message(cid, reply, parse_mode='HTML')


def get_info_by_location(latitude, longitude):
    geolocator = Nominatim(user_agent="telegram-bot")
    location = geolocator.reverse((latitude, longitude))
    country_code = location.raw['address']['country_code']
    country = pycountry.countries.get(alpha_2=country_code).name

    return get_info_by_country_name(country)


def get_info_by_country_name(country_name):
    response = get_covid_statistics()
    for elem in response['Countries']:
        if elem['Country'].lower() == country_name.lower():
            logging.info("Request for statistics in {0}".format(country_name))
            return elem
    return None


@bot.message_handler(content_types=['location'])
@send_action('typing')
def geo_command_handler(message):
    cid = message.chat.id
    country_info = get_info_by_location(message.location.latitude, message.location.longitude)
    country_name = country_info['Country']

    logging.info("User {0} ({1} {2}) sent location: {3}"
                 .format(message.chat.username,
                         message.chat.first_name, message.chat.last_name,
                         country_name))

    reply = get_statistics_reply(country_info)
    bot.send_message(cid, reply, parse_mode='HTML')


@bot.message_handler(commands=['statistics'])
@send_action('typing')
def geo_command_handler(message):

    logging.info("/statistics command from user {0} ({1} {2})"
                 .format(message.chat.username,
                         message.chat.first_name, message.chat.last_name))

    cid = message.chat.id

    response = get_covid_statistics();

    with codecs.open('template/statistics.html', 'r', encoding='UTF-8') as file:
        template = Template(file.read())
        reply = template.render(date=date.today(),
                                new_confirmed=response['Global']['NewConfirmed'],
                                total_confirmed=response['Global']['TotalConfirmed'],
                                new_deaths=response['Global']['NewDeaths'],
                                total_deaths=response['Global']['TotalDeaths'],
                                new_recovered=response['Global']['NewRecovered'],
                                total_recovered=response['Global']['TotalRecovered'])

    bot.send_message(cid, reply, parse_mode='HTML')


@bot.message_handler(func=lambda message: message.text.lower() == 'hi')
@send_action('typing')
def greeting_command_handler(message):
    cid = message.chat.id
    with codecs.open('template/greeting.html', 'r', encoding='UTF-8') as file:
        template = Template(file.read())
        bot.send_message(cid, template.render(user_name=message.chat.username))


@bot.message_handler(commands=['contacts'])
@send_action('typing')
def contacts_command_handler(message):

    logging.info("/contacts command from user {0} ({1} {2})"
                 .format(message.chat.username,
                         message.chat.first_name, message.chat.last_name))

    cid = message.chat.id
    with codecs.open('template/contacts.html', 'r', encoding='UTF-8') as file:
        template = Template(file.read())
        bot.send_message(cid, template.render(user_name=message.chat.username), parse_mode='HTML')


@bot.message_handler(commands=['help'])
@send_action('typing')
def help_command_handler(message):

    logging.info("/help command from user {0} ({1} {2})"
                 .format(message.chat.username,
                         message.chat.first_name, message.chat.last_name))

    cid = message.chat.id
    help_text = 'The following commands are available:\n'
    for command in commands:
        help_text += '/' + command + ': '
        help_text += commands[command] + '\n'

    help_text += "\nIf you are using a smartphone you can also send location to get statistics in your country.\n"
    bot.send_message(cid, help_text)


@bot.message_handler(content_types=['text'])
@send_action('typing')
def unknown_command_handler(message):

    logging.info("Message from user {0} ({1} {2}): {3}"
                 .format(message.chat.username,
                         message.chat.first_name, message.chat.last_name,
                         message.text))

    cid = message.chat.id
    with codecs.open('template/unknown_command.html', 'r', encoding='UTF-8') as file:
        template = Template(file.read())
        bot.send_message(cid, template.render(text_command=message.text), parse_mode='HTML')


def get_statistics_reply(statistics):
    with codecs.open('template/country_statistics.html', 'r', encoding='UTF-8') as file:
        template = Template(file.read())
        reply = template.render(date=date.today(),
                                country=statistics['Country'],
                                new_confirmed=statistics['NewConfirmed'],
                                total_confirmed=statistics['TotalConfirmed'],
                                new_deaths=statistics['NewDeaths'],
                                total_deaths=statistics['TotalDeaths'],
                                new_recovered=statistics['NewRecovered'],
                                total_recovered=statistics['TotalRecovered'])
    return reply


def get_covid_statistics():
    url = "https://api.covid19api.com/summary"
    response = requests.request("GET", url).json()
    return response


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    bot.polling(none_stop=True, interval=0)
