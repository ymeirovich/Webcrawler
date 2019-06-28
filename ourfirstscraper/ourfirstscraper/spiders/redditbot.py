# -*- coding: utf-8 -*-

import traceback

import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.spiders import Rule
from twisted.internet.error import DNSLookupError, TCPTimedOutError
from ..items import OurfirstscraperItem
from ..pipelines import DuplicatesPipeline
from scrapy.linkextractors import LinkExtractor


class RedditbotSpider(scrapy.Spider):
    name = 'redditbot'
    # allowed_domains = []
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
    ]
    # rules = (
    #     # Extract links matching 'category.php' (but not matching 'subsection.php')
    #     # and follow links from them (since no callback means follow=True by default).
    #     # Rule(LinkExtractor(allow=('category\.php',), deny=('subsection\.php',))),
    #
    #     # Extract links matching 'item.php' and parse them with the spider's method parse_item
    #     Rule(LinkExtractor(allow=('http?:',)), callback='parse_item'),
    # )

    # def __init__(self, name=None, **kwargs):
    #     super().__init__(name=None, **kwargs)
    #     self.links = []
    #     self.store = LinkStore()
    #     self.duplicates = DuplicatesPipeline().ids_see

    # def start_requests(self):
    #     depth = getattr(self, 'depth', None)
    #     url = getattr(self, 'url', None)
    #     if url is not None:
    #         self.start_urls = [url]
    #     self.start_urls = [
    #         'http://quotes.toscrape.com/page/1/',
    #     ]
    #
    #     custom_settings = {
    #         'DEPTH_LIMIT': depth is not None or 1,
    #         'DEPTH_STATS_VERBOSE': True
    #     }
    #     for u in self.start_urls:
    #         yield scrapy.Request(u, callback=self.parse_item,
    #                              errback=self.errback_httpbin, dont_filter=True)
    def parse(self, response):
        try:
            def x():
                pass

            print('depth=' and response.meta['depth'])
            for quote in response.css('div.quote'):
                yield {
                    'text': quote.css('span.text::text').get(),
                    'author': quote.css('small.author::text').get(),
                    'tags': quote.css('div.tags a.tag::text').getall(),
                }

            next_page = response.css('li.next a::attr(href)').get()
            if next_page is not None:
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse,dont_filter=True)
            else

            # self.logger.info('Hi, this is an item page! %s', response.url)
            # self.links = LinkExtractor().extract_links(response)
            # if hasattr(response.meta, 'depth') and response.meta['depth'] < int(self.depth):
            #     # self.store.add(response.url, self.links, response.meta['depth'])
            #     # self.links = response.css('a::attr(href)').getall()
            #     item = OurfirstscraperItem()
            #     item['url'] = response.url
            #     if hasattr(response.meta, 'depth'):
            #         item['depth'] = response.meta['depth']
            #     item['ratio'] = 0
            # for next_page in self.links:
            #     # rmv " " & / for true comparison
            #     if response.url.strip().replace('/', '') != next_page.url.strip().replace('/', ''):
            #         self.links.pop(0)
            #         yield scrapy.Request(next_page.url, callback=self.parse_item, errback=self.errback_httpbin,
            #                              dont_filter=True)
            # # return item
        except Exception as e:
            print("type error: " + str(e))
            print(traceback.format_exc())

    def errback_httpbin(self, failure):
        # log all failures
        # self.logger.error(repr(failure))
        print(repr(failure))
        next_page = self.links.pop(0)
        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.parse, errback=self.errback_httpbin, dont_filter=True)
        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.info('HttpError on %s', response.url)
            yield scrapy.Request(next_page, callback=self.parse, errback=self.errback_httpbin, dont_filter=True)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.info('DNSLookupError on %s', request.url)
            yield scrapy.Request(next_page, callback=self.parse, errback=self.errback_httpbin, dont_filter=True)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.info('TimeoutError on %s', request.url)
            yield scrapy.Request(next_page, callback=self.parse, errback=self.errback_httpbin, dont_filter=True)


class LinkStore(object):
    """
    Question: how does one keep state using recursion?
    - by threading the execution context from one level of the recursion tree to the next
    - by keeping the context in a global scope and iterate
    """

    def __init__(self, name=None, **kwargs):
        super().__init__(**kwargs)
        self._store = []
        self._followedLinks = []
        self.duplicates = DuplicatesPipeline().ids_seen

    def create_dict(self):
        pass

    def get_store(self):
        return self._store

    def add(self, link, links, depth):
        if link not in self._store:
            _arr = []
            if len(links) > 0:
                for l in links:
                    _arr.append(l.url)
                self._store.append({link, _arr})

    def followed_links(self, arg):
        if arg in self.duplicates:
            pass
        else:
            pass
        # self._followedLinks.append(arg)

    def _exist_in_followed_links(self, arg):
        return arg in self._followedLinks

    def get_next_page(self, arg):

        pass


"""
Requirements:
1. cmd line arguments 
    √ url 
    depth limit
2. √ check mime type of each link --> process 'text/html' 
3. √ extract fixed <a>, not dynamic inserted links (how do you tell the difference)
4. per page calculate the ratio of same-domain:diff-domain links
    - same domain links have the same common prefix including subdomain
5. √ crawler should cache last work done to restart where left off after termination
6. schedule crawler
    - prevent duplicate downloads
    - check when page was last updated --> need to store lastUpdateDate field for each page
        - don't re-download unless current page date is later than lastUpdateDate field
7. Output TSV  (url, depth, ratio)
"""
