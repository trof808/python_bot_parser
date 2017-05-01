import telebot
from telebot import types
import avito
import config

URL = 'https://www.avito.ru/krasnodar'

custom_request = {}

buttons = {
    'Квартиры': '/kvartiry',
    'Дома': '/doma_dachi_kottedzhi',
    'Комнаты': '/komnaty',
    'Коммерция': '/kommercheskaya_nedvizhimost',
    'Купить': '/prodam',
    'Снять': '/sdam'
}

TOKEN = config.TOKEN

bot = telebot.TeleBot(TOKEN)


##Функция, которая обрабатывает команду /start
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in ['Квартиры', 'Дома', 'Комнаты', 'Коммерция']])
    sent = bot.send_message(message.chat.id, 'Выберите тип недвижимости', reply_markup=keyboard)

    ##После отправки сообщения, бот ждет сообщение в ответ, чтобы вызвать функцию stepTwo()
    bot.register_next_step_handler(sent, stepTwo)


##Обработка любых пользовательских сообщений
# @bot.message_handler(content_types=["text"])
# def handle_message(message):
#     bot.send_message(
#         message.chat.id,
#         'Для того, чтобы составить запрос на поиск нужной недвижимости введите команду /start'
#     )



def stepTwo(message):
    msg = message.text
    custom_request['1'] = msg

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in ['Купить', 'Снять', 'Показать объявления']])
    sent = bot.send_message(message.chat.id, 'Что вы хотите?', reply_markup=keyboard)

    bot.register_next_step_handler(sent, stepThree)



def stepThree(message):
    if(message.text == 'Показать объявления'):
        showResults(message)

##Покзать результат
def showResults(message):

    ##Информаци о запросе
    info_msg = 'По Вашему запросу: \n'
    for item in custom_request:
        info_msg = info_msg + item + ': ' + custom_request[item] + '\n'
        custom_url = URL + buttons[custom_request[item]]

    info_msg = info_msg + 'Было найдено'


    bot.send_message(
        message.chat.id,
        info_msg
    )

    ##Парсим первую страницу по  URL
    result = avito.parse(avito.get_html(custom_url))

    #Парсим 2 и 3 страницы
    # for page in range(2, 4):
    #     result2 = avito.parse(avito.get_html(custom_url + '?p=' + str(page)))
    #     for item in result2:
    #         result.append(item)

    ##Выводим результаты запроса
    for item in result:
        bot.send_message(
            message.chat.id,
            '{price} \n {link}'.format(price=item['price'], link=item['link'])
        )

if __name__ == '__main__':
    bot.polling()