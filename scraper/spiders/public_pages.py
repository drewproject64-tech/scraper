import re
from urllib.parse import urljoin, urlparse

import scrapy

from scraper.items import PublicPageItem

EMAIL_RE = re.compile(
    r"""(?i)\b[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+\b"""
)

class PublicPagesSpider(scrapy.Spider):
    name = "public_pages"

    def __init__(self, start_url=None, keyword="", max_pages=20, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not start_url:
            raise ValueError("start_url is required")
        self.start_url = start_url
        self.keyword = (keyword or "").strip().lower()
        try:
            self.max_pages = max(1, int(max_pages))
        except (TypeError, ValueError):
            self.max_pages = 20
        self.seen = set()
        self.count = 0
        hostname = urlparse(start_url).hostname
        self.allowed_domains = [hostname] if hostname else []

    def start_requests(self):
        yield scrapy.Request(
            self.start_url,
            callback=self.parse,
            errback=self.errback,
            dont_filter=True,
        )

    def parse(self, response):
        if self.count >= self.max_pages or response.url in self.seen:
            return

        self.seen.add(response.url)
        self.count += 1

        title = response.css("title::text").get(default="").strip()
        description = response.css(
            'meta[name="description"]::attr(content)'
        ).get(default="").strip()

        body = " ".join(response.css("body ::text").getall())
        emails = sorted(set(EMAIL_RE.findall(body + " " + response.text)))
        haystack = f"{title} {description} {body}".lower()

        item = PublicPageItem(
            url=response.url,
            title=title,
            description=description,
            keyword_match=(not self.keyword) or (self.keyword in haystack),
            emails=emails,
        )

        if item["keyword_match"] or emails:
            yield item

        if self.count >= self.max_pages:
            return

        for href in response.css("a::attr(href)").getall():
            next_url = urljoin(response.url, href)
            parsed = urlparse(next_url)

            if parsed.scheme not in {"http", "https"}:
                continue
            if not parsed.hostname or parsed.hostname != self.allowed_domains[0]:
                continue
            if next_url in self.seen:
                continue

            yield response.follow(
                next_url,
                callback=self.parse,
                errback=self.errback,
            )

    def errback(self, failure):
        self.logger.warning("Request failed: %s", failure.request.url)
