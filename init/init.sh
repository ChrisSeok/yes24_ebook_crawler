#!/bin/bash
#source /home1/ncloud/.profile
# ! 가상환경 실행
#conda: #source /opt/conda/bin/activate /가상환경 경로
#venv : #source 가상환경이름/bin/activate


mkdir -p log/$(date +"%Y-%m-%d")
log_path=log/$(date +"%Y-%m-%d")/ #앞에 공백 없도록



# ! 최초 도서 url 수집
python3 url_crawler.py 1>> ${log_path}init.log 2>> ${log_path}init.err.log

# ! url split
# split_urls.py의 출력을 init.log, 에러를 init.err.log에 저장
# > 는 overwrite, >> 는 append
python3 split_urls.py 10 1>> ${log_path}init.log 2>> ${log_path}init.err.log 


# # ! 크롤링
parallel -a split_urls.csv -j 5 python3 crawl_parallel.py 1>> ${log_path}init.log 2>> ${log_path}init.err.log

for f in ${log_path}init.log ${log_path}init.err.log; do echo -e "\n FINISHED [$(date +"%H:%M:%S")]" >> $f; done
