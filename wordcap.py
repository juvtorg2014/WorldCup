# Загрузка результатов конкурса World Cup Trading Championship
# и конкурса The Global Cup Trading Championship
import csv
import datetime
import os
import re
import sys
from subprocess import run, PIPE, STDOUT

import requests
from bs4 import BeautifulSoup

INSTALLED_PACKEGES = sys.modules
headers = {'User-Agent': 'Mozilla/5.0'}
NAME_WORLD = '2024 World Cup Championship of Futures Trading®'
NAME_1Q = '2024 1st Quarter Futures Day Trading Championship®'
NAME_GLOBAL = 'The Global Cup Trading Championship Futures™️ 2023-2024'
PAGE = "https://www.worldcupchampionships.com//world-cup-trading-championship-standings"

pack_requests = 'requests'
pack_BS4 = 'bs4'
pack_datetime = '_datetime'
pack2 = "pandas"


def run_cmd(cmd):
	""" Запуск командной строки для установки пакетов"""
	ps = run(cmd, stdout=PIPE, stderr=STDOUT, shell=True, text=True)
	print(ps.stdout)


def check_modules():
	required = [pack_datetime, pack_requests, pack_BS4]
	is_pack = []
	for pack in INSTALLED_PACKEGES:
		if pack in required:
			is_pack.append(pack)
	
	if len(required) != len(is_pack):
		missing = set(required).difference(set(is_pack))
		if len(missing) == 1:
			try:
				run_cmd(f'pip install --ignore-installed {" ".join([*missing])}')
			except Exception as e:
				print(f"Не удалось установить пакет {missing}", e)
		else:
			for item in missing:
				try:
					run_cmd(f'pip install --ignore-installed {" ".join([*item])}')
				except Exception as e:
					print(f"Не удалось установить пакет {item}", e)
					continue
	else:
		print("Все пакеты установлены!")


def parsing_page(start_page, dir):
	check_modules()
	get_page(get_html(start_page), dir)


def get_html(url):
	"""Проверка отвечает ли сервер и получение содержания"""
	resp = requests.get(url, headers=headers)
	if resp.status_code == 200:
		return resp.text
	else:
		print("Нет ответа от сервера {}".format(PAGE))
	return None


def get_1st_quarter(tag, mode) -> list:
	""" Получение таблицы призеров квартала"""
	if mode == 'fut':
		text = 'tablepress-2024-q1-futures'
	else:
		text = 'tablepress-2024-q1-forex'
	table = tag.find('table', id=text)
	table_f = table.find('tbody', class_='row-hover').find_all('tr')
	return table_f
	
	
def get_2024(tag, mode):
	if mode == 'fut':
		text = 'tablepress-2024-futures-wcc'
	else:
		text = 'tablepress-2024-forex-wcc'
	table = tag.find('tbody', class_='row-hover').find_all('tr')
	return table



def get_page(html, dir):
	"""Получение данных со страницы"""
	soup = BeautifulSoup(html, 'html.parser')
	futures_2024_q = soup.find('div', class_='elementor-element elementor-element-c243174 elementor-widget elementor-widget-text-editor')
	forex_2024_q = soup.find('div', class_='elementor-element elementor-element-ffa3959 elementor-widget elementor-widget-text-editor')
	
	futures_2024 = soup.find('table', id='tablepress-2024-futures-wcc')
	forex_2024 = soup.find('div', class_='has_eae_slider elementor-column elementor-col-33 elementor-inner-column elementor-element elementor-element-08db3c7')
	
	futures = soup.find('table', class_='tablepress tablepress-id-2023-futures-WCC tablepress-responsive')
	forex = soup.find('table', class_='tablepress tablepress-id-2023-forex-wcc tablepress-responsive')
	
	# Работа с данными World Cup
	fut_2024_world = get_2024(futures_2024, 'fut')
	for_2024_world = get_2024(forex_2024, 'for')
	data_fut_2024 = find_global(fut_2024_world)
	data_for_2024 = find_global(for_2024_world)
	
	# Работа с данными квартальными
	fut_1st_quarter = get_1st_quarter(futures_2024_q, 'fut')
	for_1st_quarter = get_1st_quarter(forex_2024_q, 'for')
	data_fut_1q = find_global(fut_1st_quarter)
	data_for_1q = find_global(for_1st_quarter)
 
	
	# Работа с данными  Global Cup
	for_g = soup.find('div', class_='has_eae_slider elementor-column elementor-col-33 '
									'elementor-inner-column elementor-element elementor-element-2ffa355')
	for_name = for_g.find('div', class_="elementor-widget-container").text.strip()
	for_table = for_g.find('table', class_="tablepress tablepress-id-global-cup-forex-23-24 tablepress-responsive")
	
	fut = soup.find('div', class_='has_eae_slider elementor-column elementor-col-33 '
								  'elementor-inner-column elementor-element elementor-element-e7c9cd4')
	fut_name = fut.find('div', class_="elementor-widget-container").text.strip()
	fut_table = fut.find('table', class_="tablepress tablepress-id-global-cup-futures-23-24 tablepress-responsive")
	
	date = soup.find('span', id='tablepress-global-cup-futures-23-24-description').text
	year_now = date.split(',')[2]
	date_date = date.split(',')[1].split(' ')
	
	today = date_date[3] + ' ' + date_date[4] + ' ' + year_now.strip()
	new_data = today.replace(today.partition(' ')[0], today[:3])
	date_n = datetime.datetime.strptime(new_data, '%b %d %Y')
	date_string = f'{date_n:%Y%m%d}'
	
	table_for = forex.find('tbody', class_='row-hover').find_all('tr')
	data_for = find_world(table_for)
	
	table_fut = futures.find('tbody', class_='row-hover').find_all('tr')
	data_fut = find_world(table_fut)
	
	for_table_global = for_table.find('tbody', class_='row-hover').find_all('tr')
	data_for_global = find_global(for_table_global)
	
	fut_table_global = fut_table.find('tbody', class_='row-hover').find_all('tr')
	data_fut_global = find_global(fut_table_global)
	
	write_futures(data_fut_2024, data_fut_1q, data_fut_global, date_string, dir)
	write_forex(data_for_2024, data_for_1q, data_for_global, date_string, dir)


