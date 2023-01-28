from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
from time import sleep
from random import randint
import pandas as pd

'''
## this for github mode

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
from pyvirtualdisplay import Display

display = Display(visible=0, size=(800, 800))
display.start()
chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
chrome_options = webdriver.ChromeOptions()
options = [
    # Define window size here
    "--window-size=1200,1200",
    "--ignore-certificate-errors",
]
for option in options:
    chrome_options.add_argument(option)
driver = webdriver.Chrome(options=chrome_options)


# executable_path = "C:\webdriver\chromedriver.exe"
# driver = webdriver.Chrome(executable_path=executable_path)
'''


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller

import requests # 2
import json # 3

from pyvirtualdisplay import Display
display = Display(visible=0, size=(800, 800))  
display.start()

chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                      # and if it doesn't exist, download it automatically,
                                      # then add chromedriver to path

chrome_options = webdriver.ChromeOptions()    
# Add your options as needed    
options = [
  # Define window size here
   "--window-size=1200,1200",
    "--ignore-certificate-errors"
 
    #"--headless",
    #"--disable-gpu",
    #"--window-size=1920,1200",
    #"--ignore-certificate-errors",
    #"--disable-extensions",
    #"--no-sandbox",
    #"--disable-dev-shm-usage",
    #'--remote-debugging-port=9222'
]

for option in options:
    chrome_options.add_argument(option)

    
driver = webdriver.Chrome(options = chrome_options)



driver.get("https://www.realestate.moj.gov.kw/live/Moj_Rs_11.aspx")


def small_sleep(low=1, high=5):
    sleep(randint(low, high))


def large_sleep(low=1, high=10):
    sleep(randint(low, high))


def get_data(driver):
    data = {}
    elements = driver.find_elements(By.XPATH("//*"))
    for element in elements:
        if element.get_attribute("id"):
            data[element.get_attribute("id")] = element.get_attribute("value")
    return data


def check_button(driver, id):
    element = driver.find_element_by_id(id)
    if not element.is_selected():
        element.click()


def click_button(driver, id):
    element = driver.find_element(By.ID(id))
    element.click()


def get_beautiful_soup(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup


def get_table_data(driver):
    source = get_beautiful_soup(driver)
    table = source.find("table")
    table_body = table.find("tbody")
    rows = table_body.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])  # Get rid of empty values
    return True


# driver.find_element_by_link_text(“Testsigma Cloud”).click()

from_date = "5/1/2023"
to_date = "23/01/2023"

from_date_el = driver.find_element(By.ID, "bodyContent_fromDate")
from_date_el.send_keys(from_date)
small_sleep()
to_date_el = driver.find_element(By.ID, "bodyContent_tillDate")
to_date_el.send_keys(to_date)
small_sleep()
## click to main button
checked = False

if checked == False:
    driver.execute_script('document.getElementById("bodyContent_cbGov").click()')
    small_sleep()
    driver.execute_script('document.getElementById("bodyContent_cbZone").click()')
    small_sleep()
    driver.execute_script('document.getElementById("bodyContent_cbCat").click()')
    small_sleep()
    checked = True

if checked == True:
    driver.execute_script('document.getElementById("bodyContent_btnSubmit").click()')

source = get_beautiful_soup(driver)


data = []
for page_number in range(1, 3):
    driver.find_element(By.LINK_TEXT, str(page_number + 1)).click()
    # driver.execute_script(f"document.getElementsByTagName('a')[{page_number}].click()")
    large_sleep()
    get_table_data(driver)

df = pd.DataFrame(data=data)

df.to_csv("data.csv")
