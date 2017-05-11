import postgresql
import avito

URL = 'https://www.avito.ru'

objCities = avito.parseLocation(avito.get_html(URL))

db = postgresql.open('pq://postgres:585465077m@localhost:5432/postgres')

# def addCity(name, link):
#     ins = db.prepare("INSERT INTO city (name, link) VALUES ($1, $2)")
#     ins(name, link)

# for city in objCities:
#     addCity(city, objCities[city])

def getCitiesFromDb():
    cities = db.query('SELECT name FROM city')
    arrCities = []

    for city in cities:
        for item in city:
            arrCities.append(item)

    return arrCities
