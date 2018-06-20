import scrapy
from hoaxslayer.items import HoaxslayerItem


class HoaxslayerSpider(scrapy.Spider):
    name = "hoaxslayer"

    def start_requests(self):
        urls = [
                "https://www.hoax-slayer.net/category/hoaxes/",
                "https://www.hoax-slayer.net/category/scams/",
                "https://www.hoax-slayer.net/category/malware/",
                "https://www.hoax-slayer.net/category/fake-news/",
                "https://www.hoax-slayer.net/category/misleading/",
                "https://www.hoax-slayer.net/category/true/",
                "https://www.hoax-slayer.net/category/politics/"
                ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        item = HoaxslayerItem()

        #print(self.list_strip(response.xpath('//div[@class="entry-meta"]').extract()))
        title = response.xpath('//h2[@class="grid-title"]/a/text()').extract()
        postid = self.get_postid(response.xpath('//article/@id').extract())
        url = response.xpath('//h2[@class="grid-title"]/a/@href').extract()
        date = self.list_strip(response.xpath('//div[@class="grid-post-box-meta"]//span[not(contains(@class, "author-italic"))]/text()').extract())
        claim = response.xpath('//div[@class="item-content"]/p/text()').extract()
        category = [self.get_url(response.request.url)] * len(title)
        veracity = [self.get_veracity(self.get_url(response.request.url))] * len(title)

        yield date
        
        for i, info in enumerate(title):
            item['title'] = title[i]
            item['url'] = url[i]
            item['date'] = date[i]
            item['claim'] = claim[i]
            item['category'] = category[i]
            item['veracity'] = veracity[i]
            item['postid'] = postid[i]
            item['source'] = 'hoaxslayer'
            yield item

        """
        for info in zip(title, url, date, claim, category, veracity, postid):
            item['title'] = info[0]
            item['url'] = info[1]
            item['date'] = info[2]
            item['claim'] = info[3]
            item['category'] = info[4]
            item['veracity'] = info[5]
            item['postid'] = info[6]
            yield item
#            self.yield_item(scraped_info)
        """
        
        next_page = response.xpath('//a[@class="next page-numbers"]/@href').extract_first()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
        
    def parse_veracity(self, response):
        item = response.meta['item']
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
        if "page" in url:
            return url.split("/page")[0].split('/')[-1]
        else:
            return url.split('/')[-2]

    def get_veracity(self, category):
        if "true" != category:
            return "false"
        else:
            return "true"
