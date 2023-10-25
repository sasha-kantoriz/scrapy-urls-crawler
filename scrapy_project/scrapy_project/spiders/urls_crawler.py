import time
import logging
import mysql.connector
from urllib.parse import urlparse
from http.client import responses
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.signals import spider_opened


class UrlsCrawlerSpider(CrawlSpider):
    name = "urls_crawler"
    processed_urls_num = 0
    custom_settings = {
        'LOG_ENABLED': True,
        'HTTPERROR_ALLOW_ALL': True,
        'ALLOWED_DOMAINS': r"*",
        'USER_AGENT': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36",
        'CONCURRENT_REQUESTS': 1
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        cls.rules = [
            Rule(
                LinkExtractor(
                    deny_extensions=[
                        'png', 'jpg', 'jpeg', '7z', '7zip', 'apk', 'bz2', 'cdr', 'dmg', 'ico', 'iso', 'tar', 'rar', 'tar.gz', 'pdf', 'docx'
                    ],
                ),
                callback='parse',
                follow=bool(kwargs.get('recursive', False)),
            ),
        ]
        # spider options
        cls.start_urls = kwargs.get('urls').split(',')
        cls.limit = int(kwargs.get('limit', 100))
        # mysql parameters
        cls.db_host = 'website-promoter.net'
        cls.db_port = 3306
        cls.db_name = 'websitepromoter_siteaudits'
        cls.db_user = kwargs.get('db_user')
        cls.db_password = kwargs.get('db_password')
        crawler.signals.connect(cls.spider_opened, signal=spider_opened)
        spider = super(UrlsCrawlerSpider, cls).from_crawler(crawler, *args, **kwargs)
        return spider

    @classmethod
    def spider_opened(cls, spider):
        logging.info(f"{'=' * 80}\n\nConnecting to: mysql://{cls.db_user}:{cls.db_password}@{cls.db_host}:{cls.db_port}/{cls.db_name}\n\n")
        try:
            db_connection = mysql.connector.connect(
                host=cls.db_host,
                port=cls.db_port,
                user=cls.db_user,
                passwd=cls.db_password,
                database=cls.db_name
            )
        except mysql.connector.Error as err:
            logging.info("=" * 80 + "\n\nClosing Spider\n\n" + "=" * 80)
            spider.crawler.engine.close_spider(spider, reason="Failed DB connection: {}".format(err))
            return

        cursor = db_connection.cursor()
        cursor.execute("""INSERT INTO projects (url, domain, date, status) \
            VALUES (%s, %s, %s, %s)""",
            (cls.start_urls[0], urlparse(cls.start_urls[0]).netloc, time.time(), 0)
        )
        db_connection.commit()
        cls.project_id = cursor.lastrowid
        cursor.close()
        db_connection.close()

    def closed(self, reason):
        db_connection = mysql.connector.connect(
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            passwd=self.db_password,
            database=self.db_name
        )
        cursor = db_connection.cursor()
        cursor.execute("UPDATE projects SET status = %s WHERE id = %s", (1, self.project_id))
        db_connection.commit()
        cursor.close()
        db_connection.close()

    def parse(self, response):
        if self.processed_urls_num >= int(self.limit):
            self.crawler.engine.close_spider(self, reason='Limit reached')
            return
        self.processed_urls_num += 1
        title = response.xpath("//title/text()").extract_first()
        description = response.xpath("//meta[@name='description']/@content").extract_first()
        extracted_url = {
            'projectid': self.project_id,
            'url': response.url,
            'response_code': response.status,
            'response_msg': responses[response.status],
            'title': title,
            'titlechars': len(title),
            'description': description if description else "-",
            'descriptionchars': len(description) if description else 0,
        }
        yield extracted_url
