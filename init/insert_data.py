import pandas as pd
import pymysql
import time
from pymysql.err import IntegrityError

class InsertData:
    def __init__(self, df):
        super().__init__()
        self.dataset = df
        # self.df = pd.read_csv(path)
        self.host = "192.168.10.100"
        self.port = 30000
        self.database = "book"
        self.username = "book"
        self.password = "book!@34"

    def preprocess_data(self):
        dataset = self.dataset
        # dataset.drop(columns=["Unnamed: 0"], inplace=True)
        dataset.reset_index(drop=True, inplace=True)

        isbnl = []
        for isbn in dataset["ISBN13"]:
            isbn = str(isbn).split(".")[0].strip()
            if len(isbn) == 13:
                isbnl.append(isbn)
            else:
                isbnl.append("0")
        dataset["ISBN13"] = isbnl

        dataset.dropna(subset=["url"], inplace=True)
        dataset["title"] = dataset["title"].replace(r"\[[^\]]*YES24[^\]]*\]", "", regex=True)
        dataset["title"] = dataset["title"].replace(r"\[[^\]]*yes24[^\]]*\]", "", regex=True)
        dataset["title"] = dataset["title"].replace(r"\[[^\]]*예스24[^\]]*\]", "", regex=True)
        dataset["title"] = dataset["title"].replace(r"\[[^\]]*무료[^\]]*\]", "", regex=True)
        dataset["title"] = dataset["title"].replace(r"\[[^\]]*예스리커버[^\]]*\]", "", regex=True)
        dataset["title"] = dataset["title"].replace(r"\[[^\]]*대여[^\]]*\]", "", regex=True)
        dataset["title"] = dataset["title"].replace(r"\[[^\]]*연재[^\]]*\]", "", regex=True)

        # dataset["adult"].fillna(False, inplace=True) #tag_19 0 or 1로 설정 -> crawl_parallel.py 확인
        # dataset["rating"].fillna(0, inplace=True)
        # dataset["review_num"].fillna(0, inplace=True)
        # dataset["pages"].fillna(0, inplace=True)
        # dataset["salespoint"].fillna(0, inplace=True)
        # dataset["adult"] = [True if a != False else a for a in dataset["adult"]]

        dataset["rating"] = dataset["rating"].replace(r"", 0, regex=True)
        dataset["pages"] = dataset["pages"].replace(r"", 0, regex=True)
        dataset["review_num"] = dataset["review_num"].replace(r"", 0, regex=True)
        dataset["salespoint"] = dataset["salespoint"].replace(r"", 0, regex=True)
        
        dataset.fillna("", inplace=True)
        dataset.reset_index(drop=True, inplace=True)

        return dataset

    def insert(self, dataset): 
        cover = dataset["cover"] # pandas Series
        title = dataset["title"]
        subtitle = dataset["subtitle"]
        author = dataset["author"]
        publisher = dataset["publisher"]
        publisher_date = dataset["publisher_date"]
        yes24_rating = dataset["rating"]
        yes24_review_num = dataset["review_num"]
        yes24_best1 = dataset["best1"]
        yes24_best2 = dataset["best2"]
        yes24_sales_point = [int(i) for i in dataset["salespoint"]]
        isbn13 = dataset["ISBN13"]
        isbn10 = dataset["ISBN10"]

        try:
            number_of_page = [
                int(i[:-1].replace(",", "")) if i != "쪽수확인중" else 0 for i in dataset["pages"]
            ]
            number_of_page = [i if i < 30000 else 30000 for i in number_of_page]
        except:
            number_of_page = dataset["pages"]
        book_size = dataset["size"]
        try:
            book_category = [
                c if len(c.split("||")) <= 10 else "||".join(c.split("||")[:10])
                for c in dataset["category"]
            ]
        except:
            book_category = dataset["category"]

        award_detail = dataset["awards"]
        introduce = dataset["introduce"]
        toc = dataset["toc"]
        content_detail = dataset["into_the_book"]
        publisher_review = dataset["review"]
        series_info = dataset["series"]
        url = dataset["url"]
        book_adult = dataset["adult"]

        db = pymysql.connect(
            host=self.host,
            user=self.username,
            passwd=self.password,
            db=self.database,
            port=self.port,
            use_unicode=True,
            charset="utf8",
            cursorclass=pymysql.cursors.DictCursor,
        )

        with db:
            with db.cursor(pymysql.cursors.DictCursor) as cursor:
                # weight 제외 25개
                query = (
                    "INSERT INTO book.yes24 (cover, title, subtitle, author, publisher, "
                    "publisher_date, rating, review_num, best1, best2, "
                    "salespoint, ISBN13, ISBN10, pages, size, "
                    "category, awards, introduce, toc, into_the_book, "
                    "review, series, url, type, adult)"
                    "VALUES (%s, %s, %s, %s, %s, "
                    "%s, %s, %s, %s, %s, "
                    "%s, %s, %s, %s, %s, "
                    "%s, %s, %s, %s, %s, "
                    "%s, %s, %s, 'ebook', %s) "
                )

                # select_query = "select * from book.yes24 where url=%s" # select_query = "select * from book.yes24 where url=%s"
                update_complete = "UPDATE book.yes24_url SET complete=1 WHERE book_url=%s" # update_complete = "UPDATE book.yes24_url SET complete=1 WHERE book_url=%s"
                for i in range(len(dataset)):
                    try:
                        
                        data = (
                            cover[i],
                            title[i],
                            subtitle[i],
                            author[i],
                            publisher[i],
                            publisher_date[i],
                            yes24_rating[i],
                            yes24_review_num[i],
                            yes24_best1[i],
                            yes24_best2[i],
                            yes24_sales_point[i],
                            isbn13[i],
                            isbn10[i],
                            number_of_page[i],
                            book_size[i],
                            book_category[i],
                            award_detail[i],
                            introduce[i],
                            toc[i],
                            content_detail[i],
                            publisher_review[i],
                            series_info[i],
                            url[i],
                            book_adult[i],
                        )

                        try:
                            cursor.execute(query, data)
                            db.commit()

                        except IntegrityError as e: 
                            print("Duplicated key error in insert data.",url[i],"\nContinue.")
                            continue
                        try:
                            cursor.execute(update_complete, url[i])
                            db.commit()
                        except: 
                            print("error in setting complete to 1. Continue.")
                            continue
                    except Exception as e:
                        print("unknown error in inserting data:",e)
                        print(time.strftime('%Y.%m.%d - %H:%M:%S'))
                        continue
                    #필드 unique 설정, pymysql.err.IntegrityError exception처리하기
