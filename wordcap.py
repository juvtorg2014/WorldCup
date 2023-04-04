# Загрузка результатов конкурса World Cup Trading Championship

import requests
from bs4 import BeautifulSoup
import re
import datetime


headers = {'User-Agent': 'Mozilla/5.0'}
FUTURES = "2023 World Cup Championship of Futures Trading®"
FOREX = "2023 World Cup Championship of Forex Trading®"
PAGE = "https://www.worldcupchampionships.com//world-cup-trading-championship-standings"


def parsing_page(start_page):
    get_page(get_html(start_page))


def get_html(url):
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.text
    else:
        print("Нет ответа от сервера {}".format(PAGE))
        return None


def get_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    futures = soup.find('table', class_='tablepress tablepress-id-2023-futures-WCC tablepress-responsive')
    forex = soup.find('table', class_='tablepress tablepress-id-2023-forex-wcc tablepress-responsive')
    date = soup.find('span', id='tablepress-2023-futures-WCC-description').text
    date_date = date.split(',')[1].split(' ')
    today = date_date[3] + ' ' + date_date[4] + ' ' + date_date[1]
    new_data = today.replace(today.partition(' ')[0], today[:3])
    date_n = datetime.datetime.strptime(new_data, '%b %d %Y')
    date_string = f'{date_n:%Y%m%d}'

    table_fut = futures.find_all('tbody', class_='row-hover')
    table_for = forex.find_all('tbody', class_='row-hover')

    fut_list = []
    for_list = []
    for item in table_fut:
        fut_list.append(item.text.title().split('%'))
    for item in table_for:
        for_list.append(item.text.title().split('%'))

    final_fut = []
    final_for = []
    for play in fut_list:
        final_fut.append(re.sub(r'[^-a-zA-Z0-9. ]', '', play[0]))
        final_fut.append(re.sub(r'[^-a-zA-Z0-9. ]', '', play[1]))
        final_fut.append(re.sub(r'[^-a-zA-Z0-9. ]', '', play[2]))
        final_fut.append(re.sub(r'[^-a-zA-Z0-9. ]', '', play[3]))
        final_fut.append(re.sub(r'[^-a-zA-Z0-9. ]', '', play[4]))

    for pl in for_list:
        final_for.append(re.sub(r'[^-a-zA-Z0-9. ]', '', pl[0]))
        final_for.append(re.sub(r'[^-a-zA-Z0-9. ]', '', pl[1]))
        final_for.append(re.sub(r'[^-a-zA-Z0-9. ]', '', pl[2]))
        final_for.append(re.sub(r'[^-a-zA-Z0-9. ]', '', pl[3]))
        final_for.append(re.sub(r'[^-a-zA-Z0-9. ]', '', pl[4]))

    with open('Fut_' + date_string + '.txt', 'w', encoding='utf-8') as f:
        print("*********FUTURES*********")
        for item in final_fut:
            place = item[:1]
            player = re.sub(r'[^a-zA-Z ]', '', item[1:])
            number = re.sub(r'[^0-9.]', '', item[1:])
            f.writelines(place + ' ' + player + ' ' + number + "\n")
            print(place + ' ' + player + ' ' + number)
        print("*********FUTURES*********")
    with open('For_' + date_string + '.txt', 'w', encoding='utf-8') as f:
        print("**********FOREX**********")
        for item in final_for:
            place = item[:1]
            player = re.sub(r'[^a-zA-Z ]', '', item[1:])
            number = re.sub(r'[^0-9.]', '', item[1:])
            f.writelines(place + ' ' + player + ' ' + number + "\n")
            print(place + ' ' + player + ' ' + number)
        print("**********FOREX**********")


if __name__ == "__main__":
    parsing_page(PAGE)
