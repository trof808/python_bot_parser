import postgresql
import avito
import telebot
from telebot import types

URL = 'https://www.avito.ru'

objCities = avito.parseLocation(avito.get_html(URL))

db = postgresql.open('pq://postgres:585465077m@localhost:5432/postgres')

def getCitiesFromDb():
    cities = db.query('SELECT name FROM city')
    arrCities = []

    for city in cities:
        for item in city:
            arrCities.append(item)

    return arrCities

def getZn():
    links = db.prepare("SELECT user_id, link FROM task_table WHERE active = true")
    arrlink = []
    for link in links:
        items = avito.parse(avito.get_html(link[1]))[:8]
        for item in items:
            bot.send_message(
                link[0],
                '{price} \n {link}'.format(price=item['price'], link=item['link'])
            )

def main():
    getZn()

if __name__ == '__main__':
    main()