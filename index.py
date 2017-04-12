import urllib.request
from bs4 import BeautifulSoup
import csv

MAIN_URL = 'http://www.ratingruneta.ru/web/krasnodar/'

def save(studios, path):
    with open(path, 'w', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(('Название вебстудии', 'Выполнено проектов', 'Рейтинг'))

        for item in studios:
            writer.writerow((item['name'], item['projects'], item['rate']))

def get_html(url):
    response = urllib.request.urlopen(url)
    return response.read()


def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', class_='for_tender')
    items = table.find_all('tr', class_='row-with-childs')[1:-1]
    web_studios = []
    for item in items:
        name = item.find_all('td')[1].find('span').a.get_text()
        projects = item.find_all('td')[2].a.get_text()
        rate = item.find_all('td')[3].a.get_text()
        item_link = item.find_all('td')[1].find('span').a.get('href')
        web_studios.append({
            'name': name,
            'projects': projects,
            'rate': rate,
            'link': item_link
        })
    return web_studios

def main():
    studios = parse(get_html(MAIN_URL))
    count_items = len(studios)
    #for page in range(0, count_items-1):
        #print('Выполняется парсинг %d%%' % (page / count_items * 100))
        #print((parse(get_html(MAIN_URL)))[page]['link'])

    #print((parse(get_html(MAIN_URL)))[0]['link'])

    save(studios, 'studios_list.csv')


if __name__ == '__main__':
    main()