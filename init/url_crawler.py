# -*- coding: utf-8 -*-
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
#driver.quit처리 > paper >crawl_parallel 소스 참고 

# log = logging.getLogger()
# log_Format = "%(levelname)s %(asctime)s - %(message)s"
# logging.basicConfig(filename = "url_logfile.log",
#                     filemode = "a",
#                     format = log_Format, 
#                     level = logging.DEBUG)
name = "crawl.log"
log = logging.getLogger(name)
logging.basicConfig(level = logging.INFO)


class UrlCrawler:

    def __init__(self):
        # self.executable_path = "/home/jupyter-coseok/web-scraping/web-scraper/yes24-ebook/driver/chromedriver"
        self.executable_path = "/driver/chromedriver"
        self.host = "192.168.10.100"
        self.port = 30000
        self.database = "book"
        self.username = "book"
        self.password = "book!@34"
        
    def get_Category(self):
        print("---------Start url_crawler---------")
        driver = webdriver.Chrome(
            executable_path=self.executable_path, chrome_options=self.chrome_option_setting()
        )

        genrelist = []
        category = []

        #get genre url
        ebook_url = "http://www.yes24.com/Mall/Main/eBook/017?CategoryNumber=017" #ebook 메인 페이지
        driver.get(ebook_url)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        # selector
        gen_items = soup.select("#mCateLi > li.cate2d > a")
        for item in gen_items:
            genre_url = item['href']
            genrelist.append(genre_url)

        # 크레마, eBook 대량/법인 등은 제외
        genrelist = genrelist[:-2]

        #get category url
        for genurl in genrelist:
            try: 
                driver.get(genurl)
            except:
                log.error(f'failed to get url at {genurl}')
                driver.quit()
                driver = webdriver.Chrome(executable_path=chromedriver_executable_path, options=options)
                continue


            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            # selector
            cat_items = soup.select("#cateSubListWrap > dl > dt > a")

            for item in cat_items:
                category_url = item['href']
                #만화-성인(구조 한 단계 더 있을 때)
                if (category_url == "/24/Category/Display/017001038022"):
                    driver.get("http://www.yes24.com/24/Category/Display/017001038022")
                    html = driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')
                    layer_cat_items = soup.select("#cateSubListWrap > dl > dt > a")
                    for items in layer_cat_items:
                        cat_url = items['href']
                        cat_detail_url = "http://www.yes24.com" + cat_url+ "?FetchSize=200"
                        category.append(cat_detail_url)

                else:
                    category_detail_url = "http://www.yes24.com" + category_url+ "?FetchSize=200"
                    category.append(category_detail_url)



        print(f"세부 카테고리 총 개수: {len(category)}")
        return category

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

    def get_last_pagenum(self, cateurl):
        driver = webdriver.Chrome(
            executable_path=self.executable_path, chrome_options=self.chrome_option_setting()
        )
        try:
            driver.get(cateurl)
        except:
            log.error('failed get url in get_last_pagenum')
            driver.quit()
            driver = webdriver.Chrome(executable_path=chromedriver_executable_path, options=options)    

        try:
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "category_layout")))

        except TimeoutException as e:
            log.error("TimeoutException error occurred in get_last_pagenum")
            log.error('%s',e)    #logging is optimized to use %s formatting
            self.insert_failed_db(cateurl)
        
        html = driver.page_source
        page_source = BeautifulSoup(html, "html.parser")
        html_selector = page_source.select(   #html_selector:  pagenumber바의 html 소스 전체(처음,다음,끝) 
            "#cateSubWrap > div.cateSubRgt > div > div.cCont_sortBot > span.cCont_sortLft > div > a.bgYUI.end"
        )

        if len(html_selector)==0:
            result = None
        else:
            html_end = html_selector[-1]
            parsed = urlparse.urlparse(html_end["href"])
            result = parse_qs(parsed.query)["PageNumber"] # ['21']  type list
            result = int(result[0])
            print("last page num:",result)
        return result

    def get_book_url(self, caturl): #url : 카테고리 url
        log.debug("----Start Crawling----")

        last_num = self.get_last_pagenum(caturl)
        print(f'{caturl}, {last_num}')

        if last_num == None:
            print("last page is None")
            return 
        else:
            caturl = caturl + "&PageNumber="
            #페이지 처음부터 끝까지
            for i in tqdm(range(last_num)):
                page = i + 1
                driver = webdriver.Chrome(
                    executable_path=self.executable_path,
                    chrome_options=self.chrome_option_setting(),
                )
        # #         # try:
                get_url = caturl + str(page)
                
                try: 
                    driver.get(get_url)
                except Exception as e:
                    driver.quit()
                    driver = webdriver.Chrome(
                        executable_path=executablepath,
                        chrome_options=options,
                    )
                    # continue 
                try:
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.ID, "category_layout"))
                        # categoryElemCenter
                    )
                except TimeoutException as e:
                    log.error("TimeoutException error occurred in get_book_url")
                    log.error('%s',e)    #logging is optimized to use %s formatting
                    self.insert_failed_db(geturl,page)
                    # continue

                html = driver.page_source
                page_source = BeautifulSoup(html, "html.parser")
                # 기본 도서 리스트 구조
                items = page_source.select(
                    "#category_layout > ul > li > div > div.goods_info > div.goods_name > a.bgYUI.ico_nWin"
                )
                # 카드형 도서 리스트 구조
                if len(items) == 0:
                    items = page_source.select(
                        "#category_layout > div.cCont_thumbLi > ul > li > div > div > div.goods_name > a"
                    )

                for item in items:
                    data = "http://www.yes24.com" + item["href"]
                    # db에 insert
                    try:
                        # print(data)
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
                query = (
                    "INSERT INTO book.yes24_url_new (book_url) VALUES (%s)"
                )
                # 필드 속성이 Unique 아닐경우
                # select_query = "select * from book.yes24 where url=%s"
                #     try:
                #         cursor.execute(select_query)
                #         result = cursor.fetchall()
                #         # ! url 중복되는 데이터는 입력 안함
                #         if len(result) != 0:
                #             pass
                #         else:

                # 필드 속성을 Unique로 설정(중복값X)
                try:
                    cursor.execute(query, url)
                    db.commit()
                #중복키 에러
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


    # 루프로 카테고리마다.
    def crawler(self):
        catelist = self.get_Category()
        print(f'카테고리{len(catelist)} 개 스크래핑')
        for i in range(len(catelist)):
            try:
                print(f'{i+1}번째 카테고리')
                self.get_book_url(catelist[i])
            except:
                continue


if __name__ == "__main__":
  
    get_url = UrlCrawler()
    get_url.crawler()
