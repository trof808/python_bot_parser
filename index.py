import urllib.request
from bs4 import BeautifulSoup

MAIN_URL = 'http://www.ratingruneta.ru/web/krasnodar/'

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
    print(parse(get_html(MAIN_URL)))

if __name__ == '__main__':
    main()