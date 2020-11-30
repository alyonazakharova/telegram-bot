import telebot
import os
import codecs
from functools import wraps
from telebot import types
from jinja2 import Template
from services.country_service import CountryService
from services.statistics_service import StatisticsService

import requests
from datetime import date


token = os.getenv('API_BOT_TOKEN')
bot = telebot.TeleBot(token)
user_steps = {}
known_users = []
country_service = CountryService()
stats_service = StatisticsService()


commands = {'start': 'Start using chatbot',
            'country': 'Please, enter county name',
            'statistics': 'Statistics by users queries',
            'help': 'Some useful info about chatbot',
            'contacts': 'Developer contacts'}


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
    cid = message.chat.id
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_geo = types.KeyboardButton(text='send location', request_location=True)
    markup.add(btn_geo)
    bot.send_message(cid, 'Hi, {0}! Please, choose command from the list:'
                     .format(message.chat.username),
                     reply_markup=markup)
    help_command_handler(message)


# @bot.message_handler(commands=['country'])
# @send_action('typing')
# def country_command_handler(message):
#     cid = message.chat.id
#     user_steps[cid] = 1
#     bot.send_message(cid, '{0}, enter country name, please'.format(message.chat.username))


# @bot.message_handler(content_types=['location'])
# @send_action('typing')
# def geo_command_handler(message):
#     cid = message.chat.id
#     geo_result = country_service.get_country_information(message.location.latitude, message.location.longitude)
#     statistics = stats_service.get_statistics_by_country_name(geo_result['countryName'], message.chat.username)
#     user_steps[cid] = 0
#     bot.send_message(cid, statistics, parse_mode='HTML')


@bot.message_handler(commands=['statistics'])
@send_action('typing')
def geo_command_handler(message):
    cid = message.chat.id

    url = "https://api.covid19api.com/summary"
    response = requests.request("GET", url).json()

    with codecs.open('template/statistics.html', 'r', encoding='UTF-8') as file:
        template = Template(file.read())
        reply = template.render(date=date.today(),
                                confirmed_new=response['Global']['NewConfirmed'],
                                confirmed_total=response['Global']['TotalConfirmed'],
                                deaths_new=response['Global']['NewDeaths'],
                                deaths_total=response['Global']['TotalDeaths'],
                                recovered_new=response['Global']['NewRecovered'],
                                recovered_total=response['Global']['TotalRecovered'])

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
    cid = message.chat.id
    with codecs.open('template/contacts.html', 'r', encoding='UTF-8') as file:
        template = Template(file.read())
        bot.send_message(cid, template.render(user_name=message.chat.username), parse_mode='HTML')


@bot.message_handler(commands=['help'])
@send_action('typing')
def help_command_handler(message):
    cid = message.chat.id
    help_text = 'The following commands are available\n'
    for command in commands:
        help_text += '/' + command + ': '
        help_text += commands[command] + '\n'
    bot.send_message(cid, help_text)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)