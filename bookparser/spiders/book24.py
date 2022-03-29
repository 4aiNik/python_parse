import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/']

    def parse(self, response: HtmlResponse):
        links = response.xpath('//a[contains(@class, "product-card__image-link")]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.item_parse)

    def item_parse(self, response: HtmlResponse):
        link = response.url
        title_row = response.xpath('//h1[contains(@class, "product-detail-page__title")]/text()').get()
        if title_row.find(':') == -1:
            title = title_row
        else:
            title_parts = title_row.split(':')
            title = title_parts[1]

        author = response.xpath('//span[contains(text(),"Автор:")]/../following-sibling::div/a/text()').get()
        if author is None:
            author = response.xpath('//span[contains(text(),"Автор:")]/../following-sibling::div/text()').get()
        price = response.xpath('//span[@class="app-price product-sidebar-price__price"]/text()').get()
        price_old = response.xpath('//span[contains(@class, "product-sidebar-price__price-old")]/text()').get()
        if price_old is None:
            price_old = price
        rating = response.xpath('//span[contains(@class, "rating-widget__main-text")]/text()').get()

        item = BookparserItem(link=link, title=title, author=author, price_old=price_old, price=price, rating=rating)
        yield item
