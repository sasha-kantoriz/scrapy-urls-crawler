import os
import mysql.connector


class WebspiderPipeline(object):
    def process_item(self, item, spider):
        db_connection = mysql.connector.connect(
            host=spider.db_host,
            port=spider.db_port,
            user=spider.db_user,
            passwd=spider.db_password,
            database=spider.db_name
        )
        db_cursor = db_connection.cursor()
        db_cursor.execute("""INSERT INTO urls (projectid, url, response_code, response_msg, title, titlechars, description, descriptionchars) \
            VALUES (%(projectid)s, %(url)s, %(response_code)s, %(response_msg)s, %(title)s, %(titlechars)s, %(description)s, %(descriptionchars)s)""",
            item
        )
        db_connection.commit()
        db_cursor.close()
        db_connection.close()
        return item

