# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from FxRates.items import MainItemLoader
import logging as log
import datetime
from scrapy.exceptions import CloseSpider

# create custom log for Banca Transilvania
logger = log.getLogger('BancaTransilvania_logger')
logger.info('We have created the %s custom log', logger)


class BancatransilvaniaSpider(Spider):
    name = 'BancaTransilvania'
    allowed_domains = ['bancatransilvania.ro']
    start_urls = ['https://www.bancatransilvania.ro/curs-valutar-spot/']

    def __init__(self):

        # set a dictionary with the values of currencies that are in scope
        self.currency = {
            "1": "USD",
            "2": "EUR",
            "3": "GBP"
        }

        # set a list with history years that are in scope
        self.years = ['2018', '2017', '2016']

    def parse(self, response):

        # parse current rates
        yield Request('https://www.bancatransilvania.ro/curs-valutar-spot/'
                      , callback=self.parse_current_rates)

        # parse history rates
        for year in self.years:
            for currency in self.currency.keys():
                history_url = 'https://www.bancatransilvania.ro/istoric_valuta_processor.php?limba=0&valuta=' + currency + '&an=' + year + '&tabel=true'
                yield Request(history_url, callback=self.parse_history_rates)

    def parse_current_rates(self, response):

        quotations = response.xpath('//tr')[1:]

        if quotations is None:
            logger.critical('No quotations on this page')
            raise CloseSpider('No quotations on this page')

        for quotation in quotations[0:3]:
            loader = MainItemLoader(selector=quotation)

            # load the currency name
            loader.add_xpath('currency_name', './/td/span/text()')

            # load the official rate (posted by Natioanl Romanian Bank)
            loader.add_xpath('currency_official_rate', './/td[@width="10%"][1]/text()')

            # load the bid rate for a specific currency
            loader.add_xpath('currency_bid_rate', './/td[@width="10%"][2]/text()')

            # load the ask rate for a specific currency
            loader.add_xpath('currency_ask_rate', './/td[@width="10%"][3]/text()')

            # load the name of the Bank
            loader.add_value('bank_name', 'Banca Transilvania')

            # load the capturing time
            now = datetime.datetime.now()
            loader.add_value('insert_time', now.strftime('%Y-%m-%d %H-%M'))

            yield loader.load_item()

    def parse_history_rates(self, response):

        # get the currency name
        currency_name = str(response.xpath('//*[@colspan="4"]/text()').extract())[3:6]

        quotations = response.xpath('//tr')[3:]

        if quotations is None:
            logger.critical('No quotations on history page')
            raise CloseSpider('No quotations on history page')

        for quotation in quotations:
            loader = MainItemLoader(selector=quotation)

            # load the currency name
            loader.add_value('currency_name', currency_name)

            # load the official rate (posted by Natioanl Romanian Bank)
            currency_official_rate = quotation.xpath('.//td[3]/text()').extract()
            loader.add_value('currency_official_rate', currency_official_rate)

            # load the bid rate for a specific currency
            currency_bid_rate = quotation.xpath('.//td[4]/text()').extract()
            loader.add_value('currency_bid_rate', currency_bid_rate)

            # load the ask rate for a specific currency
            currency_ask_rate = quotation.xpath('.//td[5]/text()').extract()
            loader.add_value('currency_ask_rate', currency_ask_rate)

            # load the name of the Bank
            loader.add_value('bank_name', 'Banca Transilvania')

            # load the capturing time
            insert_time = quotation.xpath('.//td[2]/text()').extract()
            loader.add_value('insert_time', insert_time)

            yield loader.load_item()
