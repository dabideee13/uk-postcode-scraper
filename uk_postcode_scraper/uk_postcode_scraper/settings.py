BOT_NAME = 'uk_postcode_scraper'

SPIDER_MODULES = ['uk_postcode_scraper.spiders']
NEWSPIDER_MODULE = 'uk_postcode_scraper.spiders'

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS = 32

DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY = True
AUTOTHROTTLE_ENABLED = True

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,

    # 'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    # 'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
}

HTTPCACHE_ENABLED = True
