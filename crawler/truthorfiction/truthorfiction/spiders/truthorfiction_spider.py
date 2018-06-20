import scrapy
from truthorfiction.items import TruthorfictionItem


class TruthorfictionSpider(scrapy.Spider):
    name = "truthorfiction"

    def start_requests(self):
        urls = [
                "https://www.truthorfiction.com/category/politics",
                "https://www.truthorfiction.com/category/religious",
                "https://www.truthorfiction.com/category/terrorism",
                "https://www.truthorfiction.com/category/9-11-attack",
                "https://www.truthorfiction.com/category/natural-disasters",
                "https://www.truthorfiction.com/category/animals",
                "https://www.truthorfiction.com/category/insects",
                "https://www.truthorfiction.com/category/space-aviation",
                "https://www.truthorfiction.com/category/food",
                "https://www.truthorfiction.com/category/household",
                "https://www.truthorfiction.com/category/crime-police",
                "https://www.truthorfiction.com/category/money-financial",
                "https://www.truthorfiction.com/category/health-medical"
                ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        item = TruthorfictionItem()

        #print(self.list_strip(response.xpath('//div[@class="entry-meta"]').extract()))
        title = response.xpath('//h2[@class="grid-title"]/a/text()').extract()
        item['postid'] = self.get_postid(response.xpath('//article/@id').extract())
        item['title'] = title
        item['url']= response.xpath('//h2[@class="grid-title"]/a/@href').extract()
        item['date'] = self.list_strip(response.xpath('//div[@class="grid-post-box-meta"]//span/text()').extract())
        item['claim'] = response.xpath('//div[@class="item-content"]/p/text()').extract()
        item['category'] = [self.get_url(response.request.url).split('/')[-1]] * len(title)
        response.request.url.split('/')
        for info in zip(item['title'], item['url'], item['date'], item['claim'], item['category'], item['postid']):
            scraped_info = {
                    'title' : info[0],
                    'url' : info[1],
                    'date' : info[2],
                    'claim' : info[3],
                    'category' : info[4],
                    'postid' : info[5]
                    }
            yield response.follow(info[1], callback=self.parse_veracity, meta={'item':scraped_info})

        next_page = response.xpath('//div[@class="older"]/a/@href').extract_first()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_veracity(self, response):
        item = response.meta['item']
        item['source'] = 'truthorfiction'
        rating = response.xpath('//h1[@class="post-title single-post-title"]/text()').extract_first()
        #rating = response.xpath('//div[@class="inner-post-entry"]/h3/span/text()').extract_first()
        if rating != None:
            #parse image name
            veracity = rating.split('-')[-1]
            veracity = veracity.replace('!', '')
            item['veracity'] = veracity
            yield item

    def get_postid(self, postid):
        return [x.replace("post-","") for x in postid]

    def list_strip(self, list_data):
        return [x.strip() for x in list_data]

    def get_url(self, url):
        return url.split("/page")[0]
