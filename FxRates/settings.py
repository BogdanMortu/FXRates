# -*- coding: utf-8 -*-

# Scrapy settings for FxRates project

BOT_NAME = 'FxRates'

SPIDER_MODULES = ['FxRates.spiders']
NEWSPIDER_MODULE = 'FxRates.spiders'

LOG_FILE = 'logs.txt'
LOG_LEVEL = 'INFO'

CONCURRENT_REQUESTS = 2
DOWNLOAD_DELAY = 1
RANDOM_USER_AGENTS = True
RETRY_ENABLED = True
RETRY_TIMES = 8
RETRY_HTTP_CODES = [503, 511, 301, 302]
HTTPERROR_ALLOW_ALL = True
COOKIES_ENABLED = False

ROBOTSTXT_OBEY = True

ITEM_PIPELINES = {
    'FxRates.pipelines.RemoveItemWithNoCurrenciesPipeline': 1,
	'FxRates.pipelines.StoreInDBPipeline': 2
}

HTTPCACHE_ENABLED = True

