#!/usr/bin/env python3

import collections
from threading import Thread
from selenium import webdriver
import time
import itertools
import pandas as pd
import xlwt
from bs4 import BeautifulSoup
import lxml
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
import os

_VERSION = '1.2'


def login(driver, url, email, password):
    """
    This function logging in a user with given email and password.
    :param url: address of the web page
    :param email: email for the login
    :param password: password for the login
    """
    count = 0
    while True:
        try:
            count += 1
            driver.get(url)
            driver.find_element_by_id('CybotCookiebotDialogBodyButtonAccept').click()
            driver.get(url)
            driver.find_elements_by_xpath('//div[@class="rn-menuBar__navWrp"]//''div[@id="react-rp-auth-root"]'
                                          '//div//div//div//div')[0].click()
            break
        except (WebDriverException, IndexError):
            print("Reload %s" % count)

    driver.find_elements_by_xpath('//div[@class="fields__validationWrapper___3D3Kv"]')[0]\
        .find_element_by_tag_name('input').send_keys(email)
    driver.find_elements_by_xpath('//div[@class="fields__validationWrapper___3D3Kv"]')[1]\
        .find_element_by_tag_name('input').send_keys(password)
    driver.find_element_by_xpath('//div[@class="fields__submitField___T-_wW"]//button').click()
    time.sleep(10)


def save_to_excel(data, name):
    """
    This functions saves data(that is represented as dictionary collection) to Excel file.
    :param data: dictionary.
    """

    try:
        df = pd.DataFrame(data, columns=data.keys())
        df.index += 1
        columns = ['Fullname', 'Runs', 'Wins', '2nds', '3rds', 'Earnings', 'OR', 'TS', 'RPR']
        nums = [str(num) for num in range(1, 63)]
        for num in nums:
            columns.append(num)
        df = df[columns]
        filename = "Output #%s.xls" % name
        writer = pd.ExcelWriter(filename)
        df.to_excel(writer)
        writer.save()
    except ValueError:
        for key, value in data.items():
            print(key, len(value))


def count_pages(soup):
    """
    This function counts how much pages of horse profiles each combination of 3 letters have.
    :param soup: gives the 'html' sctructure of the page to parse and find how many horse profiles this page have.
    :return: returns number of pages.
    """

    pages = int(soup.find('span', {'class': 'search-resultCounter'}).text.replace(',', '')) / 15
    pages1 = int(soup.find('span', {'class': 'search-resultCounter'}).text.replace(',', '')) // 15
    if pages != pages1:
        if pages >= 100 or pages == 99:
            pages = 100
        else:
            pages += 1

    return int(pages)


