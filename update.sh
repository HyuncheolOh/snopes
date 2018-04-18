#!/bin/sh

while true; 

do 
	
	cd ./crawler/snopes

	echo "remove old data file"
	rm data_new.json
	rm snopes_update.json
	sleep 1

	echo "update sharecount of Snopes.com articles"
	sleep 1
	cd ../crawler/snopes
	scrapy crawl sharecount_update -o snopes_update.json

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
