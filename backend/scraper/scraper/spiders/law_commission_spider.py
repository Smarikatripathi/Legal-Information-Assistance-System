"""
Nepal Law Commission PDF spider.

Downloads legal PDFs only (Acts, Rules, Regulations, Constitution, Court Decisions)
into backend/media/legal_docs/. No Django, embeddings, or FAISS operations.
"""

import re
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

import scrapy

# WordPress category IDs on lawcommission.gov.np
LEGAL_CATEGORIES = {
    "2166": "acts",
    "2160": "rules_regulations",
    "2157": "constitution",
    "2161": "regulations",
}

IGNORE_PATH_RE = re.compile(
    r"/(?:news|notice|notices|press|event|gallery|blog|about|contact|"
    r"announcement|vacancy|tender|media|photo|video|slider|banner)(?:/|$)",
    re.I,
)


class LawCommissionSpider(scrapy.Spider):
    name = "law_commission"

    allowed_domains = [
        "lawcommission.gov.np",
        "www.lawcommission.gov.np",
        "giwmscdnone.gov.np",
    ]

    start_urls = []

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 0.5,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
        "DOWNLOAD_TIMEOUT": 120,
        "RETRY_TIMES": 3,
        "LOG_LEVEL": "INFO",
        "USER_AGENT": "LegalIAS-Bot/1.0 (+https://lawcommission.gov.np/)",
        "ITEM_PIPELINES": {},
        "DOWNLOADER_CLIENTCONTEXTFACTORY": "scraper.middlewares.RelaxedSSLContextFactory",
    }

    def __init__(self, max_pages=5000, categories="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.visited_pages: set[str] = set()
        self.downloaded_pdfs: set[str] = set()

        if categories:
            cat_ids = [c.strip() for c in categories.split(",") if c.strip()]
            self.allowed_categories = {cid: LEGAL_CATEGORIES[cid] for cid in cat_ids if cid in LEGAL_CATEGORIES}
        else:
            self.allowed_categories = dict(LEGAL_CATEGORIES)

        self.start_urls = [
            f"https://lawcommission.gov.np/category/{cat_id}/"
            for cat_id in self.allowed_categories
        ]

        backend_root = Path(__file__).resolve().parents[3]
        self.download_dir = backend_root / "media" / "legal_docs"
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def _normalize(self, url: str) -> str:
        return url.split("#")[0].rstrip("/")

    def _category_id(self, url: str) -> str | None:
        match = re.search(r"/category/(\d+)", urlparse(url).path)
        return match.group(1) if match else None

    def _is_legal_page(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.netloc and parsed.netloc not in self.allowed_domains:
            return False
        if IGNORE_PATH_RE.search(parsed.path):
            return False
        cat_id = self._category_id(url)
        if cat_id and cat_id in self.allowed_categories:
            return True
        # Allow pagination under an already-visited legal category path
        for cid in self.allowed_categories:
            if f"/category/{cid}" in parsed.path:
                return True
        return False

    def parse(self, response):
        if len(self.visited_pages) >= self.max_pages:
            return

        page = self._normalize(response.url)
        if page in self.visited_pages:
            return
        self.visited_pages.add(page)

        self.logger.info("Scanning %s", page)

        for href in response.css("a::attr(href)").getall():
            url = self._normalize(urljoin(response.url, href))

            if url.lower().endswith(".pdf") or ".pdf?" in url.lower():
                if url not in self.downloaded_pdfs:
                    self.downloaded_pdfs.add(url)
                    yield scrapy.Request(url, callback=self.save_pdf, dont_filter=True)
                continue

            if not self._is_legal_page(url):
                continue

            if url not in self.visited_pages and len(self.visited_pages) < self.max_pages:
                yield scrapy.Request(url, callback=self.parse)

    def save_pdf(self, response):
        filename = unquote(urlparse(response.url).path.split("/")[-1])
        if not filename.lower().endswith(".pdf"):
            filename = f"{filename}.pdf"

        filepath = self.download_dir / filename
        if filepath.exists():
            self.logger.info("Exists %s", filename)
            return

        filepath.write_bytes(response.body)
        self.logger.info("Saved %s (%d bytes)", filename, len(response.body))
