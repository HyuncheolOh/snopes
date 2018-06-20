#--------------------------------
# This program is for updating veracity values for missing which is None tuples
# Collect all veracity of missing entities and save
#--------------------------------
import scrapy
import MySQLdb

from snopes.items import SnopesItem

def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

def sql_close(cursor, conn):
    cursor.close()
    conn.close()

def get_urls():
    urls = []
    conn, cursor, = sql_connect()

    sql = """
        SELECT post_id, url
        FROM snopes_set
        WHERE published_date >= '2018-06-01'
        """
    cursor.execute(sql)
    rs = cursor.fetchall()
    for i, item in enumerate(rs):
        postid, url ,= item
        urls.append(url)
    return urls
        
class MmlabSpider(scrapy.Spider):
    name = "sharecount_update"
    allowed_domains = ["snopes.com"]
    start_urls = get_urls()

    def parse(self, response):
        url = response.xpath('//meta[@property="og:url"]/@content').extract_first()

        #share_count = response.xpath('//div[@class="share-controls-item numbers share-count"]/text()').extract()[1].strip()
        share_count = "0"
        yield {"url": url,  "share_count" : share_count}




