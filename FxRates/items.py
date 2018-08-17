# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose


class Rates(Item):
    bank_name = Field()
    currency_name = Field()
    currency_official_rate = Field()
    currency_bid_rate = Field()
    currency_ask_rate = Field()
    insert_time = Field()

class MainItemLoader(ItemLoader):

    default_item_class = Rates
    default_output_processor = TakeFirst()

    currency_name_in = MapCompose(lambda x: x.upper())