def main(start, proc, end=None):

    chromedriver = 'chromedriver.exe'  # for Windows OS Chrome
    # chromedriver = '/Users/ilchenkoslava/Downloads/chromedriver3' # for Mac OS
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_option = webdriver.ChromeOptions()
    chrome_option.add_experimental_option("prefs", prefs)
    # chrome_option.add_argument("headless")
    driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chrome_option)
    # driver = webdriver.Chrome(executable_path=chromedriver)
    login(driver, 'https://www.racingpost.com/', 'jmcatelen@hotmail.com', '22Muyse22')

    chars = [chr(c) for c in range(ord('a'), ord('z') + 1)]
    keywords = [''.join(i) for i in itertools.product(chars, repeat=3)]
    if end is None:
        end = keywords[-1]
    query_url = 'https://www.racingpost.com/search/?tab=profiles&page=%d&query=%s&profiles_type=horses_profiles'
    lists = collections.defaultdict(list)
    counter = 0

    while True:
        try:
            for k in keywords[keywords.index(start):keywords.index(end)]:
                copy_list = lists
                if counter > 1000:
                    print(k, proc)
                    filename = '{0} '.format(counter) + k
                    save_to_excel(lists, filename)
                    counter = 0
                    lists = collections.defaultdict(list)

                driver.get(query_url % (1, k))
                time.sleep(3)
                soup = BeautifulSoup(driver.page_source, 'lxml')
                if soup.find('span', {'class': 'search-resultCounter'}).text == '0':
                    print('No horses here')
                    continue
                else:
                    pages = count_pages(soup)
                    for page in range(1, pages + 1):
                        names = []
                        driver.get(query_url % (page, k))
                        time.sleep(3)
                        horses_list = driver.find_elements_by_class_name('search-resultList__item')
                        horses_urls = []

                        for horse in horses_list:
                            horses_urls.append(horse.find_element_by_tag_name('a').get_attribute('href') + '/form')
                            name = horse.find_element_by_class_name('search-resultList__linkName').text
                            names.append(name)
                            country = horse.find_element_by_class_name('search-resultList__linkCountry').text
                            year = horse.find_element_by_class_name('search-resultList__linkYear').text
                            lists['Fullname'].append(name + " " + "(" + country + ")" + " " + year)
                        for n in names:
                            driver.get('https://www.pedigreequery.com/%s' % n)
                            male = []
                            female = []
                            try:
                                table = driver.find_element_by_class_name('pedigreetable')
                                if table.find_elements_by_class_name('w'):
                                    for zz in range(1, 63):
                                        lists[str(zz)].append('-')
                                    continue

                                for m in table.find_elements_by_class_name('f'):
                                    if m.get_attribute('data-g') is not None:
                                        male.append((m.get_attribute('data-g'),
                                                     m.text.replace('\n', '').split(')')[0] + ')'))

                                for f in table.find_elements_by_class_name('f'):
                                    if f.get_attribute('data-g') is not None:
                                        female.append((f.get_attribute('data-g'),
                                                       f.text.replace('\n', '').split(')')[0] + ')'))

                                for i, ma in enumerate(sorted(male, key=lambda i: i[0]), 1):
                                    lists[str(i)].append(ma[1])
                                for ii, fe in enumerate(sorted(female, key=lambda i: i[0]), 1):
                                        lists[str(len(male) + ii)].append(fe[1])
                            except (StaleElementReferenceException, NoSuchElementException) as e:
                                for zz in range(1, 63):
                                    lists[str(zz)].append('-')
                            except TimeoutException:
                                save_to_excel(copy_list, filename)

                        for horse_url in horses_urls:
                            driver.get(horse_url)
                            try:
                                if driver.find_element_by_class_name('p404-error'):
                                    print('No data')
                                    for key, v in lists.items():
                                        try:
                                            if isinstance(int(key), int):
                                                continue
                                        except ValueError:
                                            if key == 'Fullname':
                                                continue
                                            v.append('-')
                                    continue
                            except NoSuchElementException:
                                pass

                            time.sleep(3)
                            counter += 1
                            # print(counter)
                            try:
                                if driver.find_element_by_class_name('ui-errorMessage__text'):
                                    print('No data')
                                    lists['OR'].append('-')
                                    lists['TS'].append('-')
                                    lists['RPR'].append('-')
                                    lists['Runs'].append('-')
                                    lists['Wins'].append('-')
                                    lists['2nds'].append('-')
                                    lists['3rds'].append('-')
                                    lists['Earnings'].append('-')
                            except NoSuchElementException:
                                soup_form = BeautifulSoup(driver.page_source, 'lxml')
                                try:
                                    trs = soup_form.find_all('tbody', {'class': 'ui-table__body'})[0].find_all('tr')
                                    tds = trs[-1].find_all('td')
                                    lists['Runs'].append(tds[1].text)
                                    lists['Wins'].append(tds[2].find_all('span')[0].text.split('/')[0])
                                    lists['2nds'].append(tds[3].text)
                                    lists['3rds'].append(tds[4].text)
                                    lists['Earnings'].append(tds[7].text)
                                    ors = []
                                    tss = []
                                    rprs = []
                                    for rows in trs:
                                        if '—' not in rows.find_all('td')[8].text:
                                            ors.append(int(rows.find_all('td')[8].text))
                                    for rows in trs:
                                        if '—' not in rows.find_all('td')[9].text:
                                            tss.append(int(rows.find_all('td')[9].text))
                                    for rows in trs:
                                        if '—' not in rows.find_all('td')[10].text:
                                            rprs.append(int(rows.find_all('td')[10].text))

                                    lists['OR'].append('-') if len(ors) == 0 else lists['OR'].append(max(ors))
                                    lists['TS'].append('-') if len(tss) == 0 else lists['TS'].append(max(tss))
                                    lists['RPR'].append('-') if len(rprs) == 0 else lists['RPR'].append(max(rprs))
                                except IndexError:
                                    time.sleep(5)
                                    print('IndexError appeared')
                                    lists['OR'].append('-')
                                    lists['TS'].append('-')
                                    lists['RPR'].append('-')
                                    lists['Runs'].append('-')
                                    lists['Wins'].append('-')
                                    lists['2nds'].append('-')
                                    lists['3rds'].append('-')
                                    lists['Earnings'].append('-')
                        len_value = len(lists['OR'])
                        if all(len_value == len(value) for value in lists.values()) is False:
                            for key, value in lists.items():
                                print(key, len(value), value)
                            exit()
            break
        except KeyboardInterrupt:
            save_to_excel(copy_list, filename)
            exit()
        except TimeoutException:
            print(k)
            save_to_excel(copy_list, filename)
    save_to_excel(lists, filename)


if __name__ == '__main__':
    t1 = Thread(target=main, args=('abv', 2, 'giq'))
    t2 = Thread(target=main, args=('giq', 1, 'iii'))
    t3 = Thread(target=main, args=('iii', 1, 'mmm'))
    t4 = Thread(target=main, args=('mmm', 2, 'ppp'))
    t5 = Thread(target=main, args=('ppp', 1, 'sss'))
    t6 = Thread(target=main, args=('sss', 2, 'uuu'))
    t7 = Thread(target=main, args=('uuu', 1, 'xxx'))
    t8 = Thread(target=main, args=('xxx', 2, 'zzz'))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
    t7.start()
    t8.start()

