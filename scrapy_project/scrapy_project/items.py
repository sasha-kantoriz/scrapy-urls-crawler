import scrapy


class WebspiderItem(scrapy.Item):
    url = scrapy.Field()
    projectid = scrapy.Field()
    response_code = scrapy.Field()
    response_msg = scrapy.Field()
    title = scrapy.Field()
    titlechars = scrapy.Field()
    description = scrapy.Field()
    descriptionchars = scrapy.Field()
