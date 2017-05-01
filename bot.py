import telebot
from telebot import types
import avito
import config

URL = 'https://www.avito.ru'

custom_request = {}

buttons = {
    'Квартиры': '/kvartiry',
    'Дома': '/doma_dachi_kottedzhi',
    'Комнаты': '/komnaty',
    'Коммерция': '/kommercheskaya_nedvizhimost',
    'Купить': '/prodam',
    'Снять': '/sdam'
}

options = {
    'start': 0,
    'end': 5
}

result = []

objCities = avito.parseLocation(avito.get_html(URL))


TOKEN = config.TOKEN

bot = telebot.TeleBot(TOKEN)


##Функция, которая обрабатывает команду /start
@bot.message_handler(commands=['start'])
def stepOne(message, info='Введите ваш город'):
    sent = bot.send_message(
        message.chat.id,
        info
    )

    bot.register_next_step_handler(sent, stepTwo)


def stepTwo(message):

    city = message.text

    cityStatus = objCities.get(city, 'Нет такого города')
    if(cityStatus == 'Нет такого города'):
        info = cityStatus + '\n' + 'Введите город заного'
        stepOne(message, info)
    else:
        custom_request['1'] = city

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in ['Квартиры', 'Дома', 'Комнаты', 'Коммерция']])
        sent = bot.send_message(message.chat.id, 'Выберите тип недвижимости', reply_markup=keyboard)

        ##После отправки сообщения, бот ждет сообщение в ответ, чтобы вызвать функцию stepTwo()
        bot.register_next_step_handler(sent, stepThree)



def stepThree(message):
    msg = message.text
    custom_request['2'] = msg

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in ['Купить', 'Снять', 'Показать объявления']])
    sent = bot.send_message(message.chat.id, 'Выберите услугу', reply_markup=keyboard)

    bot.register_next_step_handler(sent, stepFour)



def stepFour(message):
    if(message.text == 'Показать объявления'):
        showResults(message)

##Покзать результат
def showResults(message):
    custom_url = URL


    ##Информаци о запросе
    info_msg = 'По Вашему запросу: \n'
    for item in custom_request:
        info_msg = info_msg + item + ': ' + custom_request[item] + '\n'
        if (item == '1'):
            custom_url = objCities[custom_request[item]]
        else:
            custom_url = custom_url + buttons[custom_request[item]]

    info_msg = info_msg + 'Было найдено'

    print(custom_url)
    bot.send_message(
        message.chat.id,
        info_msg
    )

    ##Парсим первую страницу по  URL
    parse = avito.parse(avito.get_html(custom_url))

    for item in parse:
        result.append(item)


    part = result[:options['end']]
    options['start'] = options['end']
    options['end'] = options['end'] + 5


    #Парсим 2 и 3 страницы
    # for page in range(2, 4):
    #     result2 = avito.parse(avito.get_html(custom_url + '?p=' + str(page)))
    #     for item in result2:
    #         result.append(item)

    ##Выводим результаты запроса
    for item in part:
        bot.send_message(
            message.chat.id,
            '{price} \n {link}'.format(price=item['price'], link=item['link'])
        )

    afterShow(message)

    # bot.register_next_step_handler(sent, afterShow)



def afterShow(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in ['Показать еще', 'Создать новый запрос']])
    sent = bot.send_message(message.chat.id, 'Выберите следующее действие', reply_markup=keyboard)

    bot.register_next_step_handler(sent, chooseAction)

def chooseAction(message):
    if (message.text == 'Показать еще'):
        showMore(message)
    else:
        createNew(message)

def createNew(message):
    options['start'] = 0
    options['end'] = 5
    result.clear()
    stepOne(message)

def showMore(message):
    part = result[options['start']:options['end']]
    options['start'] = options['end']
    options['end'] = options['end'] + 5
    for item in part:
        bot.send_message(
            message.chat.id,
            '{price} \n {link}'.format(price=item['price'], link=item['link'])
        )

    afterShow(message)

if __name__ == '__main__':
    bot.polling()