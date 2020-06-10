# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class DemoPipeline:
    def process_item(self, item, spider):
        return item

import json

class JsonWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open('batdongsan.json', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

import pymongo

class MongoPipeline:

    collection_name = 'estate'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI', 'mongodb+srv://dataraw:dataraw10@estateraw-ww6ya.mongodb.net/dataraw?retryWrites=true&w=majority'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'dataraw')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].update({'id':item['id']},{'$set':dict(item)},upsert=True)
        return item
        
