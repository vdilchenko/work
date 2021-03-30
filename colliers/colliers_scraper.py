from bs4 import BeautifulSoup
from selenium import webdriver
import lxml
from openpyxl import Workbook
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

def write_to_excel(ws, data):
	ws.append(data)
	return ws


driver = webdriver.Chrome("chromedriver")

start_url = [
	"https://www.collierscanada.com/fr-CA/Experts#&sort=%40lastz32xname%20ascending", 
	"https://www.collierscanada.com/fr-CA/Experts#first=%s&sort=%%40lastz32xname%%20ascending"]

wb = Workbook()
ws = wb.active
headers = ["Name", "Address", "Phone", "Email"]
ws.append(headers)

i = 0
while i <= 750:
	if i == 0:
		driver.get(start_url[0])
	else:
		driver.get(start_url[1] % str(i))

	sleep(5)
	soup = BeautifulSoup(driver.page_source, "lxml")
	boxes = soup.find_all("div", {"class": "coveo-list-layout CoveoResult"})
	for box in boxes:
		name = box.find("h3", {"class": "expert-card__name"}).find("a").text
		address = box.find("p", {"class": "expert-office"}).text
		try:
			phone = box.find_all("a", {"class": "expert__phone-text"})[0]["href"].replace("tel:", "")
		except IndexError:
			phone = None
		try:
			email = box.find_all("div", {
				"class": "expert-link"})[-1].find("a")["href"].replace("mailto:", "")
		except IndexError:
			email = None

		data = [name, address, phone, email]
		ws = write_to_excel(ws, data)
	wb.save("Collierscanada.xlsx")

	i += 30

driver.quit()