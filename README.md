# Yes24 ebook 크롤러

yes24 ebook의 url, 도서정보 스크래핑<br>
설치 및 실행가이드: Install_Guide.md


# Release Notes
- [0.1] 2022-11-21
    - 신간도서 url 수집 모듈 개발 
    - 도서 url, 상세정보 수집 후 db에 저장하도록 모듈 수정
    - 도서 상세정보 업데이트 모듈 개발
    - README.md, 사용자가이드.md 작성



# directory tree
```	
📦yes24-ebook
 ┣ 📂driver
 ┃ ┣ 📜chromedriver
 ┣ 📂init
 ┃ ┣ 📂log
 ┃ ┃ ┗ 📂yyyy-mm-dd
 ┃ ┃ ┃ ┣ 📜init.err.log
 ┃ ┃ ┃ ┗ 📜init.log
 ┃ ┣ 📜init.sh
 ┃ ┣ 📜url_crawler.py
 ┃ ┣ 📜split_urls.py
 ┃ ┣ 📜crawl_parallel.py
 ┃ ┗ 📜insert_data.py
 ┣ 📂new
 ┃ ┣ 📂log
 ┃ ┃ ┗ 📂yyyy-mm-dd
 ┃ ┃ ┃ ┣ 📜new.err.log
 ┃ ┃ ┃ ┗ 📜new.log
 ┃ ┣ 📜new.sh
 ┃ ┣ 📜yes24_newBook_list.py
 ┃ ┣ 📜split_urls.py
 ┃ ┣ 📜crawl_parallel.py
 ┃ ┗ 📜insert_data.py
 ┣ 📂update
 ┃ ┣ 📂log
 ┃ ┃ ┗ 📂yyyy-mm-dd
 ┃ ┃ ┃ ┣ 📜update.err.log
 ┃ ┃ ┃ ┗ 📜update.log
 ┃ ┣ 📜update.sh
 ┃ ┣ 📜split_update_urls.py
 ┃ ┣ 📜crawl_update.py
 ┃ ┗ 📜insert_data.py
 ┣ 📜README.md
 ┣ 📜사용자가이드.md
 ┣ 📜requirements.txt
 ┗ 📜tor_test.py

```	

- driver 폴더
    - 구글 크롬 드라이버(version. 107.0.5304.62)
- split_update_urls.py
    - DB의 yes24 테이블에서 adult필드가 0인 ebook url을 가져오고 n개 단위로 분리
    - output : split_urls_update.csv
- crawl_update.py
    - 도서 상세정보 업데이트 모듈
    - 토르 브라우저 사용
    - gnu parallel로 병렬처리
    - DB의 yes24 테이블의 도서정보 update
- crawl_parallel.py
    - 도서 상세정보 수집 모듈
    - 토르 브라우저 사용
    - gnu parallel로 병렬처리
    - DB의 yes24 테이블에 도서정보 Insert, yes24_url 테이블의 complete 필드 1로 Update
- insert_data.py
    - 크롤링 완료된 도서 데이터 preprocessing, DB의 yes24 테이블에 입력/업데이트
- split_urls.py
    - DB의 yes24_url 테이블에서 ebook url을 가져오고 n개 단위로 분리
    - output : split_urls.csv
- tor_test.py
    - tor 브라우저가 작동하는지 확인: 우회 ip 출력
- yes24_newBook_list.py
    - ebook 신간도서 url 크롤러
    - 토르 브라우저 사용안함
    - DB의 yes24_url 테이블에 수집한 도서 url Insert
    - 수집 못한 url/페이지 있을 경우 DB의 failedpage 테이블에 신간도서 홈페이지 url, 페이지 수 Insert
- url_crawler.py
    - ebook url 크롤러
    - 토르 브라우저 사용안함
    - 일반적인 도서 리스트 목록 확인 후 카드형 도서 리스트 목록 확인
    - DB의 yes24_url 테이블에 수집한 도서 url Insert
    - DB의 failedpage 테이블에 수집 못한 카테고리url(+ 페이지 수) Insert
- init.sh
    - 가상환경 설정(필요시)
    - log 폴더 생성
    - url_crawler.py , split_urls.py, crawl_parallel.py로 구성
    - nohup으로 실행
    - 로그파일 init.log, init.err.log 생성
        - init.log
            - url_crawler.py 실행후 각 카테고리의 마지막 페이지 수 표시, 프로세스바로 url 크롤링 진행상황 표시
            - split_urls.py 실행후 db에서 가져온 url 개수, csv파일의 한 행에 들어갈 url 개수 표시
            - crawl_parallel.py 실행후 도서의 url, 성인도서 여부, 크롤링 된 데이터, exception 메세지 등 표시
        - init.err.log : 에러메세지
- new.sh
    - 가상환경 설정(필요시)
    - log 폴더 생성
    - yes24_newBook_list.py, split_urls.py, crawl_parallel.py로 구성
    - crontab에 등록(사용자가이드 참고)
    - 로그파일 new.log, new.err.log 생성
        - new.log
            - yes24_newBook_list.py 실행후 마지막 페이지 수 표시, 프로세스바로 진행상황 표시
            - split_urls.py 실행후 db에서 가져온 url 개수, csv파일의 한 행에 들어갈 url 개수 표시
            - crawl_parallel.py 실행후 도서의 url, 성인도서 여부, 크롤링 된 데이터, exception 메세지 등 표시
        - new.err.log : 에러메세지
- update.sh
    - 가상환경 설정(필요시)
    - log 폴더 생성
    - split_update_urls.py, crawl_update.py로 구성
    - 로그파일 update.log, update.err.log 생성
        - update.log 
            - split_urls.py 실행후 db에서 가져온 url 개수, csv파일의 한 행에 들어갈 url 개수 표시
            - crawl_Update.py 실행후 도서의 url, 크롤링 된 데이터, exception 메세지 등 표시
        - update.err.log : 에러메세지




<br><br>


# DB
<br>


<b>yes24_url</b>


|필드|내용|접근|
|------|---|---|
|book_url|도서 url (Unique)|url_crawler.py<br>yes24_newBook_list.py |
|complete|default=0,<br>해당 url이 크롤링 완료되면 1로 업데이트|crawl_parallel.py |
|created_at|해당 데이터 생성시의 시간|데이터 조회 시(workbench)|
|updated_at|해당 데이터 변경시의 시간|데이터 조회 시(workbench)|

<br><br>


<b>yes24</b>

|필드|내용|접근|
|------|---|---|
|url|도서 url (Unique)|crawl_parallel.py<br>crawl_Update.py|
|cover, title, ... ,adult|도서 상세 정보|crawl_parallel.py<br>crawl_Update.py|
|created_at|해당 데이터 생성시의 시간|데이터 조회 시(workbench)|
|updated_at|해당 데이터 변경시의 시간|데이터 조회 시(workbench)|

<br><br>

<b>failedpage</b>

|필드|내용|접근|
|------|---|---|
|category_url|수집 실패한 카테고리 url<br> (신간도서의 경우 ebook 신간도서 웹페이지 url)|url_crawler.py <br>yes24_newBook_list.py |
|page|실패한 페이지|url_crawler.py <br>yes24_newBook_list.py |



<br><br>

- backup_yes24 <br>
    -2022.11.11 yes24테이블 backup
<br><br>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
- backup_yes24_url <br>
    -2022.11.21 yes24_url 테이블 backup <br> 
