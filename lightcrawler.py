import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlparse

class LightcrawlerSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        start_urls = []
        depth = getattr(self, 'depth', None)
        if depth is None:
            raise Exception('Command line argument \'depth\' must be set')
        url = getattr(self, 'url', None)
        links=[]
        if url is not None:
            self.start_urls = [url]

        custom_settings = {
            'DEPTH_LIMIT': depth is not None or 1,
            'DEPTH_STATS_VERBOSE': True
        }
        rules = (
            # Extract links matching 'category.php' (but not matching 'subsection.php')
            # and follow links from them (since no callback means follow=True by default).
            # Rule(LinkExtractor(allow=('category\.php',), deny=('subsection\.php',))),

            # Extract links matching 'item.php' and parse them with the spider's method parse_item
            Rule(LinkExtractor(allow=('//',1)), unique=True, callback='parse_item'),
        )

    def parse_item(self, response):
        self.logger.info('Hi, this is an item page! %s', response.url)
        item = scrapy.Item()
        item['url'] = response.url
        item['depth'] = response.meta['depth']
        item['ratio'] = 0
        return item