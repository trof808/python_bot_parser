import urllib.request
from bs4 import BeautifulSoup
import csv

MAIN_URL = 'http://www.ratingruneta.ru/web/krasnodar/'

def save(studios, path):
    with open(path, 'w', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(('Название вебстудии', 'Выполнено проектов', 'Рейтинг', 'Год основания', 'Количество сотрудников', 'Веб сайт', 'Стоимость'))

        for item in studios:
            writer.writerow((item['name'], item['projects'], item['rate'], item['year'], item['stuff'], item['web_site'], item['price']))

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

def parseEachStudio(html):

    soup = BeautifulSoup(html, 'html.parser')
    dop_options = {}
    table = soup.find('table', class_='catalogueTab')
    options = table.find_all('td')[1].find_all('p')

    for option in options:
        if(option.find('i', class_='grey').get_text() == 'Год основания:'):
            dop_options.update({
                'year': option.find('span').get_text()
            })
        elif(option.find('i', class_='grey').get_text() == 'Количество сотрудников:'):
            dop_options.update({
                'stuff': option.find('span').get_text()
            })
        elif(option.find('i', class_='grey').get_text() == 'Сайт компании:'):
            dop_options.update({
                'web_site': option.a.get_text()
            })
        elif(option.find('i', class_='grey').get_text() == 'Стоимость услуг по разработке сайтов:'):
            dop_options.update({
                'price': option.a.get_text()
            })

    dop_options.setdefault('stuff', '-')
    dop_options.setdefault('web_site', '-')
    dop_options.setdefault('price', '-')

    return dop_options


def main():
    studios = parse(get_html(MAIN_URL))
    count_items = len(studios)
    links = [item['link'] for item in studios]

    for item in range(0, count_items):
        print('Идет Парсинг %d%%' % (item / count_items * 100))
        dop_options = parseEachStudio(get_html(links[item]))
        studios[item].update(dop_options)

    #print(studios)

    save(studios, 'studios_list.csv')


if __name__ == '__main__':
    main()