#!/bin/sh

while true; 

do 
	cd ./crawler/snopes
	#remove old files
	echo "remove old data file"
	rm data_new.json
	rm snopes_sharecount.json
	sleep 1
	echo "crawl snopes news until 5 pages"
	sleep 1
	scrapy crawl snopes_new -o data_new.json
	cd ../..
	#copy file to database location
	cd database
	rm data_new.json
	cp ../crawler/snopes/data_new.json data_new.json
	echo "update database if updated news exists"
	sleep 1
	python insert_data.py data_new.json

	cd ../
	echo "update sharecount of Snopes.com articles"
	sleep 1
	cd ./crawler/snopes
	scrapy crawl sharecount_update -o snopes_sharecount.json

	cd ../../
	cd database

	cp ../crawler/snopes/snopes_sharecount.json ./snopes_sharecount.json
	python update_sharecount.py
	timestamp=`date +%Y%m%d%H%M`
	echo "$timestamp"
	echo "done"

	cd ..
	#repeat update per day
	sleep 86400
	pwd

done
