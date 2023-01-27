import urllib
import requests
import os
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen, urlretrieve

DOWNLOAD_DIR = 'F:\\Data\\Zerich\\'
URL_DOWN = 'http://erinrv.qscalp.ru/'
#   2021-05-28


# Поиск директорий на странице
def read_url(sub_dir):
    url = URL_DOWN.replace(" ", "%20")
    req = Request(URL_DOWN)
    a = urlopen(req).read()
    soup = BeautifulSoup(a, 'html.parser')
    x = (soup.find_all('a'))
    dir_list = []
    for i in x:
        file_name = i.extract().get_text()
        url_new = url + file_name
        url_new = url_new.replace(" ","%20")
        if(file_name[-1]=='/' and file_name[0]!='.'):
            read_url(url_new)
        #print(url_new.split('/')[3][:7])
        if url_new.split('/')[3][:7] == sub_dir:
            dir_list.append(url_new)
    return dir_list


def download_files(sub_dir):
     URL_NEW = URL_DOWN + sub_dir + '/'
     down_dir = DOWNLOAD_DIR + sub_dir
     down_directs = read_url(sub_dir)

     html_content = requests.get(URL_NEW)
     soup = BeautifulSoup(html_content.content, 'html.parser')
     f_links = soup.findAll('a')

     dir_content = requests.get(DOWNLOAD_DIR)
     print(dir_content.text)

     for one_dir in down_directs:
         html_content = requests.get(one_dir)
         soup = BeautifulSoup(html_content.content, 'html.parser')
         f_links = soup.findAll('a')
         down_dir = DOWNLOAD_DIR + one_dir[24:]

         if not os.path.exists(down_dir):
            os.mkdir(down_dir)
            print('Создана папка: ' + down_dir)
         else:
            print('Имеется уже папка: ' + down_dir)

         for file_name in f_links:
            url_file = one_dir + '/' + file_name.text
            down_file = down_dir + '\\' + file_name.text
            if url_file.endswith('qsh'):
                urllib.request.urlretrieve(url_file, down_file)
                print(down_file)


if __name__ == '__main__':
    sub_dir = input("Input directory:\n")
    download_files(sub_dir)

