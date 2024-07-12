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
quarters = {1: [1, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9], 4: [10, 11, 12]}

NAME_WORLD = '2024 World Cup Championship of Futures Trading®'
NAME_GLOBAL = 'The Global Cup Trading Championships™️ 2024-2025'
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


def parsing_page(start_page, dir_dir):
	check_modules()
	get_page(get_html(start_page), dir_dir)


def get_html(url):
	"""Проверка отвечает ли сервер и получение содержания"""
	resp = requests.get(url, headers=headers)
	if resp.status_code == 200:
		return resp.text
	else:
		print("Нет ответа от сервера {}".format(PAGE))
	return None


def get_number_quarter(today) -> int:
	"""Получение номера квартала"""
	month = today.month
	for key, value in quarters.items():
		if month in value:
			return key
	return 2


def get_st_quarter(tag, mode, number) -> list:
	""" Получение таблицы призеров квартала"""
	table_f = " "
	if 0 < number < 5:
		if mode == 'fut':
			text = f'tablepress-2024-q{number}-futures'
		else:
			text = f'tablepress-2024-q{number}-forex'
		table = tag.find('table', id=text)
		if table is not None:
			table_f = table.find('tbody', class_='row-hover').find_all('tr')
		else:
			print('Проверьте номер квартала')
	return table_f


def get_2024(tag, mode):
	# if mode == 'fut':
	# 	text = 'tablepress-2024-futures-wcc'
	# else:
	# 	text = 'tablepress-2024-forex-wcc'
	table = tag.find('tbody', class_='row-hover').find_all('tr')
	return table


def get_page(html, dir_name):
	"""Получение данных со страницы"""
	soup = BeautifulSoup(html, 'html.parser')
	today = []
	global_list = []
	# Работа с датами
	date = soup.find('span', id='tablepress-2024-futures-wcc-description').text
	year_now = date.split(',')[2].strip()
	date_now = date.split(',')[1].split(' ')[-1]
	month_now = date.split(',')[1].split(' ')[-2]
	# for item in date_date:
	# 	if len(item) > 1:
	# 		today.append(item)
	#new_data = today[1] + ' ' + today[2] + ' ' + today[0]
	new_date = month_now + ' ' + date_now + ' ' + year_now
	date_n = datetime.datetime.strptime(new_date, '%B %d %Y')
	date_string = f'{date_n:%Y%m%d}'
	
	num_q = get_number_quarter(date_n)
	name_qr = f'2024 {num_q}-st Quarter Futures Day Trading Championship®'
	futures_2024_q = soup.find('div',
		class_='elementor-element elementor-element-c243174 elementor-widget elementor-widget-text-editor')
	forex_2024_q = soup.find('div',
		class_='elementor-element elementor-element-ffa3959 elementor-widget elementor-widget-text-editor')
	
	futures_2024 = soup.find('table', id='tablepress-2024-futures-wcc')
	forex_2024 = soup.find('div',
		class_='has_eae_slider elementor-column elementor-col-33 elementor-inner-column elementor-element elementor-element-08db3c7')
	
	# Работа с данными World Cup
	fut_2024_world = get_2024(futures_2024, 'fut')
	for_2024_world = get_2024(forex_2024, 'for')
	data_fut_2024 = find_global(fut_2024_world)
	data_for_2024 = find_global(for_2024_world)
	
	# Работа с данными квартальными
	fut_st_quarter = get_st_quarter(futures_2024_q, 'fut', num_q)
	for_st_quarter = get_st_quarter(forex_2024_q, 'for', num_q)
	if fut_st_quarter == " ":
		data_fut_q = fut_st_quarter
	else:
		data_fut_q = find_global(fut_st_quarter)
	if for_st_quarter == " ":
		data_for_q = for_st_quarter
	else:
		data_for_q = find_global(for_st_quarter)
	
	# Работа с данными  Global Cup
	gl_date = soup.find('span', id ='tablepress-global-cup-futures-forex-24-25-description').text
	for_table = soup.find('div', class_='elementor-element elementor-element-df368fe elementor-widget elementor-widget-text-editor')
	global_list = for_table.find('tbody').find_all('tr')
	data_global = get_global_data(global_list)

	# Запись всех данных в файлы
	write_futures(data_fut_2024, data_fut_q, data_global, date_string, dir_name, name_qr, gl_date)
	write_forex(data_for_2024, data_for_q, data_global, date_string, dir_name, name_qr, gl_date)


def get_global_data(global_list)->list:
	"""Получение мест участников The Global Cup Trading Championships™️ 2024-2025"""
	new_list = []
	for item in global_list:
		small_list = []
		for it in item.find_all('td'):
			small_list.append(it.text)
		new_list.append(small_list)
	return new_list


def write_futures(data_fut, data_1q, data_gl, date, dir_d, qr, gl_date):
	""" Запись данных фьючерса в общий файл"""
	with open(dir_d + '\\' + 'Fut_' + date + '.csv', 'w', encoding='utf-8', newline='') as f:
		print("*********FUTURES_WORLD*********")
		f.writelines(NAME_WORLD + '\n')
		for item in data_fut:
			csv.writer(f, delimiter=';').writerow(item)
			print(item)
		f.writelines('\n')
		
		print("*********QUARTER*********")
		f.writelines(qr + '\n')
		for item in data_1q:
			csv.writer(f, delimiter=';').writerow(item)
			print(item)
		f.writelines('\n')
		
		print("*********FUTURES_GLOBAL**********")
		f.writelines(NAME_GLOBAL + '\n')
		f.writelines(gl_date + '\n')
		for item in data_gl:
			csv.writer(f, delimiter=';').writerow(item)
			print(item)
		f.writelines('\n')


def write_forex(data_for, data_1q, data_global, date, dird, qr, gl_date):
	""" Запись данных форекса в общий файл"""
	with open(dird + '\\' + 'For_' + date + '.csv', 'w', encoding='utf-8', newline='') as f:
		print("**********FOREX_WORLD**********")
		f.writelines(NAME_WORLD + '\n')
		for item in data_for:
			csv.writer(f, delimiter=';').writerow(item)
			print(item)
		f.writelines('\n')
		
		print("*********QUARTER**********")
		f.writelines(qr + '\n')
		for item in data_1q:
			csv.writer(f, delimiter=';').writerow(item)
			print(item)
		f.writelines('\n')
		
		print("*********FOREX_GLOBAL**********")
		f.writelines(NAME_GLOBAL + '\n')
		f.writelines(gl_date + '\n')
		for item in data_global:
			csv.writer(f, delimiter=';').writerow(item)
			print(item)
		f.writelines('\n')

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
	dirname = os.path.abspath(__file__)
	dir_nam = '\\'.join(dirname.split('\\')[:-1])
	parsing_page(PAGE, dir_nam)
