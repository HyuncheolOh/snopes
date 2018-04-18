#!/bin/sh

while true; 

do 
	cd ./crawler/snopes

	echo "remove old data file"
	rm data_new.json
	rm snopes_update.json
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


	echo "update sharecount of Snopes.com articles"
	sleep 1
	cd ../crawler/snopes
	scrapy crawl snopes_new -o snopes_update.json

	cd ../../
	cd database
	rm snopes_update.json

	cp ../crawler/snopes/snopes_update.json ./snopes_update.json
	python update_data.py
	timestamp=`date +%Y%m%d%H%M`
	echo "$timestamp"
	echo "done"

	cd ..

	#repeat update per day
	sleep 86400
done
