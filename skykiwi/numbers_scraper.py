import requests
import lxml
from bs4 import BeautifulSoup
import pandas as pd
import collections
from threading import Thread
import numpy as np


def save(data, thread):
    df = pd.DataFrame(data, columns=data.keys())
    df.index += 1
    df = df[['URL', 'Phone number']]
    writer = pd.ExcelWriter('Data%s.xlsx' % thread, engine='xlsxwriter')
    df.to_excel(writer)
    writer.save()


def get_phone(chunked_urls, number):
    new_data = collections.defaultdict(list)
    for hr in chunked_urls:
        try:
            req = requests.get(hr)
            phone_number = BeautifulSoup(
                requests.get(hr).text, 'lxml').find_all('td', {'class': 'td-content'})[1].text
            if phone_number.startswith('02'):
                new_data['Phone number'].append(phone_number)
                new_data['URL'].append(hr)
            else:
                continue
        except (IndexError, AttributeError):
            try:
                phone_number = BeautifulSoup(req.text, 'lxml'). \
                    find('div', {'class': 'typeoption'}).find('table').find_all('tr')[1].find('td').text
                if phone_number.startswith('02'):
                    new_data['Phone number'].append(phone_number)
                    new_data['URL'].append(hr)
                else:
                    continue
            except (IndexError, AttributeError):
                print('Finding data in text on {0}'.format(hr))
                try:
                    t_f = BeautifulSoup(req.text, 'lxml').find_all('td', {'class': 't_f'})[0].text.split('\n')
                except IndexError:
                    continue
                o_twos = []
                for t in t_f:
                    t = t.replace(' ', '')
                    try:
                        o_two = ''
                        n = 4
                        if isinstance(int(t[t.index('02'):t.index('02') + n]), int):
                            while True:
                                try:
                                    if isinstance(int(t[t.index('02'):t.index('02') + n]), int):
                                        if isinstance(int(t[t.index('02') + n]), int):
                                            n += 1
                                            o_two = t[t.index('02'):t.index('02') + n]
                                except Exception:
                                    break
                            if len(o_two) != 0:
                                o_twos.append(o_two)
                    except ValueError:
                        pass

                if len(o_twos) != 0:
                    phone_number = o_twos[0]
                    new_data['Phone number'].append(phone_number)
                    new_data['URL'].append(hr)
                    print('Found')

    save(new_data, number)


if __name__ == '__main__':    
    URL = 'http://bbs.skykiwi.com/forum.php?mod=forumdisplay&fid=205&page={0}'
    page = 1
    
    r = requests.get(URL.format(page))
    last_page = int(BeautifulSoup(r.text, 'lxml').find_all('div', {'class': 'pg'})[0].find_all('a')[-2].
                    text.split(' ')[1])
    data = collections.defaultdict(list)
    
    while page != last_page + 1:
        page_url = requests.get(URL.format(page))
        soup = BeautifulSoup(page_url.text, 'lxml')
        normal_threads = soup.find_all('tbody')
        for normal_thread in normal_threads:
            try:
                if normal_thread['id'].startswith('normalthread'):
                    data['URL'].append('http://bbs.skykiwi.com/' + normal_thread.find('td', {'class': 'icn'}).
                                       find('a')['href'])
            except KeyError:
                continue
        print(page)
        page += 1
    
    chunked_urls = np.array_split(data['URL'], 7)
    
    thread1 = Thread(target=get_phone, args=[chunked_urls[0], '1'])
    thread2 = Thread(target=get_phone, args=[chunked_urls[1], '2'])
    thread3 = Thread(target=get_phone, args=[chunked_urls[2], '3'])
    thread4 = Thread(target=get_phone, args=[chunked_urls[3], '4'])
    thread5 = Thread(target=get_phone, args=[chunked_urls[4], '5'])
    thread6 = Thread(target=get_phone, args=[chunked_urls[5], '6'])
    thread7 = Thread(target=get_phone, args=[chunked_urls[6], '7'])
    
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()
    thread6.start()
    thread7.start()
