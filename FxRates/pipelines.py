import sqlite3 as lite
from scrapy.exceptions import DropItem
import logging as log


# set priority 1 in settings.py
# Remove items that do not have a currency_name
class RemoveItemWithNoCurrenciesPipeline(object):

    def process_item(self, item, spider):
        if item['currency_name']:
            return item
        else:
            raise DropItem("Missing currency_name in %s" % item)


con = None  # db connection


# set priority 2 in settings.py
class StoreInDBPipeline(object):

    def __init__(self):
        self.con = lite.connect('rates.db')
        self.cur = self.con.cursor()
        self._create_rates_table()

    def process_item(self, item, spider):

        # check for rate existence in db
        self.cur.execute(
            "select bank_name,currency_name,currency_bid_rate,currency_ask_rate,insert_time from rates \
                where bank_name =? and currency_name=? and currency_bid_rate=? and currency_ask_rate=? and insert_time=?"
            , [
                item['bank_name'],
                item['currency_name'],
                item['currency_bid_rate'],
                item['currency_ask_rate'],
                item['insert_time']
            ]
            )
        result = self.cur.fetchone()

        if result:
            # do not write to db if the rates already exists; log existing items
            log.info('Item already in database: %s', item)
        else:
            # insert row into db
            self._store_in_db(item)
        return item

    def _store_in_db(self, item):

        self.cur.execute("INSERT INTO rates(bank_name,currency_name,currency_official_rate,currency_bid_rate,currency_ask_rate,insert_time) \
                          VALUES( ?, ?, ?, ?, ?, ?)",
                         (
                             str(item['bank_name']),
                             str(item['currency_name']),
                             str(item['currency_official_rate']),
                             str(item['currency_bid_rate']),
                             str(item['currency_ask_rate']),
                             str(item['insert_time'])
                         ))
        self.con.commit()

    def _create_rates_table(self):
        # reset the autoincrement
        self.cur.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='rates';")

        # create table rates at runtime
        self.cur.execute("CREATE TABLE IF NOT EXISTS rates(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
        bank_name TEXT, \
        currency_name TEXT, \
        currency_official_rate TEXT, \
        currency_bid_rate TEXT, \
        currency_ask_rate TEXT, \
        insert_time TEXT \
      )")

    def __del__(self):
        self.con.close()