# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
tor_proxy = "127.0.0.1:9050"
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--test-type")
options.add_argument("--allow-insecure-localhost")  #
options.add_argument("--disable-dev-shm-usage")  #
options.add_argument("acceptInsecureCerts")  #
options.add_argument("--disable-extensions")
options.add_argument("--ignore-certificate-errors")
options.add_argument("disable-infobars")
options.add_argument("--incognito")
options.add_argument("--proxy-server=socks5://%s" % tor_proxy)
executablepath = "/driver/chromedriver"

driver = webdriver.Chrome(executable_path=executablepath, options=options)


url = 'http://icanhazip.com/'
driver.get(url)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
text = soup.get_text()
print(text)
  



