import sys
import pymysql
from datetime import date, timedelta
import csv
from time import sleep
from logger import *

name = "crawl.log"
log = logging.getLogger(name)

def main():

    today = date.today() #type: datetime.date
    try:
        # db연결
        db = pymysql.connect(
            host=#db server ip address here, 
            db="book", 
            user="book", 
            password="book!@34", 
            port=30000
        )
        urls = []
        with db:
            with db.cursor() as cursor:
                query = (
                    f"select url from book.yes24 where adult = 0 ;"  # yes24 테이블에서 성인도서 제외한 url 가져오기
                )
                cursor.execute(query)

                urls = cursor.fetchall()  # tuple

        urls = [u[0] for u in urls]
        print(urls)
        log.info(len(urls))
        c_l = str(len(urls))  #url 개수
        num = int(sys.argv[1]) #1번째 인자(입력) #url 나눌 개수
        print(c_l,"by", num)

        s_urls = []
        for i in range(len(urls) // num + 1):
            s_urls.append(urls[num * i : num * (i + 1)])
        # s_urls : list inside list
        with open("split_urls_update.csv", "w") as f:
            write = csv.writer(f)
            write.writerows(s_urls)
    except Exception as e:
        raise e
    return c_l


if __name__ == "__main__":

    error_count = 0
    while error_count <= 3:
        try:
            log.debug("start split urls")
            c_l = main()
            log.debug(f"{c_l} urls splited")
            break
        except Exception as e:

            error_count += 1
            if error_count > 2:
                log.error("error raise")
                log.debug(f"split urls make error", e)
                raise e
            sleep(60)
            continue
    log.info("done")
