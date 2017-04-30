import telebot
import index
import json

TOKEN = '303092094:AAFdpjNi3EO-Utc5A598Mo5kcd4CwlWH9cc'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    sent = bot.send_message(message.chat.id, 'Пришлите url')
    bot.register_next_step_handler(sent, hello)

def hello(message):
    result = index.parse(index.get_html(message.text))[:5]

    for item in result:
        bot.send_message(
            message.chat.id,
            '{price} {link}'.format(price=item['price'], link=item['link'])
        )


bot.polling()