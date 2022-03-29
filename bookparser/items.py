# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookparserItem(scrapy.Item):
    link = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    price_old = scrapy.Field()
    price = scrapy.Field()
    rating = scrapy.Field()
    _id = scrapy.Field()
