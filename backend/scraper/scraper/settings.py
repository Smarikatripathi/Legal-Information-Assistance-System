# Scrapy settings for the Legal IAS crawler project.

BOT_NAME = "legal_ias_scraper"

SPIDER_MODULES = ["scraper.spiders"]
NEWSPIDER_MODULE = "scraper.spiders"

ROBOTSTXT_OBEY = True
USER_AGENT = (
    "Mozilla/5.0 (compatible; LegalIAS-Bot/1.0; +https://lawcommission.gov.np/) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,ne;q=0.8",
}

CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8
DOWNLOAD_DELAY = 0
DOWNLOAD_TIMEOUT = 60
RETRY_ENABLED = True
RETRY_TIMES = 2
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

ITEM_PIPELINES = {}

DOWNLOADER_CLIENTCONTEXTFACTORY = "scraper.middlewares.RelaxedSSLContextFactory"

AUTOTHROTTLE_ENABLED = False
# AUTOTHROTTLE_START_DELAY = 1.0
# AUTOTHROTTLE_MAX_DELAY = 10.0
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(levelname)s %(asctime)s [%(name)s] %(message)s"
FEED_EXPORT_ENCODING = "utf-8"

# Avoid duplicate requests across redirects
DUPEFILTER_DEBUG = False
REDIRECT_MAX_TIMES = 5

DEPTH_LIMIT = 0
DEPTH_PRIORITY = 1