#1.Запускаем сервер (эту ячейку) CTRL+ENTER
#2.В КВИКе запускаем луа-скрипт QuikLuaPython.lua
import socket
import threading
import pandas as pd

ticker = 'BRN0' #В Квике должен быть открыт стакан BRN0, а в таблице обезличенных сделок транслироваться тики BRN0
ticks=[] #Для примера, список обезличенных сделок BRN0
stakan = '' # строка формата '"имя тикера" {bid_price:bid_size,bid_price1:bid_size1...ask_price:-ask_size,ask_price1:-ask_size1}'

def parser (res):
    parse = res.split(" ", 2) #первый элемент - идентификатор события, второй имя тикера
    if parse[0] == '2': # парсинг стакана (событие '2')
        if parse[1] == ticker:
            global stakan
            stakan = parse[2]
    if parse[0] == '1': # парсинг обезличенной сделки (событие '1')
        tail = res.split(" ")
        if tail[1] == ticker: #записываем цену текущего тика BRN0 в список ticks
            ticks.append(float(tail[4]))

#Собственно сервер
def service():
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1',3587)) #Локальный хост-этот компьютер, порт - 3587
    while True:
        res = sock.recv(2048).decode('utf-8')
        if res == '<qstp>\n':  #строка приходит от клиента при остановке луа-скрипта в КВИКе
            break
        else:
            parser(res) #Здесь вызываете свой парсер. Для примера функция: parser (parse)
    sock.close()

#Запускаем сервер в своем потоке
t = threading.Thread(name='service', target = service)
t.start()


if __name__ == '__main__':
    service()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
