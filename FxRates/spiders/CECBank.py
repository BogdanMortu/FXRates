# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from FxRates.items import MainItemLoader
import logging as log
import datetime
from scrapy.exceptions import CloseSpider

# create custom log for CEC Bank
logger = log.getLogger('CECBank_logger')
logger.info('We have created the %s custom log', logger)


class CecbankSpider(Spider):
    name = 'CECBank'
    allowed_domains = ['www.cec.ro']
    start_urls = ['https://www.cec.ro/curs-valutar/']

    def __init__(self):

        # set a dictionary with the values of currencies that are in scope
        self.currency = {
            "1": "USD",
            "2": "EUR",
            "3": "GBP"
        }

    def parse(self, response):
        for currency in self.currency.values():
            history_url = 'https://www.cec.ro/curs-istoric/cont/' + currency
            yield Request(history_url, callback=self.parse_history_rates)

    def parse_history_rates(self, response):
        # capture the currency name
        currency_name = response.xpath('//*/h1[@class="title"]/text()').extract_first()[-3:]

        quotations = response.xpath('//tbody/tr')

        if quotations is None:
            logger.critical('No quotations on this page')
            raise CloseSpider('No quotations on this page')

        for quotation in quotations:
            loader = MainItemLoader(selector=quotation)

            rates = quotation.xpath('.//td/text()').extract()

            # load the currency name
            loader.add_value('currency_name', currency_name)

            # load the official rate (posted by Natioanl Romanian Bank)
            loader.add_value('currency_official_rate', rates[1])

            # load the bid rate for a specific currency
            loader.add_value('currency_bid_rate', rates[2])

            # load the ask rate for a specific currency
            loader.add_value('currency_ask_rate', rates[3])

            # load the name of the Bank
            loader.add_value('bank_name', 'CEC Bank')

            # load the capturing time
            loader.add_value('insert_time', rates[0])

            yield loader.load_item()

        # generate the url for the next page
        next_page_url = response.xpath('//*[@class="next"]/a/@href').extract_first()
        if next_page_url is not None:
            absolut_next_page_url = response.urljoin(next_page_url)

        yield Request(absolut_next_page_url, callback=self.parse_history_rates)