def write_futures(data_fut, data_1q, data_gl, date, dir):
	""" Запись данных фьючерса в общий файл"""
	with open(dir + '\\' + 'Fut_' + date + '.csv', 'w', encoding='utf-8', newline='') as f:
		print("*********FUTURES_WORLD*********")
		f.writelines(NAME_WORLD + '\n')
		for item in data_fut:
			csv.writer(f, delimiter=';').writerow(item)
			print(item)
		f.writelines('\n')
		
		print("*********Quarter*********")
		f.writelines(NAME_1Q + '\n')
		for item in data_1q:
			csv.writer(f, delimiter=';').writerow(item)
			print(item)
		f.writelines('\n')
		
		print("*********FUTURES_GLOBAL**********")
		f.writelines(NAME_GLOBAL + '\n')
		for item in data_gl:
			csv.writer(f, delimiter=';').writerow(item)
			print(item)
		f.writelines('\n')


def write_forex(data_for, data_1q, data_global, date, dir):
	""" Запись данных форекса в общий файл"""
	with open(dir + '\\' + 'For_' + date + '.csv', 'w', encoding='utf-8', newline='') as f:
		print("**********FOREX_WORLD**********")
		f.writelines(NAME_WORLD + '\n')
		for item in data_for:
			csv.writer(f, delimiter=';').writerow(item)
			print(item)
		f.writelines('\n')
		
		print("*********Quarter**********")
		f.writelines(NAME_1Q + '\n')
		for item in data_1q:
			csv.writer(f, delimiter=';').writerow(item)
			print(item)
		
		print("*********FOREX_GLOBAL**********")
		f.writelines(NAME_GLOBAL + '\n')
		for item in data_global:
			csv.writer(f, delimiter=';').writerow(item)
			print(item)


def find_global(tags):
	"""Поиск даты и других данных"""
	data_global = []
	for tr in tags:
		tds = tr.find_all('td')
		place = int(tds[0].text)
		name = tds[1].text
		procent = float(re.sub(r'[^0-9,.]', '', tds[2].text))
		country = tr.find('td', class_="column-4").find('script').text.strip()
		country = re.sub(r'[^a-zA-Z]', '', country)
		data = [place, name, procent, country]
		data_global.append(data)
	return data_global


def find_world(tags):
	"""Поиск даты и других данных"""
	data_world = []
	for tr in tags:
		tds = tr.find_all('td')
		place = int(tds[0].text)
		name = tds[1].text
		procent = float(re.sub(r'[^0-9,.]', '', tds[2].text))
		country = tds[3].find('script').text.strip()
		country = re.sub(r'[^a-zA-Z]', '', country)
		data = [place, name, procent, country]
		data_world.append(data)
	return data_world


if __name__ == "__main__":
	dir = os.path.abspath(__file__)
	dir_name = '\\'.join(dir.split('\\')[:-1])
	parsing_page(PAGE, dir_name)
