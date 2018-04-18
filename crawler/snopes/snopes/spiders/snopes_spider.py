import scrapy
import re
from BeautifulSoup import BeautifulSoup

from snopes.items import SnopesItem
from snopes.items import ArticleItem

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
    name = "snopes"
    allowed_domains = ["snopes.com"]
    max_news_num = 10
    start_urls = ["https://www.snopes.com/fact-check"
            ]
    
    def data_processing(self, data_type, data_list):
        if data_type=="category":
            category_list = []
            for i in range(self.max_news_num):
                category_list.append((data_list[i].replace('<div class="breadcrumbs">',"").replace('<i class="fa fa-angle-right"></i>','_').replace('</div>', '').replace("Fact Check","").strip()))
            return category_list
        elif data_type=="description":
            desc_list = []
            for i in range(0, self.max_news_num * 2, 2):
                desc_list.append(data_list[i+1].strip())
            return desc_list
        elif data_type=="post_id":
            id_list = []
            for i in range(self.max_news_num):
                _ids = data_list[i].split()
                id_idx = 0
                for word in _ids:
                    if "post-" in word:
                        id_list.append(word.split('-')[-1])
                        break
            return id_list
        else: 
            return data_list[0:10]


    def parse(self, response):
        item = SnopesItem()
        item['post_id'] = self.data_processing("post_id", response.xpath('//article//a/@class').extract())
        item['url'] = self.data_processing("url", response.xpath('//article//a/@href').extract())
        item['category'] = self.data_processing("category", response.xpath('//article//div[@class="article-link-container"]//div[@class="breadcrumbs"]').extract())
        item['title'] = response.xpath('//article//div[@class="article-link-container"]//h2[@class="title"]/text()').extract()
        item['description'] = self.data_processing("description", response.xpath('//article//div[@class="article-link-container"]//p[@class="desc"]/text()').extract())
        item['published_date'] = response.xpath('//article//a/meta[@itemprop="datePublished"]/@content').extract()
        item['modified_date'] = response.xpath('//article//a/meta[@itemprop="dateModified"]/@content').extract()

        for info in zip(item['url'], item['category'], item['title'], item['description'], item['published_date'], item['modified_date'], item['post_id']):
            scraped_info = {
                    'url' : info[0],
                    'category' : info[1],
                    'title' : info[2],
                    'description' : info[3], 
                    'published_date' : info[4],
                    'modified_date' : info[5],
                    'post_id' : info[6],
                    }
            #recursive page request
            yield response.follow(info[0], callback=self.parse_veracity, meta={'item':scraped_info})

        next_page = response.xpath('//div[contains(@class, "pagination-inner-wrapper")]//a[contains(., "Next")]/@href').extract_first()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
            
    #detail article veracity only
    def parse_veracity(self, response):
        item = response.meta['item']
        item['veracity'] = response.xpath('//div//div[contains(@class,"claim")]/span/text()').extract_first()
        if item['veracity'] == None:
            item['veracity'] = response.xpath('//font[@class="status_color"]//b/text()').extract_first()

        if item['veracity'] == None:
            item['veracity'] = response.xpath('//a[contains(@class, "claim")]/span/text()').extract_first()

        item['share_count'] = response.xpath('//div[@class="share-controls-item numbers share-count"]/text()').extract()[1].strip()
        item['fact_checker'] = response.xpath('//input[@name="post_author"]/@value').extract_first()
        if item['fact_checker'] == None:
            item['fact_checker'] = response.xpath('//a[@class="author-link"]/text()').extract_first()

        item['claim'] = response.xpath('//p[@itemprop="claimReviewed"]/text()').extract_first()
        if item['claim'] == None:
            item['claim'] = response.xpath('//div[@class="entry-content article-text"]/p/text()').extract_first()
        if item['claim'] != None:
            item['claim'] = item['claim'].strip()
        item['tag'] = response.xpath('//p[@class="tag-box"]/a[not(@href="#show-all-tags")]/text()').extract()
        content = response.xpath('//footer//div[@class="article-sources-box"]/p').extract()
        source = get_sources(content)
        item['source'] = source

        item['detailed_description'] = response.xpath('//div[@class="entry-content article-text"]').extract()
        #item['detailed_description'] = response.xpath('//div[@class="entry-content article-text"]/p/text() | //div[@class="entry-content article-text"]/blockquote/p/text() | //div[@class="entry-content article-text"]/blockquote/span/text()').extract()


        yield item

    #detail article parser - currently not being used
    def parse_article_detail(self, response):
        item = ArticleItem()
        item['veracity'] = response.xpath('//div//div[contains(@class,"claim")]/span/text()').extract()
        item['title'] = response.xpath('//header//h1[@class="article-title"]/text()').extract()
        item['claim'] = response.xpath('//p[@itemprop="claimReviewed"]/text()').extract()
        item['published_date'] = response.xpath('//article/meta[@itemprop="datePublished"]/@content').extract()
        item['fact_checker'] = response.xpath('//a[@class="author-link"]/text()').extract()
        item['post_id'] = response.xpath('//p//input[contains(@name,"post_id")]/@value').extract_first()
        yield item





