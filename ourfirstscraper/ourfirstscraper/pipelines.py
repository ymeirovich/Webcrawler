# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem

import json


class OurfirstscraperPipeline(object):
    def process_item(self, item, spider):
        return item

    def open_spider(self,spider):
        pass

    def close_spider(self,spider):
        pass


class JsonWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open('items.json', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        # line = json.dumps(dict(item)) + "\n"
        # self.file.write(line)
        # return item
        pass


class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        # if item['url'] in self.ids_seen:
        #     raise DropItem("Duplicate item found: %s" % item)
        # else:
        #     self.ids_seen.add(item['url'])
        #     return item
        pass

