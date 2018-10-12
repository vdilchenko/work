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
import copy
import numpy as np


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
            break
        except WebDriverException:
            print("Reload %s" % count)
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


def main(chunk, proc):
    try:
        # chromedriver = 'chromedriver.exe'  # for Windows OS Chrome
        chromedriver = '/Users/ilchenkoslava/Downloads/chromedriver3' # for Mac OS
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_option = webdriver.ChromeOptions()
        chrome_option.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chrome_option)
        login(driver, 'https://www.racingpost.com/', 'jmcatelen@hotmail.com', '22Muyse22')

        query_url = 'https://www.racingpost.com/search/?tab=profiles&page=%d&query=%s&profiles_type=horses_profiles'
        lists = collections.defaultdict(list)
        counter = 0
        iii = 250
        while True:
            try:
                for k in chunk:
                    copy_list = copy.copy(lists)
                    if counter > iii:
                        # print(proc, k, counter)
                        iii += 250
                    if counter > 2000:
                        iii = 0
                        filename = '{0} {1}'.format(proc, counter) + k
                        save_to_excel(lists, filename)
                        counter = 0
                        lists = collections.defaultdict(list)

                    driver.get(query_url % (1, k))
                    time.sleep(3)
                    soup = BeautifulSoup(driver.page_source, 'lxml')
                    try:
                        if soup.find('span', {'class': 'search-resultCounter'}).text == '0':
                            continue
                        else:
                            pages = count_pages(soup)
                            page = 0
                            while page != pages:
                                driver.get(query_url % (page, k))
                                time.sleep(3)
                                horses_list = driver.find_elements_by_class_name('search-resultList__item')
                                horses_urls = []

                                for horse in horses_list:
                                    horses_urls.append(horse.find_element_by_tag_name('a').get_attribute('href')
                                                       + '/form')
                                    name = horse.find_element_by_class_name('search-resultList__linkName').text
                                    country = horse.find_element_by_class_name('search-resultList__linkCountry').text
                                    year = horse.find_element_by_class_name('search-resultList__linkYear').text
                                    lists['Fullname'].append(name + " " + "(" + country + ")" + " " + year)

                                for n in lists['Fullname']:
                                    driver.get('https://www.pedigreequery.com/')
                                    time.sleep(5)
                                    driver.find_elements_by_class_name('menu')[1].find_element_by_tag_name('input').\
                                        send_keys(n.split('(')[0])
                                    driver.find_elements_by_class_name('prettybutton')[1].submit()
                                    try:
                                        tablesorter = driver.find_element_by_class_name('tablesorter')
                                        try:
                                            fullnames = tablesorter.find_elements_by_class_name('m')[1]
                                            fullnames = tablesorter.find_elements_by_class_name('m')
                                        except Exception as e:
                                            fullnames = tablesorter.find_elements_by_class_name('f')

                                        horses = [full.text for full in fullnames]
                                        date_of_birth = [d.find_elements_by_class_name('w')[0].text for d in
                                                         tablesorter.find_elements_by_tag_name('tr')[1:]]
                                        stop = False
                                        for hors in horses:
                                            for dob in date_of_birth:
                                                if (hors.lower() + ' ' + str(dob)) == n.lower():
                                                    stop = True
                                                    horse_index = date_of_birth.index(dob)
                                                    break
                                            if stop is True:
                                                break

                                        url_horse = fullnames[horse_index].find_elements_by_tag_name('a')[0].\
                                            get_attribute('href')
                                        driver.get(url_horse)

                                    except Exception as e:
                                        # print('Unique {0} or No matches'.format(n))
                                        pass

                                    male = []
                                    female = []
                                    try:
                                        table = driver.find_element_by_class_name('pedigreetable')
                                        if table.find_elements_by_class_name('w'):
                                            for zz in range(1, 63):
                                                lists[str(zz)].append('-')
                                            continue

                                        for m in table.find_elements_by_class_name('m'):
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
                                    except (StaleElementReferenceException, NoSuchElementException):
                                        for zz in range(1, 63):
                                            lists[str(zz)].append('-')
                                    except TimeoutException:
                                        filename = '{0} {1}'.format(proc, counter) + k
                                        save_to_excel(copy_list, filename)
                                page += 1

                                for horse_url in horses_urls:
                                    driver.get(horse_url)
                                    try:
                                        if driver.find_element_by_class_name('p404-error'):
                                            lists['OR'].append('-')
                                            lists['TS'].append('-')
                                            lists['RPR'].append('-')
                                            lists['Runs'].append('-')
                                            lists['Wins'].append('-')
                                            lists['2nds'].append('-')
                                            lists['3rds'].append('-')
                                            lists['Earnings'].append('-')
                                            continue
                                    except NoSuchElementException:
                                        pass

                                    time.sleep(3)
                                    counter += 1
                                    try:
                                        if driver.find_element_by_class_name('ui-errorMessage__text'):
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
                                            lists['OR'].append('-')
                                            lists['TS'].append('-')
                                            lists['RPR'].append('-')
                                            lists['Runs'].append('-')
                                            lists['Wins'].append('-')
                                            lists['2nds'].append('-')
                                            lists['3rds'].append('-')
                                            lists['Earnings'].append('-')
                                if len(lists['Fullname']) != len(lists['61']):
                                    for ke, valu in lists.items():
                                        print(ke, len(valu), valu)
                                        while len(valu) != len(lists['Fullname']):
                                            valu.append('-')
                    except Exception as e:
                        print(e)
                        print(driver.current_url)
                        continue
                print("THREAD #%d IS OVER" % proc)
                break
            except KeyboardInterrupt:
                print('Proc: {0} keyboard interrupt'.format(proc))
                filename = '{0} {1}'.format(proc, counter) + k
                save_to_excel(copy_list, filename)
                exit()
            except TimeoutException:
                print('Proc: {0} timed out'.format(proc))
                filename = '{0} {1}'.format(proc, counter) + k
                save_to_excel(copy_list, filename)
                exit()
        filename = '{0} {1}'.format(proc, counter) + k
        save_to_excel(lists, filename)
    except WebDriverException:
        filename = '{0} {1}'.format(proc, counter) + k
        save_to_excel(copy_list, filename)


if __name__ == '__main__':
    chars = [chr(c) for c in range(ord('a'), ord('z') + 1)]
    keywords = [''.join(i) for i in itertools.product(chars, repeat=4)]
    chunked_keywords = np.array_split(keywords, 5)

    t1 = Thread(target=main, args=(chunked_keywords[0], 1))
    t2 = Thread(target=main, args=(chunked_keywords[1], 2))
    t3 = Thread(target=main, args=(chunked_keywords[2], 3))
    t4 = Thread(target=main, args=(chunked_keywords[3], 4))
    t5 = Thread(target=main, args=(chunked_keywords[4], 5))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
