"""
This program scrapes data from RacingPost and PedigreeQuery and extracts it to an Excel files when data length equals to 100 or more.
This is not final version of a program.
"""
import collections
from selenium import webdriver
import time
import itertools
import pandas as pd
import xlwt
from bs4 import BeautifulSoup
import lxml
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException

_VERSION = '1.0'


def login(url, email, password):
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
        except WebDriverException:
            print("Reload %s" % count)

    driver.find_elements_by_xpath('//div[@class="fields__validationWrapper___3D3Kv"]')[0]\
        .find_element_by_tag_name('input').send_keys(email)
    driver.find_elements_by_xpath('//div[@class="fields__validationWrapper___3D3Kv"]')[1]\
        .find_element_by_tag_name('input').send_keys(password)

    driver.find_element_by_xpath('//div[@class="fields__submitField___T-_wW"]//button').click()

    time.sleep(10)


def save_to_excel(data, number):
    """
    This functions saves data(that is represented as dictionary collection) to Excel file.
    :param data: dictionary.
    """

    df = pd.DataFrame(data, columns=data.keys())

    df.index += 1
    columns = ['Fullname', 'Runs', 'Wins', '2nds', '3rds', 'Earnings', 'OR', 'TS', 'RPR']
    nums = [str(num) for num in range(1, 63)]
    for num in nums:
        columns.append(num)
    df = df[columns]
    filename = "Output #%d.xls" % number
    writer = pd.ExcelWriter(filename)
    df.to_excel(writer)
    writer.save()


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


if __name__ == '__main__':
    chromedriver = 'chromedriver.exe'
    driver = webdriver.Chrome(chromedriver)

    login('https://www.racingpost.com/', 'jmcatelen@hotmail.com', '22Muyse22')

    chars = [chr(c) for c in range(ord('a'), ord('z') + 1)]
    keywords = [''.join(i) for i in itertools.product(chars, repeat=3)]
    query_url = 'https://www.racingpost.com/search/?tab=profiles&page=%d&query=%s&profiles_type=horses_profiles'
    lists = collections.defaultdict(list)
    by_xpaths = driver.find_elements_by_xpath
    counter = 0

    while True:
        try:
            for k in keywords[keywords.index('aas')+1:]:
                # for key, value in lists.items():
                #     print(key, len(value))
                copy_list = lists
                if counter > 100:
                    print(k)
                    save_to_excel(lists, counter)
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
                                abc = 'ch.', 'gr.', 'b.', 'br.', 'blk.', 'dkb/br.', 'blk/br.', 'chuck.'
                                if table.find_elements_by_class_name('w'):
                                    print('a')
                                    for zz in range(1, 63):
                                        lists[str(zz)].append('-')
                                    continue

                                for m in table.find_elements_by_class_name('m'):
                                    horsename_m = m.find_element_by_xpath('//a[@class="horseName"]').text
                                    if (horsename_m.startswith(abc)) or (horsename_m.isupper() is False):
                                        continue
                                    male.append((m.get_attribute('data-g'), horsename_m.replace('\n', '')))

                                for f in table.find_elements_by_class_name('f'):
                                    horsename_f = f.find_element_by_xpath('//a[@class="horseName"]').text
                                    if (horsename_f.startswith(abc)) or (horsename_f.isupper() is False):
                                        continue
                                    female.append((f.get_attribute('data-g'), horsename_f.replace('\n', '')))
                                print(male)
                                print(female)

                                for i, ma in enumerate(sorted(male, key=lambda i: i[0]), 1):
                                    lists[str(i)].append(ma[1])
                                for ii, fe in enumerate(sorted(female, key=lambda i: i[0]), 1):
                                        lists[str(len(male) + ii)].append(fe[1])
                            except (StaleElementReferenceException, NoSuchElementException) as e:
                                print(e)
                                print('raz')
                                for zz in range(1, 63):
                                    lists[str(zz)].append('-')
                            except TimeoutException:
                                save_to_excel(copy_list, counter)

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
                            print(counter)
                            if 'No race record for this horse' not in \
                                    by_xpaths('//tbody[@class="ui-table__body"]//tr[1]/td')[0].text:
                                lists['Runs'].append(by_xpaths('//tbody[@class="ui-table__body"]//tr[last()]/td')[1].text)
                                lists['Wins'].append(by_xpaths('//tbody[@class="ui-table__body"]//tr[last()]/td')[2].text)
                                lists['2nds'].append(by_xpaths('//tbody[@class="ui-table__body"]//tr[last()]/td')[3].text)
                                lists['3rds'].append(by_xpaths('//tbody[@class="ui-table__body"]//tr[last()]/td')[4].text)
                                lists['Earnings'].append(by_xpaths('//tbody[@class="ui-table__body"]//tr[last()]/td')[7].text)
                                ors = []
                                tss = []
                                rprs = []
                                for rows in by_xpaths('//tbody[@class="ui-table__body"]//tr'):
                                    ors.append(rows.find_elements_by_xpath('//td')[8].text)
                                for rows in by_xpaths('//tbody[@class="ui-table__body"]//tr'):
                                    tss.append(rows.find_elements_by_xpath('//td')[9].text)
                                for rows in by_xpaths('//tbody[@class="ui-table__body"]//tr'):
                                    rprs.append(rows.find_elements_by_xpath('//td')[10].text)
                                lists['OR'].append(max(ors))
                                lists['TS'].append(max(tss))
                                lists['RPR'].append(max(rprs))
                            else:
                                print('No data')
                                for key, v in lists.items():
                                    try:
                                        if isinstance(int(key), int):
                                            continue
                                    except ValueError:
                                        if key == 'Fullname':
                                            continue
                                        v.append('-')

            break
        except KeyboardInterrupt:
            save_to_excel(lists, counter)
            exit()
        except TimeoutException:
            print(k)
            save_to_excel(copy_list, counter)
    save_to_excel(lists, counter)
    
