from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException,\
	StaleElementReferenceException, TimeoutException

from bs4 import BeautifulSoup
import lxml
from openpyxl import Workbook

from time import sleep

import pandas as pd

from collections import defaultdict

from pyvirtualdisplay import Display
display = Display(visible=0)  
display.start()


def survey_check(driver):
	soup = BeautifulSoup(driver.page_source, "lxml")
	try:
		survey_btn = soup.find("div", {"class": "vp-dialog-title"}).text
		if "Survey" in survey_btn:
			print("Survey dialog, closing")
			driver.find_element_by_xpath("//button[@class='vp-dialog-cancel']").click()
	except AttributeError:
		pass


def pass_empty():
	data_to_add = [address[0]]
	for _ in columns[1:]:
		data_to_add.append(None)
	ws.append(data_to_add)
	wb.save("viewpoint_ca3.xlsx")


addresses = pd.read_excel("Nova for new.xlsx", header=1, usecols="A")

email = "vdilchenko@gmail.com"
password = "Password1234"

options = webdriver.ChromeOptions()
# options.add_argument('headless')

driver = webdriver.Chrome("chromedriver", options=options)
driver.get("https://www.viewpoint.ca/user/login")

driver.find_element_by_xpath("//input[@name='email']").send_keys(email)
driver.find_element_by_xpath("//input[@name='password']").send_keys(password)
driver.find_element_by_xpath("//button[@type='submit']").click()

ignored_exceptions = (NoSuchElementException, StaleElementReferenceException, TimeoutException)

wb = Workbook()
ws = wb.active

years = [str(i) for i in range(2008, 2021)]

detail_columns = [
	"Type", "Style", "Building Style", "Listed By", "Age", "Beds", "Baths", "Main Living Area",
	"Total Living Area", "Listing Parcel Size", "Building Dimensions", "Prov. Parcel Size",
	"PID", "Assessed At", "Waterfront", "Heating/Cooling", "Fuel", "Has Garage", "Garage Type",
	"Drinking Water Source", "Sewer", "Roof", "PCDS", "Parking", "Foundation",
	"Applainces Incl.", "Flooring,Utilities"]

columns = [
	"Address", "Address from site", "Status", "Start date", "End Date", "List Price",
	"Sold Price", "Duration"] + years + detail_columns
ws.append(columns)

for address in addresses.values[353000:]:
	data = defaultdict(list)
	for year in years:
		data[year] = []

	search = WebDriverWait(driver, 5).until(EC.presence_of_element_located(
		(By.XPATH, "//input[@name='omnibox']")))
	search.send_keys(address)

	el = driver.find_element_by_xpath("//span[@class='search-btn']")
	ActionChains(driver).key_down(Keys.ENTER).click(el).key_up(Keys.ENTER)\
		.perform()

	sleep(5)

	survey_check(driver)

	try:
		error = WebDriverWait(driver, 1, ignored_exceptions=ignored_exceptions).until(
			EC.presence_of_element_located((By.XPATH, "//div[@class='vp-dialog-bg']")))
		pass_empty()
		driver.find_element_by_xpath("//button[@class='vp-dialog-cancel']").click()
		sleep(2)
		driver.find_element_by_xpath("//input[@name='omnibox']").clear()
		continue
	except TimeoutException:
		try:
			driver.find_element_by_xpath("//div[@class='vpiw-big']").click()
		except (NoSuchElementException, ElementNotInteractableException):
			pass_empty()
			sleep(2)
			driver.find_element_by_xpath("//input[@name='omnibox']").clear()
			continue

	sleep(3)

	soup = BeautifulSoup(driver.page_source, "lxml")
	try:
		address_site = soup.find("div", {"class": "overlay-address-wrap"}).text
	except AttributeError:
		address_site = soup.find_all("div", {"class": "vpiw-meta bottom-meta"})[-1].text
	try:
		age = soup.find("span", {"class": "age"}).parent.find_all("span")[1].find_all("div")[1].text
	except AttributeError:
		age = None
	data["Age"].append(age)

	# sales history
	try:
		driver.find_element_by_xpath(
			"//div[@class='cutsheet-section cutsheet-section-history-wrap collapsed']").click()
	except:
		pass

	sleep(2)
	soup = BeautifulSoup(driver.page_source, "lxml")

	try:
		last_status_div = soup.find("div", {
			"class": "mls-history-section-desktop"}).find_all("div")[1]
		status = last_status_div.find("span", {"class": "history-status"}).text
		start_date = last_status_div.find_all("span", {
			"class": "history-date"})[0].text
		end_date = last_status_div.find_all("span", {
			"class": "history-date"})[1].text
		start_price = last_status_div.find_all("span", {
			"class": "history-price"})[0].text.replace("$", "").replace(",", ".")
		end_price = last_status_div.find_all("span", {
			"class": "history-price"})[1].text.replace("$", "").replace(",", ".")
		duration = last_status_div.find("span", {"class": "history-dom"}).text
	except IndexError:
		status = None
		start_price = None
		start_date = None
		end_price = None
		end_date = None
		duration = None

	data_to_add = [address[0], address_site, status, start_date, end_date, start_price, end_price, duration]

	# taxes/assessment history
	try:
		driver.find_element_by_xpath(
			"//div[@class='cutsheet-section cutsheet-section-taxes collapsed']").click()
	except:
		pass

	sleep(2)
	soup = BeautifulSoup(driver.page_source, "lxml")

	ass_tbl_body = soup.find("div", {"class": "assessment-tbl-body"})
	try:
		elements = ass_tbl_body.find_all("div")
		for el in elements:
			el_year = el.find_all("span")[0].text
			tax = el.find_all("span")[1].text.replace("$", "").replace(",", ".")
			data[el_year].append(tax)
	except AttributeError:
		pass

	for year in years:
		if len(data[year]) < 1:
			data[year].append(None)
		data_to_add.extend(data[year])

	# details
	try:
		driver.find_element_by_xpath(
			"//div[@class='cutsheet-section cutsheet-section-details collapsed']").click()
	except:
		pass

	soup = BeautifulSoup(driver.page_source, "lxml")
	sleep(2)

	details_div = soup.find("div", {"class": "cutsheet-detail-wrap striped"})
	items = details_div.find_all("div", {"class": "cutsheet-detail-item"})

	for item in items:
		label = item.find_all("div")[0].text.strip()
		if "age" in label.lower():
			continue
		if label in detail_columns:
			data[label].append(item.find_all("div")[1].text.strip())

	driver.find_element_by_xpath("//button[@class='local-close']").click()
	driver.find_element_by_xpath("//input[@name='omnibox']").clear()

	for col in detail_columns:
		keys = data.keys()
		if col in keys:
			data_to_add.extend(data[col])
		else:
			data_to_add.append(None)

	ws.append(data_to_add)
	wb.save("viewpoint_ca3.xlsx")
