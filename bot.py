import telebot
from telebot import types
import index
import json

URL = 'https://www.avito.ru/krasnodar'

buttons = {
    'Квартиры': '/kvartiry',
    'Дома': '/doma_dachi_kottedzhi'
}

TOKEN = '303092094:AAFdpjNi3EO-Utc5A598Mo5kcd4CwlWH9cc'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in ['Квартиры', 'Дома']])
    sent = bot.send_message(message.chat.id, 'Выберите тип недвижимости', reply_markup=keyboard)

    bot.register_next_step_handler(sent, hello)

def hello(message):
    msg = message.text
    url = URL + buttons[msg]
    result = index.parse(index.get_html(url))[:10]

    for item in result:
        bot.send_message(
            message.chat.id,
            '{price} {link}'.format(price=item['price'], link=item['link'])
        )


bot.polling()