# qwe
    def update(self, dataset): 
        cover = dataset["cover"] # pandas Series
        title = dataset["title"]
        subtitle = dataset["subtitle"]
        author = dataset["author"]
        publisher = dataset["publisher"]
        publisher_date = dataset["publisher_date"]
        yes24_rating = dataset["rating"]
        yes24_review_num = dataset["review_num"]
        yes24_best1 = dataset["best1"]
        yes24_best2 = dataset["best2"]
        yes24_sales_point = [int(i) for i in dataset["salespoint"]]
        isbn13 = dataset["ISBN13"]
        isbn10 = dataset["ISBN10"]
        try:
            number_of_page = [
                int(i[:-1].replace(",", "")) if i != "쪽수확인중" else 0 for i in dataset["pages"]
            ]
            number_of_page = [i if i < 30000 else 30000 for i in number_of_page]
        except:
            number_of_page = dataset["pages"]
        book_size = dataset["size"]
        try:
            book_category = [
                c if len(c.split("||")) <= 10 else "||".join(c.split("||")[:10])
                for c in dataset["category"]
            ]
        except:
            book_category = dataset["category"]

        award_detail = dataset["awards"]
        introduce = dataset["introduce"]
        toc = dataset["toc"]
        content_detail = dataset["into_the_book"]
        publisher_review = dataset["review"]
        series_info = dataset["series"]
        url = dataset["url"]
        book_adult = dataset["adult"]

        db = pymysql.connect(
            host=self.host,
            user=self.username,
            passwd=self.password,
            db=self.database,
            port=self.port,
            use_unicode=True,
            charset="utf8",
            cursorclass=pymysql.cursors.DictCursor,
        )

        with db:
            with db.cursor(pymysql.cursors.DictCursor) as cursor:
                # weight 제외 25개
                query = (
                    "UPDATE book.yes24 SET cover=%s, title=%s, subtitle=%s, author=%s, publisher=%s, "
                    "publisher_date=%s, rating=%s, review_num=%s, best1=%s, best2=%s, "
                    "salespoint=%s, ISBN13=%s, ISBN10=%s, pages=%s, size=%s, "
                    "category=%s, awards=%s, introduce=%s, toc=%s, into_the_book=%s, "
                    "review=%s, series=%s, url=%s, type=%s, adult=%s"
                    "WHERE url = %s"
                ) 

                
                # select_query = "select * from book.yes24 where url=%s" # select_query = "select * from book.yes24 where url=%s"
                for i in range(len(dataset)):
                    try:
                        data = (
                            cover[i],
                            title[i],
                            subtitle[i],
                            author[i],
                            publisher[i],
                            publisher_date[i],
                            yes24_rating[i],
                            yes24_review_num[i],
                            yes24_best1[i],
                            yes24_best2[i],
                            yes24_sales_point[i],
                            isbn13[i],
                            isbn10[i],
                            number_of_page[i],
                            book_size[i],
                            book_category[i],
                            award_detail[i],
                            introduce[i],
                            toc[i],
                            content_detail[i],
                            publisher_review[i],
                            series_info[i],
                            url[i],
                            'ebook',
                            book_adult[i],
                            url[i]
                        )
                        try:
                            cursor.execute(query, data)
                            db.commit()
                            print("updated",i+1)
                        except Exception as e: 
                            print("error occurred in update:", e)
                            continue
                        
                    except Exception as e:
                        print("error in updating data before execution:",e)
                        print(time.strftime('%Y.%m.%d - %H:%M:%S'))
                        continue