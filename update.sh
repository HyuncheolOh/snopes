#!/bin/sh

while true; 

do 
	
	cd ./crawler/snopes

	echo "remove old data file"
	rm data_new.json
	rm snopes_sharecount.json
	sleep 1

	echo "update sharecount of Snopes.com articles"
	sleep 1
	scrapy crawl sharecount_update -o snopes_sharecount.json

	cd ../../
	
	cd database
	rm snopes_sharecount.json

	cp ../crawler/snopes/snopes_sharecount.json ./snopes_sharecount.json
	python update_sharecount.py
    	
	timestamp=`date +%Y%m%d%H%M`
	echo "$timestamp"
	echo "done"

	cd ..

	#repeat update per day
	sleep 86400
done
