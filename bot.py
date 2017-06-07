import telebot
from telebot import types
import avito
import config
import bd
import re

db = bd.db

URL = ''
custom_url = []
custom_request = {}

buttons = {
    'Квартиры': '/kvartiry',
    'Дома': '/doma_dachi_kottedzhi',
    'Комнаты': '/komnaty',
    'Коммерция': '/kommercheskaya_nedvizhimost',
    'Купить': '/prodam',
    'Снять': '/sdam'
}

krasnodarAreas = {
    'Западный': '?district=359',
    'Карасунский': 'district=360',
    'Прикубанский': '?district=361',
    'Старокорсунский': '?district=547',
    'Центральный': '?district=362'
}

options = {
    'start': 0,
    'end': 5
}

result = []


TOKEN = config.TOKEN

bot = telebot.TeleBot(TOKEN)


##Функция, которая обрабатывает команду /start
@bot.message_handler(commands=['start'])
def stepOne(message, info='Введите ваш город'):
    deleteReq = db.prepare("DELETE FROM task_table WHERE user_id = $1 AND active = false")
    deleteReq(message.chat.id)
    options['start'] = 0
    options['end'] = 5
    result.clear()
    custom_url.clear()
    custom_request.clear()

    sent = bot.send_message(
        message.chat.id,
        info
    )

    bot.register_next_step_handler(sent, stepTwo)


def stepTwo(message):
    arrCities = bd.getCitiesFromDb()

    city = message.text

    #Проверяет есть ли в массиве arrCities введенный город, если его нет, то перезаписываем переменную city
    try:
        arrCities.index(city)
    except:
        city = 'Нет такого города'

    if(city == 'Нет такого города'):
        info = city + '\n' + 'Введите город заного'
        stepOne(message, info)
    else:
        ins = db.prepare("INSERT INTO task_table (user_id) VALUES ($1)")

        ins(message.chat.id)

        cityLink = db.prepare('SELECT link FROM city WHERE name = $1')
        getCityLink = cityLink(city)
        custom_url.append(getCityLink[0][0])

        custom_request['city'] = city

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in ['Квартиры', 'Дома', 'Комнаты', 'Коммерция']])
        sent = bot.send_message(message.chat.id, 'Выберите тип недвижимости', reply_markup=keyboard)

        ##После отправки сообщения, бот ждет сообщение в ответ, чтобы вызвать функцию stepTwo()
        bot.register_next_step_handler(sent, stepThree)



def stepThree(message):
    msg = message.text

    custom_request['realtyType'] = msg

    realtyLink = db.prepare('SELECT link FROM realty WHERE name = $1')
    getRealtyLink = realtyLink(msg)
    custom_url.append(getRealtyLink[0][0])


    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in ['Купить', 'Снять', 'Показать объявления']])
    sent = bot.send_message(message.chat.id, 'Выберите услугу', reply_markup=keyboard)

    bot.register_next_step_handler(sent, actionStep)

def actionStep(message):
    msg = message.text
    if(msg == 'Показать объявления'):
        showResults(message)
    else:
        custom_request['service'] = msg
        actionLink = db.prepare('SELECT link FROM action WHERE name = $1')
        getActionLink = actionLink(msg)
        custom_url.append(getActionLink[0][0])
        # print(''.join(custom_url))

        if(custom_request.get('realtyType') == 'Дома'):
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(*[types.KeyboardButton(name) for name in ['Показать объявления']])
            sent = bot.send_message(message.chat.id, 'Для этого типа недвижимости пока больше нет параметров для выбора, но мы над этим работаем. А пока вы можете посмотреть объйвления по заданному запросу', reply_markup=keyboard)

            bot.register_next_step_handler(sent, houseChoose)
        else:
            if(msg == 'Купить'):
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.add(*[types.KeyboardButton(name) for name in ['Указать количество комнат', 'Показать объявления']])
                sent = bot.send_message(message.chat.id, 'Выберите услугу', reply_markup=keyboard)

                bot.register_next_step_handler(sent, countRooms)
            if(msg == 'Снять'):
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.add(*[types.KeyboardButton(name) for name in ['На длительный срок', 'Посуточно', 'Показать объявления']])
                sent = bot.send_message(message.chat.id, 'Выберите срок на который хотите снять или можете посмотреть объявления по собранному запросу', reply_markup=keyboard)

                bot.register_next_step_handler(sent, termRent)

