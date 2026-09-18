import scrapy

class PublicPageItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    keyword_match = scrapy.Field()
    emails = scrapy.Field()
