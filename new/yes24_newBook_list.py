# -*- coding: utf-8 -*-
#신간도서url 수집모듈
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import pymysql
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.alert import Alert
# from insert_data import InsertData
from tqdm import tqdm
import pandas as pd
import csv
import urllib.parse as urlparse
from urllib.parse import parse_qs
import logging
#driver.quit처리 > paper >crawl_parallel 소스 보고 참고 

name = "crawl.log"
log = logging.getLogger(name)
logging.basicConfig(level = logging.INFO)

print("----Start Newbook Crawling----")


class NewUrlCrawler:

    def __init__(self):
        # self.executable_path = "/home/jupyter-coseok/web-scraping/web-scraper/yes24-ebook/driver/chromedriver"
        self.executable_path = "/driver/chromedriver"
        self.host = "192.168.10.100"
        self.port = 30000
        self.database = "book"
        self.username = "book"
        self.password = "book!@34"
        
    
    def chrome_option_setting(self):
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
        return options


    def get_last_pagenum(self, newbookurl):
        driver = webdriver.Chrome(
            executable_path=self.executable_path, chrome_options=self.chrome_option_setting()
        )
        try:
            driver.get(newbookurl)
        except:
            log.error('failed get url in get_last_pagenum')
            driver.quit()
            # driver = webdriver.Chrome(executable_path=chromedriver_executable_path, options=options)    

        try:
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "category_layout")))

        except TimeoutException as e:
            log.error("TimeoutException error occurred in get_last_pagenum. Run again.")
            log.error('%s',e)    #logging is optimized to use %s formatting
            self.insert_failed_db(newbookurl)
        
        html = driver.page_source
        page_source = BeautifulSoup(html, "html.parser")
        html_selector = page_source.select(          #html_selector:  pagenumber바의 html 소스 전체(처음,다음,끝) 
        "#categoryElemCenter > div:nth-child(4) > div.bosSortTop > div.sortLft > p > a"
        )
       
        if len(html_selector)==0:
            result = None
        else:
            html_end = html_selector[-1] # '끝'
            parsed = urlparse.urlparse(html_end["href"])
            result = parse_qs(parsed.query)["PageNumber"] # ['21']  type list
            result = int(result[0])
            print("last page num:",result)
        return result

    def get_book_url(self, newurl): #url : 카테고리 url

        last_num = self.get_last_pagenum(newurl)
        
        if last_num == None:
            print("last page is None")
            return 
        else:
            newurl = newurl + "&PageNumber="
            #페이지 처음부터 끝까지
            for i in tqdm(range(last_num)):
                page = i + 1
                driver = webdriver.Chrome(
                    executable_path=self.executable_path,
                    chrome_options=self.chrome_option_setting(),
                )
        # #         # try:
                get_url = newurl + str(page)
                driver.get(get_url)
                try:
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.ID, "category_layout"))
                        # categoryElemCenter
                    )
                except TimeoutException as e:
                    log.error("TimeoutException error occurred in get_book_url")
                    log.error('%s',e)    #logging is optimized to use %s formatting
                    self.insert_failed_db(geturl,page)
                    

                html = driver.page_source
                page_source = BeautifulSoup(html, "html.parser")
                items = page_source.select(
                    "#category_layout > tbody > tr > td.goodsTxtInfo > p:nth-child(1) > a:nth-child(1)"
                )

                # 카드형 도서 리스트 구조
                # if len(items) == 0:
                #     items = page_source.select(
                #         "#category_layout > div.cCont_thumbLi > ul > li > div > div > div.goods_name > a"
                #     )

                for item in items:
                    data = "http://www.yes24.com" + item["href"]
                    # db에 insert
                    try:
                        self.insert_url_db(data)
                    except Exception as e:
                        print("error in inserting url:",e)
                        self.insert_failed_db(geturl,page)
                        continue



    def insert_url_db(self, url):

        db = pymysql.connect(   
            host= self.host,
            user= self.username,
            passwd= self.password,
            db= self.database,
            port= self.port,
            use_unicode=True,
            charset="utf8",
            cursorclass=pymysql.cursors.DictCursor,
        )

        with db:
            with db.cursor(pymysql.cursors.DictCursor) as cursor:
                # weight 제외 25개
                query = (
                    "INSERT INTO book.yes24_url (book_url) VALUES (%s)"
                )

                # 필드 속성을 Unique로 설정(중복값X)
                try:
                    cursor.execute(query, url)
                    db.commit()
                #중복키 에러만 잡기
                except pymysql.err.IntegrityError as e: 
                    log.error("Duplicated key in insert_url_db. Pass.")

    def insert_failed_db(self, caturl, page=None):

        db = pymysql.connect(   
            host= self.host,
            user= self.username,
            passwd= self.password,
            db= self.database,
            port= self.port,
            use_unicode=True,
            charset="utf8",
            cursorclass=pymysql.cursors.DictCursor,
        )

        with db:
            with db.cursor(pymysql.cursors.DictCursor) as cursor:
                # weight 제외 25개
                query = (
                    "INSERT INTO book.failedpage (category_url,page) VALUES (%s, %s)"
                )

                try:
                    cursor.execute(query, (caturl,page))
                    db.commit()
                #중복키 에러만 잡기
                except pymysql.err.IntegrityError as e: 
                    log.error("Duplicated key in insert_failed_db. Pass.")

    # 카테고리마다 돌린다
    def newbook_crawler(self):
            newbook_page = 'http://www.yes24.com/24/category/newproductlist/017?sumgb=04&fetchsize=200' #ebook 신간도서 페이지
            print("-----------Start yes24_newBook_list-----------")
            self.get_book_url(newbook_page)
            


if __name__ == "__main__":
  
    get_url = NewUrlCrawler()
    get_url.newbook_crawler()
