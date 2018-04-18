#--------------------------------
# This program is for updating veracity values for missing which is None tuples
# Collect all veracity of missing entities and save
#--------------------------------
import scrapy
import MySQLdb
import re
from BeautifulSoup import BeautifulSoup
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
        FROM snopes
        """
    cursor.execute(sql)
    rs = cursor.fetchall()
    for i, item in enumerate(rs):
        postid, url ,= item
        urls.append(url)
    return urls

def trim(data):
    try :
        return data.replace("<em>", "").replace("</em>", "").replace("<br>","").replace("</br>", "")
    except TypeError as e:
        print(e, type(data), data)
        return ""

def get_sources(content):
    source_press_idx = 0
    regex = '[1-2][0-9][0-9][0-9].'

    left_quote = u"\u201c"
    right_quote = u"\u201d"
 
    if len(content) == 0:
        return "None"
    else :        
        source_list = []
        editor, title, date, press = ['','','','']
        for i, item in enumerate(content):
            soup = BeautifulSoup(item)
            if "<em>" in item:
                for p_content in soup.p.contents:
                    if left_quote in p_content:
                        editor = p_content.split(left_quote)[0]
                        title = p_content.split(left_quote)[1].replace(right_quote, "")
                    elif bool(re.search(regex, str(p_content))) == True:
                        date = p_content
                date = unicode(date) 
                press = soup.em.contents[0]
                source_list.append({"title": trim(title), "date": trim(date), "press":trim(press)})
            elif "<strong>" in item:
                #in case of text wrapped with strong tag
                s_content =  soup.strong.contents[0]
                if left_quote in s_content:
                    press = s_content.split(left_quote)[0]
                    title = s_content.split(left_quote)[1].replace(right_quote, "")

                for p_content in soup.p.contents:
                    if bool(re.search(regex, str(p_content))) == True:
                            date = p_content
                date = unicode(date)
                source_list.append({"press" : trim(press), "title" : trim(title), "date" : trim(date)})
            elif "<i>" in item:
                press = soup.i.contents[0]
                for p_content in soup.p.contents:
                    if left_quote in p_content:
                        editor = p_content.split(left_quote)[0]
                        title = p_content.split(left_quote)[1].replace(right_quote, "")
                    elif bool(re.search(regex, str(p_content))) == True:
                        date = p_content
                date = unicode(date)
                source_list.append({"press" : trim(press), "title" : trim(title), "date" : trim(date)})
            else :
                for p_content in soup.p.contents:
                    if left_quote in p_content:
                        press = p_content.split(left_quote)[0]
                        title = p_content.split(left_quote)[1].replace(right_quote, "")
                    elif bool(re.search(regex, str(p_content))) == True:
                        date = p_content
                date = unicode(date)
                source_list.append({"press" : trim(press), "title" : trim(title), "date" : trim(date)})
            
        return source_list

class MmlabSpider(scrapy.Spider):
    name = "snopes_update"
    allowed_domains = ["snopes.com"]
    start_urls = get_urls()

    def parse(self, response):
        url = response.xpath('//meta[@property="og:url"]/@content').extract_first()
        veracity = response.xpath('//div//div[contains(@class,"claim")]/span/text()').extract_first()
        if veracity == None:
            veracity = response.xpath('//font[@class="status_color"]//b/text()').extract_first()
        
        if veracity == None:
            veracity = response.xpath('//a[contains(@class, "claim")]/span/text()').extract_first()

        share_count = response.xpath('//div[@class="share-controls-item numbers share-count"]/text()').extract()[1].strip()
        fact_checker = response.xpath('//input[@name="post_author"]/@value').extract_first()
        if fact_checker == None:
            fact_checker = response.xpath('//a[@class="author-link"]/text()').extract_first()

        claim = response.xpath('//p[@itemprop="claimReviewed"]/text()').extract_first()
        if claim == None:
            claim = response.xpath('//div[@class="entry-content article-text"]/p/text()').extract_first()

        if claim != None:
            claim = claim.strip()
        
        tag = response.xpath('//p[@class="tag-box"]/a[not(@href="#show-all-tags")]/text()').extract()
       
        content = response.xpath('//footer//div[@class="article-sources-box"]/p').extract()
        source = get_sources(content)

        detailed_description = response.xpath('//div[@class="entry-content article-text"]').extract()
        #detailed_description = response.xpath('//div[@class="entry-content article-text"]/p/text() | //div[@class="entry-content article-text"]/blockquote/p/text() | //div[@class="entry-content article-text"]/blockquote/span/text()').extract()

        #if veracity != None and veracity != "":
        #yield {"url":url, "veracity": veracity, "share":share_count, "fact_checker":fact_checker, "claim":claim, "tag":tag, "source":source, "detailed_description":detailed_description}
        yield {"url":url, "sources" : source}




