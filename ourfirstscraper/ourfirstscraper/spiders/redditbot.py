# -*- coding: utf-8 -*-
import scrapy
import urllib, mimetypes
import traceback
import ssl

from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError


class RedditbotSpider(scrapy.Spider):
    name = 'redditbot'
    allowed_domains = []
    start_urls = ['https://stackoverflow.com']
    links=[]

    def start_requests(self):
        depth = getattr(self, 'depth', None)
        url = getattr(self, 'url', None)
        links=[]
        if url is not None:
            self.start_urls = [url]

        custom_settings = {
            'DEPTH_LIMIT': depth is not None or 1,
            'DEPTH_STATS_VERBOSE': True
        }
        for u in self.start_urls:
            yield scrapy.Request(u, callback=self.parse,
                                    errback=self.errback_httpbin)


    def parse(self, response):
        self.state['items_count'] = self.state.get('items_count', 0) + 1
        # Extracting the content using css selectors
        titles = response.css('a::attr(href)').getall()
        # votes = response.css('').extract()
        # times = response.css('time::attr(title)').extract()
        # comments = response.css('.comments::text').extract()

        # Give the extracted content row wise
        for item in zip(titles):
            # votes, times, comments
            # create a dictionary to store the scraped info
            if item[0].find('http') == 0 and self.check_mime_type(item[0]):
                self.links.append(item[0])
                scraped_info = {
                    'title': item[0],
                    # 'vote': item[1],
                    # 'created_at': item[2],
                    # 'comments': item[3],
                }
            # yield or give the scraped info to scrapy
                yield scraped_info
        next_page = self.links.pop(0)
        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.parse, errback=self.errback_httpbin)
            # yield response.follow(next_page, callback=self.parse)

    def check_mime_type(self, url):
        try:
            # use guess_type to for speed / efficiency, no need to call the site
            # returns a tuple
            if mimetypes.guess_type(url)[0] == 'text/html':
                return True
            # handle [SSL: CERTIFICATE_VERIFY_FAILED]
            context = ssl._create_unverified_context()
            #429 error comes from Reddit throttling the request
            with urllib.request.urlopen(url, context=context) as response:
                info = response.info()
                if info.get_content_type() == 'text/html':
                    return True
                else:
                    return False
        except Exception as e:
            print("type error: " + str(e))
            print(traceback.format_exc())

    def errback_httpbin(self, failure):
        # log all failures
        # self.logger.error(repr(failure))
        print(repr(failure))
        next_page = self.links.pop(0)
        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.parse, errback=self.errback_httpbin)
        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.info('HttpError on %s', response.url)
            yield scrapy.Request(next_page, callback=self.parse, errback=self.errback_httpbin)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.info('DNSLookupError on %s', request.url)
            yield scrapy.Request(next_page, callback=self.parse, errback=self.errback_httpbin)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.info('TimeoutError on %s', request.url)
            yield scrapy.Request(next_page, callback=self.parse, errback=self.errback_httpbin)

"""
Requirements:
1. cmd line arguments 
    √ url 
    depth limit
2. √ check mime type of each link --> process 'text/html' 
3. √ extract fixed <a>, not dynamic inserted links (how do you tell the difference)
4. per page calculate the ratio of same-domain:diff-domain links
    - same domain links have the same common prefix including subdomain
5. crawler should cache last work done to restart where left off after termination
6. schedule crawler
    - prevent duplicate downloads
    - check when page was last updated --> need to store lastUpdateDate field for each page
        - don't re-download unless current page date is later than lastUpdateDate field
7. Output TSV  (url, depth, ratio)
"""