def houseChoose(message):
    msg = message.text
    if(msg == 'Показать объявления'):
        showResults(message)

def termRent(message):
    msg = message.text
    if(msg == 'Показать объявления'):
        showResults(message)
    else:
        if(msg == 'На длительный срок'):
            termUrl = '/na_dlitelnyy_srok'
        elif(msg == 'Посуточно'):
            termUrl = '/posutochno'

    custom_request['term'] = 'Длительность ' + msg
    custom_url.append(termUrl)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in ['Студии']])
    sent = bot.send_message(message.chat.id, 'Укажите количество комнат цифрой от 1 до 9 или выберите студии из предложенного варианта', reply_markup=keyboard)

    bot.register_next_step_handler(sent, countRoomsNext)


def countRooms(message):
    msg = message.text
    if(msg == 'Показать объявления'):
        showResults(message)
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in ['Студии']])
        sent = bot.send_message(message.chat.id, 'Укажите количество комнат цифрой от 1 до 9 или выберите студии из предложенного варианта', reply_markup=keyboard)

        bot.register_next_step_handler(sent, countRoomsNext)

def countRoomsNext(message):
    msg = message.text
    if(msg == 'Студии'):
        roomUrl = '/studii'
    else:
        roomUrl = '/'+msg+'-komnatnye'
        msg = 'Количество комнат ' + msg

    custom_request['rooms'] = msg
    custom_url.append(roomUrl)

    if(custom_request.get('service') == 'Купить'):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in ['Вторичка', 'Новостройка', 'Показать объявления']])
        sent = bot.send_message(message.chat.id, 'Выберите вид объекта или можете посмотреть объявления по собранному запросу', reply_markup=keyboard)

        bot.register_next_step_handler(sent, vidObjOrShow)
    elif(custom_request.get('service') == 'Снять'):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in ['Западный', 'Карасунский', 'Прикубанский', 'Центральный', 'Старокорсунский', 'Показать объявления']])
        sent = bot.send_message(message.chat.id, 'Выберите нужный район или можете посмотреть объявления', reply_markup=keyboard)

        bot.register_next_step_handler(sent, areaChooseShow)

def vidObjOrShow(message):
    msg = message.text
    if(msg == 'Показать объявления'):
        showResults(message)
    else:
        if(msg == 'Вторичка'):
            objUrl = '/vtorichka'
        elif(msg == 'Новостройка'):
            objUrl = '/novostroyka'

        custom_request['typeBuild'] = 'Вид объекта ' + msg
        custom_url.append(objUrl)
        print(''.join(custom_url))
        if(custom_request['city'] == 'Краснодар'):
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(*[types.KeyboardButton(name) for name in ['Западный', 'Карасунский', 'Прикубанский', 'Центральный', 'Старокорсунский', 'Показать объявления']])
            sent = bot.send_message(message.chat.id, 'Выберите нужный район или можете посмотреть объявления', reply_markup=keyboard)

            bot.register_next_step_handler(sent, areaChooseShow)
        else:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(*[types.KeyboardButton(name) for name in ['Показать объявления']])
            sent = bot.send_message(message.chat.id, 'Районов вашего города пока нет в базе, но мы работаем над этим. Введите числом приблизительное количество квадратных метров или можете посмотреть объявления', reply_markup=keyboard)

            bot.register_next_step_handler(sent, amountMetres)

def areaChooseShow(message):
    msg = message.text
    if(msg == 'Показать объявления'):
        showResults(message)
    else:
        areaUrl = krasnodarAreas[msg]
        custom_request['area'] = 'Район ' + msg
        custom_url.append(areaUrl)
        print(''.join(custom_url))

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in ['Показать объявления']])
        sent = bot.send_message(message.chat.id, 'Введите числом приблизительное количество квадратных метров или можете посмотреть объявления', reply_markup=keyboard)

        bot.register_next_step_handler(sent, amountMetres)

