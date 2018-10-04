#!/usr/bin/env python3

from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import collections
import lxml
import pandas as pd
import xlsxwriter

chrome = '/Users/ilchenkoslava/Downloads/chromedriver3'
driver = webdriver.Chrome(chrome)

driver.get('https://www.naec.org/member-site/directory.html')
driver.find_element_by_id('search_keyword').click()
driver.find_element_by_xpath('//input[@type="submit"]').click()


def save_to_excel(data):
    df = pd.DataFrame(data, columns=data.keys())
    writer = pd.ExcelWriter('NAEC.xlsx', engine='xlsxwriter')
    df.to_excel(writer)
    writer.save()


def get_urls():
    soup = BeautifulSoup(driver.page_source, 'lxml')
    urls = []
    columns = soup.find_all('div', {'class': 'column'})
    for col in columns:
        try:
            urls.append(col.find('h4').find('a')['href'])
        except AttributeError:
            print(urls[-1])
            break
    return urls


if __name__ == '__main__':
    data = collections.defaultdict(list)
    urls = get_urls()
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        data['Company name'].append(soup.find('h1', {'class': 'location-name'}).text)
        try:
            address = soup.find('span', {'itemprop': 'addressLocality'}).text.split(',')
            data['City'].append(address[0].strip())
            try:
                data['State'].append(address[1].strip().split('\t')[0])
            except IndexError:
                data['State'].append('-')
            try:
                data['Country'].append(address[1].strip().split('\t')[-1])

            except IndexError:
                data['Country'].append('-')
        except AttributeError:
            print(url + 'тут нет адреса')
        try:
            data['Email'].append(soup.find('span', {'itemprop': 'email'}).text)
        except AttributeError:
            data['Email'].append('-')
        try:
            data['Website'].append(soup.find('span', {'itemprop': 'website'}).find('a')['href'])
        except AttributeError:
            data['Website'].append('-')
        try:
            data['Description'].append(soup.find('div', {'itemprop': 'description'}).text.strip())
        except AttributeError:
            data['Description'].append('-')
    save_to_excel(data)

