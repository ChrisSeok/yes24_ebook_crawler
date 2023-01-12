# -*- coding: utf-8 -*-
#yes24 DB 필드 업데이트. 
# executable path, db conncection info > should be made more reusable
from lib2to3.pgen2.pgen import DFAState
from bs4 import BeautifulSoup
from datetime import datetime
import time
import pandas as pd
import sys
from datetime import datetime
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
from insert_data import InsertData 
import csv
import time
import pymysql
from logger import *

name = "crawl.log"
log = logging.getLogger(name)
logging.basicConfig(level = logging.DEBUG)

def crawlUpdate(urls, options): #urls: 리스트 #url from yes24 db
    # executablepath = "/home/jupyter-coseok/web-scraping/web-scraper/yes24-ebook/driver/chromedriver"
    executablepath = "/driver/chromedriver"

    data = pd.DataFrame(columns = ['cover', 'title', 'subtitle', 'author', 'publisher',
                    'publisher_date', 'rating', 'review_num', 'best1', 'best2',
                    'salespoint', 'ISBN13', 'ISBN10', 'pages', 'size',
                    'category', 'awards', 'introduce', 'toc', 'into_the_book',
                    'review', 'series', 'url', 'type', 'adult'])

    log.info("-------Start info Scraping-------")
    #for 개별도서
    for url in urls:
        # url = url.strip('"')
        # print("url after strip: ",url)
        try:
            if url[-1]=='\r':
                new_url = url[:-1]
                print('stripped \r :',new_url)
                host = #db server ip address here
                port = 30000
                database = "book"
                username = "book"
                password = "book!@34"
                db = pymysql.connect(   
                            host=host,
                            user=username,
                            passwd=password,
                            db=database,
                            port=port,
                            use_unicode=True,
                            charset="utf8",
                            cursorclass=pymysql.cursors.DictCursor,
                        )
                with db:
                    with db.cursor(pymysql.cursors.DictCursor) as cursor:
                        query = ("UPDATE book.yes24 SET url=%s WHERE url=%s")  # default => 0
                        cursor.execute(query,(new_url,url))
                        db.commit()
                url = new_url
        except:
            pass

        print("######## url:",url)
        driver = webdriver.Chrome(executable_path=executablepath, options=options)

        contents = []
        try:
            driver.get(url)
            print("success get url")
        except:
            print("failed get url:",url)
            driver.quit()
            driver = webdriver.Chrome(
                executable_path=executablepath,
                chrome_options=options,
            )
            continue #for loop 다음

        try: 
            print(driver.current_url)
            print("printed current url")
        except Exception as e:
            print("cannot print current url")
        try:
            WebDriverWait(driver, 10).until(EC.alert_is_present())
            print("alert page")
            alert = driver.switch_to.alert
            print("switch to alert")
            alert.accept()
            print("accept")
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "btnLogin"))
            )
            print(driver.current_url)
            print("성인도서")
            contents =  ['',' ','','','','','','','','','','','','','','','','','','','','',url,1]
            adultdf = pd.DataFrame([contents],columns = ['cover', 'title', 'subtitle', 'author', 'publisher',
                'publisher_date', 'rating', 'review_num', 'best1', 'best2',
                'salespoint', 'ISBN13', 'ISBN10', 'pages', 'size',
                'category', 'awards', 'introduce', 'toc', 'into_the_book',
                'review', 'series', 'url','adult'])
            data = pd.concat([data,adultdf])
            print(data)
            continue
                
        except:
                try: #상세정보 로딩
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.ID, "infoset_specific"))
                    )
                except:#일반/성인 도서 오류
                    print("도서 오류")
                    print(time.strftime('%Y.%m.%d - %H:%M:%S'))
                    try: 
                        print(driver.current_url)
                        print("printed current url")
                        if driver.current_url =='https://secimage.yes24.com/sysimage/contents/notice/firewall.html?ipsFilterNumber=manual':
                            # driver.get(url)
                            html = driver.page_source
                            soup = BeautifulSoup(html, 'html.parser')
                            text = soup.select_one("#ip_address_area").get_text()
                            print("blocked IP:",text)
                    except Exception as e:
                        print("cannot print current url",e)
                        continue

        try:
            html = driver.page_source
            document = BeautifulSoup(html, "html.parser")
            print("success get html")
        except:
            print("failed get html")
            print(time.strftime('%Y.%m.%d - %H:%M:%S'))
            driver.quit()
            driver = webdriver.Chrome(executable_path=executablepath, options=options)
            continue

        try:
            print("---Begin Info Scraping---")

            # 표지
            try:
                tag_cover = document.select_one(
                    "#yDetailTopWrap > div.topColLft > div > span > em > img"
                ).get("src")
            except:
                tag_cover = ""

            # 제목
            try:
                tag_title = document.select_one(
                    "#yDetailTopWrap > div.topColRgt > div.gd_infoTop > div > h2"
                ).text
            except:
                continue

            # 부제
            try:
                tag_subTitle = document.select_one(
                    "#yDetailTopWrap > div.topColRgt > div.gd_infoTop > div > h3"
                ).get_text(strip=True)
            except:
                tag_subTitle = ""

            # 저자 옮긴이
            try:
                tag_author = ",".join(
                    [
                        n.text.split(":")[-1].split("(")[0].strip()
                        for n in document.select("div.author_name")
                    ]
                )
                if not tag_author:
                    tag_author = ",".join(
                        [
                            n.text.strip()
                            for n in document.select(
                                "#yDetailTopWrap > div.topColRgt > div.gd_infoTop > span.gd_pubArea > span.gd_auth"
                            )
                        ]
                    )
            except:
                tag_author = ""

            # 출판사 출판일
            try:
                tag_dateOfPublisher = "-".join(
                    [
                        d[:-1]
                        for d in document.select_one(
                            "#yDetailTopWrap > div.topColRgt > div.gd_infoTop > span.gd_pubArea > span.gd_date"
                        ).text.split()
                    ]
                )
                tag_publisher = document.select_one(
                    "#yDetailTopWrap > div.topColRgt > div.gd_infoTop > span.gd_pubArea > span.gd_pub > a"
                ).get_text(strip=True)
            except:
                tag_publisher = ""
                tag_dateOfPublisher = ""
            

            # 판매지수
            try:
                tag_salesPoint = (
                    document.select_one(
                        "#yDetailTopWrap > div.topColRgt > div.gd_infoTop > span.gd_ratingArea > span.gd_sellNum"
                    )
                    .get_text(separator="\n", strip=True)
                    .split("\n")[1][5:]
                    .replace(",", "")
                )
            except:
                tag_salesPoint = ''

            # 평점
            try:
                tag_GPA = document.select_one("#spanGdRating > a > em").get_text(strip=True)
            except:
                tag_GPA = ''
            # 리뷰수
            try:
                tag_reviewCount = document.select_one(
                    "#yDetailTopWrap > div.topColRgt > div.gd_infoTop > span.gd_ratingArea > span.gd_reviewCount > a > em"
                ).get_text(strip=True)
            except:
                tag_reviewCount = ''

            # 주간
            try:
                tag_Best = document.select_one(
                    "#yDetailTopWrap > div.topColRgt > div.gd_infoTop > span.gd_ratingArea > span.gd_best > dl > dd > a"
                ).get_text(strip=True)
            except:
                tag_Best = ""
            # top
            try:
                tag_Best2 = (
                    document.select_one(
                        "#yDetailTopWrap > div.topColRgt > div.gd_infoTop > span.gd_ratingArea > span.gd_best > dl > dd > a"
                    )
                    .get_text(separator="\n", strip=True)
                    .split("\n")[-1]
                )
            except:
                tag_Best2 = ""

            """
            # 키워드 픽
            try:
                tag_keywordPick = getKeywordPick(document)
                contents.append(tag_keywordPick)

            except:
                tag_keywordPick = ''
                contents.append(tag_keywordPick)
            """
            # isbn, 쪽수, 크기, 19
            try:
                tag_ISBN13 = (
                    document.find_all("th", string="ISBN13")[0]
                    .parent.select_one("td.txt.lastCol")
                    .text
                )
            except:
                tag_ISBN13 = ""
            try:
                tag_ISBN10 = (
                    document.find_all("th", string="ISBN10")[0]
                    .parent.select_one("td.txt.lastCol")
                    .text
                )
            except:
                tag_ISBN10 = ""

            tag_numberOfPage = ''
            tag_size = ""
            # tag_weight = ""
            try:
                for l in (
                    document.find_all("th", string="쪽수, 무게, 크기")[0]
                    .parent.select_one("td.txt.lastCol")
                    .text.split("|")
                ):
                    if l.find("쪽") != -1:
                        tag_numberOfPage = l.strip()
                    elif l.find("mm") != -1:
                        tag_size = l.strip()
                    elif l.find("g") != -1:
                        tag_weight = l.strip()
            except:
                tag_numberOfPage = ""
                tag_size = ""
                tag_weight = ""
            try:
                tag_19 = (
                    document.find_all("th", string="연령제한")[0]
                    .parent.select_one("td.txt.lastCol")
                    .text
                )
                tag_19 = 1
            except:
                tag_19 = 0

            # print("tag_19:",tag_19)


            # 카테고리
            try:
                tag_category = "||".join(
                    [
                        ">".join([a.text.strip() for a in l.select("a")])
                        for l in document.find("dt", string="카테고리 분류").parent.select(
                            "dd > ul > li"
                        )
                    ]
                )
            except:
                tag_category

            # 수상내역
            try:
                tag_bookAward = "||".join(
                    [
                        ">".join([a.text.strip() for a in l.select("a")])
                        for l in document.find("dt", string="수상내역 및 미디어 추천 분류").parent.select(
                            "dd > ul > li"
                        )
                    ]
                )
            except:
                tag_bookAward = ""

            # 주제어
            # try:
            #     tag_topicKeyword = ",".join(
            #         [
            #             s.get_text(strip=True)
            #             for s in document.select(
            #                 "#infoset_goodsCate > div.infoSetCont_wrap > dl.yesAlertDl > dd.tagArea > span > a"
            #             )
            #         ]
            #     )

            # except:
            #     tag_topicKeyword = ""

            # 책소개
            try:
                tag_bookIntroduce = (
                    document.select_one("#infoset_introduce .txtContentText")
                    .get_text(separator="\n", strip=True)
                    .replace("<b>", "\n")
                    .replace("</b>", "\n")
                    .replace("<br/>", "\n")
                )
            except:
                tag_bookIntroduce = ""

            # 목차
            try:
                tag_bookTOC = (
                    document.select_one(
                        "#infoset_toc > div.infoSetCont_wrap > div.infoWrap_txt > textarea"
                    )
                    .get_text(separator="\n", strip=True)
                    .replace("<b>", "\n")
                    .replace("</b>", "\n")
                    .replace("<br/>", "\n")
                )
            except:
                tag_bookTOC = ""

            # 책속으로
            try:
                tag_inaBook = (
                    document.select_one(
                        "#infoset_inBook > div.infoSetCont_wrap > div.infoWrap_txt > div.infoWrap_txtInner > textarea"
                    )
                    .get_text(separator="\n", strip=True)
                    .replace("<b>", "\n")
                    .replace("</b>", "\n")
                    .replace("<br/>", "\n")
                )
            except:
                tag_inaBook = ""

            # 출판사 서평
            try:
                tag_bookPublishReview = document.select_one(
                    "#infoset_pubReivew > div.infoSetCont_wrap > div.infoWrap_txt"
                ).get_text(separator="\n", strip=True)
            except:
                tag_bookPublishReview = ""
            # 시리즈정보
            try:
                tag_bookSeries = "||".join(
                    [
                        s.get_text(strip=True)
                        for s in document.select("li > div > div > p.goods_name > a")
                    ]
                )
            except:
                tag_bookSeries = ""


            contents.append(tag_cover)
            contents.append(tag_title)
            contents.append(tag_subTitle)
            contents.append(tag_author)
            contents.append(tag_publisher)
            contents.append(tag_dateOfPublisher)
            contents.append(tag_GPA) #rating
            contents.append(tag_reviewCount)
            contents.append(tag_Best)
            contents.append(tag_Best2)
            contents.append(tag_salesPoint) 
            contents.append(tag_ISBN13)
            contents.append(tag_ISBN10)
            contents.append(tag_numberOfPage)
            contents.append(tag_size)
            contents.append(tag_category)
            # contents.append(tag_weight)
            contents.append(tag_bookAward)
            contents.append(tag_bookIntroduce)
            contents.append(tag_bookTOC)
            contents.append(tag_inaBook)
            contents.append(tag_bookPublishReview)
            contents.append(tag_bookSeries)
            contents.append(url)
            # contents.append(tag_topicKeyword)
            contents.append(tag_19)
            # print("contents:",contents)
            contentdf = pd.DataFrame([contents],columns = ['cover', 'title', 'subtitle', 'author', 'publisher',
                        'publisher_date', 'rating', 'review_num', 'best1', 'best2',
                        'salespoint', 'ISBN13', 'ISBN10', 'pages', 'size',
                        'category', 'awards', 'introduce', 'toc', 'into_the_book',
                        'review', 'series', 'url', 'adult'])
            data = pd.concat([data,contentdf])
            print(data)

        except UnexpectedAlertPresentException:
            log.error("UnexpectedAlertPresentException")
            print(url)
            driver.quit()
            print(url)
            failed.append(url)
            driver = webdriver.Chrome(
                executable_path=executable_path,
                chrome_options=options,
            )
            continue

        except Exception as ex:
            print(ex)
            print(url)
            driver.quit()
            driver = webdriver.Chrome(
                # executable_path=chromedriver_executable_path, options=options
                executable_path=executable_path,
                chrome_options=options,
            )
            continue

    driver.quit()
    return data


if __name__ == "__main__":

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

    print("-----------Start crawl_update-----------")

    log.info("crawler setting")
    all_urls = sys.argv[1]
    log.info(f'{all_urls}')
    urls = all_urls.split(",")
    urls[-1]=urls[-1].strip('\r')
    log.info(f'{urls}')
    data = crawlUpdate(urls, options)
    print("data:",data)


    if len(data.index) == 0:
        print("No crawled data")
        pass
    else:
        try:
            print("insert df data")
            Insert = InsertData(data)
            dataset = Insert.preprocess_data()
            # pd.set_option('display.max_rows', None)
            print("dataset:",dataset)
            Insert.update(dataset)
            print("update 완료")

        except Exception as e:
            print("Update db failed ",e)



