#!/bin/bash
#source /home1/ncloud/.profile
# ! 가상환경 실행
#conda: #source /opt/conda/bin/activate /가상환경 경로
#venv : #source 가상환경이름/bin/activate

mkdir -p log/$(date +"%Y-%m-%d")
log_path=log/$(date +"%Y-%m-%d")/ #앞에 공백 없도록



# 신간도서 url 수집
python3 yes24_newBook_list.py 1>> ${log_path}new.log 2>> ${log_path}new.err.log


# ! url split
python3 split_urls.py 10 1>> ${log_path}new.log 2>> ${log_path}new.err.log 

# ! 크롤링
parallel -a split_urls.csv -j 5 python3 crawl_parallel.py 1>> ${log_path}new.log 2>> ${log_path}new.err.log

for f in ${log_path}new.log ${log_path}new.err.log; do echo -e "\n FINISHED [$(date +"%H:%M:%S")]" >> $f; done