import telebot

TOKEN = '303092094:AAFdpjNi3EO-Utc5A598Mo5kcd4CwlWH9cc'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    sent = bot.send_message(message.chat.id, 'Привет')
    bot.register_next_step_handler(sent, hello)

def hello(message):
    bot.send_message(
        message.chat.id,
        'Пока, {name}'.format(name=message.text)
    )

bot.polling()