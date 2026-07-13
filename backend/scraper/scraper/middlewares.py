"""Downloader middleware and SSL helpers for Nepal government sites with expired certs."""

import logging
import ssl

from scrapy.core.downloader.contextfactory import ScrapyClientContextFactory

logger = logging.getLogger(__name__)


class RelaxedSSLContextFactory(ScrapyClientContextFactory):
    """Allow downloads from official Nepal legal hosts with expired TLS certificates."""

    GOV_HOST_SUFFIXES = (
        "lawcommission.gov.np",
        "repository.lawcommission.gov.np",
    )

    def getContext(self, hostname=None, port=None):
        ctx = ssl.create_default_context()
        if hostname and any(hostname.endswith(suffix) for suffix in self.GOV_HOST_SUFFIXES):
            logger.debug("Relaxed SSL verification for %s", hostname)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        return ctx


class ScraperSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        yield from result
