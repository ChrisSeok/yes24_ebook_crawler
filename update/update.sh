#!/bin/bash
#source /home1/ncloud/.profile
# ! 가상환경 실행
#conda: #source /opt/conda/bin/activate /가상환경 경로
#venv : #source 가상환경이름/bin/activate

mkdir -p log/$(date +"%Y-%m-%d")
log_path=log/$(date +"%Y-%m-%d")/ #앞에 공백 없도록



# ! url split
python3 split_update_urls.py 10 1>> ${log_path}update.log 2>> ${log_path}update.err.log


# ! Update
parallel -a split_urls_update.csv -j 5 python3 crawl_update.py 1>> ${log_path}update.log 2>> ${log_path}update.err.log

for f in ${log_path}update.log ${log_path}update.err.log; do echo -e "\n FINISHED [$(date +"%H:%M:%S")]" >> $f; done