def amountMetres(message):
    msg = message.text
    if(msg == 'Показать объявления'):
        showResults(message)
    else:
        custom_request['metres'] = msg

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in ['Показать объявления', 'Посмотреть запрос', 'Создать новый запрос']])
        sent = bot.send_message(message.chat.id, 'Вы ввели все возможные параметры. Теперь вы можете мосмотреть объявления по вашему запросу, посмотреть запрос, который вы ввели или создать новый запрос. Выберите нужное действие ниже', reply_markup=keyboard)

        bot.register_next_step_handler(sent, allOver)

def allOver(message):
    msg = message.text
    if(msg == 'Показать объявления'):
        showResults(message)
    elif(msg == 'Посмотреть запрос'):
        showRequest(message)
    elif(msg == 'Создать новый запрос'):
        stepOne(message)

def showRequest(message):
    info_msg = 'Вы ввели следующие параметры: \n'
    for item in custom_request:
        info_msg = info_msg + '- ' + custom_request[item] + '\n'

    info_msg = info_msg + 'Если вы где-то ошиблись или введенные параметры вас не устраивают, вы можете создать новый запрос или, если все устраиает, то можете посмотреть объявления по вашему запросу'
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in ['Показать объявления', 'Посмотреть запрос', 'Создать новый запрос']])
    sent = bot.send_message(message.chat.id, info_msg, reply_markup=keyboard)

    bot.register_next_step_handler(sent, allOver)


##Покзать результат
def showResults(message):
    ##Информаци о запросе
    info_msg = 'По Вашему запросу: \n'
    for item in custom_request:
        info_msg = info_msg + '- ' + custom_request[item] + '\n'

    info_msg = info_msg + 'Было найдено'

    URL = ''.join(custom_url)

    insertUrl = db.prepare("UPDATE task_table SET link = $1 WHERE user_id = $2 AND active = false")
    insertUrl(URL, message.chat.id)

    bot.send_message(
        message.chat.id,
        info_msg
    )

    ##Парсим первую страницу по  URL
    parse = avito.parse(avito.get_html(URL))

    metres = custom_request.get('metres', None)

    if(metres != None):
        meters = int(custom_request['metres'])
        # search_str = '[%s - %s]' % (str(meters-10), str(meters+10))
        search_str = r'[0-9]{1,2} м'
        # regx = re.compile(search_str)

        for item in parse:
            print(item['title'])
            if re.search(search_str, item['title']) is not None:
                rightStr = re.findall(search_str, item['title'])[0]
                numInTitle = int(rightStr.split(' ')[0])
                if(numInTitle <= meters+10 and numInTitle >= meters-10):
                    print(True)
                    result.append(item)
    else:
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

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in ['Да', 'Нет']])
    sent = bot.send_message(message.chat.id, 'Вы нашли, что хотели?', reply_markup=keyboard)

    bot.register_next_step_handler(sent, findRight)

def findRight(message):
    msg = message.text

    if(msg == 'Да'):
        deleteReq = db.prepare("DELETE FROM task_table WHERE user_id = $1 AND active = false")
        deleteReq(message.chat.id)
        stepOne(message)
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in ['Да', 'Нет']])
        sent = bot.send_message(message.chat.id, 'Хотите ли вы получать уведомления по вашему последнему запросу?', reply_markup=keyboard)

        bot.register_next_step_handler(sent, pushActive)

def pushActive(message):
    msg = message.text
    if(msg == 'Нет'):
        deleteReq = db.prepare("DELETE FROM task_table WHERE user_id = $1 AND active = false")
        deleteReq(message.chat.id)
        stepOne(message)
    else:
        deleteReq = db.prepare("DELETE FROM task_table WHERE user_id = $1 AND active = true")
        deleteReq(message.chat.id)
        setActive = db.prepare("UPDATE task_table SET active = true WHERE user_id = $1 AND active = false")
        setActive(message.chat.id)
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

def getZn():
    links = db.prepare("SELECT link FROM task_table WHERE active = true")
    arrlink = []
    for link in links:
        for item in link:
            arrlink.append(item)
    return arrlink

def main():
    links = getZn()
    for item in links:
        print(item)

if __name__ == '__main__':
    bot.polling(none_stop=True)
