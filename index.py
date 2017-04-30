import requests
# import urllib.request
from bs4 import BeautifulSoup
import csv

MAIN_URL = 'https://www.avito.ru/krasnodar/nedvizhimost'

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



        link = name = item.find('div', class_='description').find('h3', class_='item-description-title').a.get('href')
        link = 'https://www.avito.ru' + link
        arrItem.append({
            'title': name,
            'price': price,
            'link': link
        })

    return arrItem

def main():
    print(parse(get_html(MAIN_URL)))

if __name__ == '__main__':
    main()