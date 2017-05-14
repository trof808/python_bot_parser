import requests
from bs4 import BeautifulSoup

MAIN_URL = 'https://www.avito.ru'

def get_html(url):
    response = requests.get(url)
    return response.text

def parse(html):

    arrItem = []

    soup = BeautifulSoup(html, 'html.parser')
    all_items = soup.find('div', class_='catalog-list')
    items = all_items.find_all('div', class_='item_table')

    for item in items:
        name = item.find('div', class_='description').find('h3', class_='item-description-title').a.get_text()

        price = item.find('div', class_='description').find('div', class_='about').contents[0]



        link = item.find('div', class_='description').find('h3', class_='item-description-title').a.get('href')
        link = 'https://www.avito.ru' + link
        arrItem.append({
            'title': name,
            'price': price,
            'link': link
        })

    return arrItem

def parseLocation(html):
    soup = BeautifulSoup(html, 'html.parser')

    arrCities = []
    objCities = {}

    tables = soup.find_all('div', class_='cities')
    for table in tables:
        cities = table.find_all('a')
        for city in cities:
            arrCities.append(city)

    for item in range(0, len(arrCities)):
        name = arrCities[item].get_text().strip('\n ')
        link = 'https:' + arrCities[item].get('href')
        objCities[name] = link

    return objCities


def main():
    print(parseLocation(get_html(MAIN_URL)))

if __name__ == '__main__':
    main()
