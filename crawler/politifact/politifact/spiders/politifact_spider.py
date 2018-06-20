import scrapy

from politifact.items import PolitifactItem

class PolitifactSpider(scrapy.Spider):
    name = "politifact"

    def start_requests(self):
        urls = [
                "http://www.politifact.com/truth-o-meter/rulings/false/",
                "http://www.politifact.com/truth-o-meter/rulings/true/"
                ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def data_trim(self, data):
        if data == None:
            return data
        data = data.replace('"', '\\"')
        data = data.replace("'", "\\'")
        data = data.replace('%', '%%')
        return data

    def parse(self, response):
        item = PolitifactItem()
        page = response.url.split("/")[-1]
        claim = response.xpath('//div[@class="statement__body"]//p[@class="statement__text"]/a/text()').extract()
        veracity = response.xpath('//div[@class="statement"]//div[@class="meter"]//a//img/@alt').extract()
        date = response.xpath('//p[@class="statement__edition"]/span/text()').extract()
        url = response.xpath('//div[@class="statement__body"]//p[@class="statement__text"]/a/@href').extract()
        for i in zip(claim, veracity, date, url):
            info = {
                    'claim':i[0].strip(),
                    'veracity':i[1], 
                    'date' : ' '.join(i[2].split(',')[1:]), 
                    'source': 'politifact',
                    'url' : "https://www.politifact.com" + i[3],
                    'postid': ''
                    }
            print(info)
            yield response.follow(i[3], callback=self.parse_url, meta={'item': info})

        #next_page = response.xpath('//div[@class="pagination"]//span//a').extract_first()
        next_page = response.xpath('//div[@class="pagination"]//span//a[contains(@title, "Next")]/@href').extract_first()
        
        if next_page is not None:
#        if next_page is not None and '5' not in next_page:
            yield response.follow(next_page, callback=self.parse)
        #yield text, verdict

    def parse_url(self, response):
        item = response.meta['item']
        title = response.xpath('//title/text()').extract_first()
        title = title.split('|')[0]
        item['title'] = title.strip()
        yield item
