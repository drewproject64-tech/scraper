import re
from urllib.parse import urlparse

import scrapy

EMAIL_RE = re.compile(
    r"""(?i)\b[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+\b"""
)

PLATFORMS = {
    "facebook": "facebook.com",
    "instagram": "instagram.com",
    "twitter": "twitter.com",
    "x": "x.com",
}

KEYWORDS = [
    "telegram ads", "telegram advertising", "telegram marketing",
    "telegram promotion", "telegram paid advertising", "telegram paid traffic",
    "telegram media buying", "telegram ad campaign", "telegram advertising campaign",
    "telegram ads campaign", "telegram ads manager", "telegram advertising manager",
    "telegram ads agency", "telegram advertising agency", "telegram marketing agency",
    "telegram promotion agency", "telegram growth agency", "telegram ads service",
    "telegram advertising service", "telegram marketing service", "telegram promotion service",
    "telegram ads expert", "telegram ads specialist", "telegram advertising specialist",
    "telegram marketing specialist", "telegram media buyer", "telegram advertising consultant",
    "telegram marketing consultant", "telegram growth consultant", "telegram channel advertising",
    "telegram channel promotion", "telegram channel marketing", "telegram channel growth",
    "telegram community marketing", "telegram community growth", "telegram audience growth",
    "telegram user acquisition", "telegram customer acquisition", "telegram lead generation",
    "telegram traffic", "telegram audience", "telegram business promotion",
]

EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "live.com", "msn.com", "aol.com",
    "icloud.com", "me.com", "mac.com", "proton.me", "protonmail.com", "pm.me", "zoho.com",
    "zohomail.com", "gmx.com", "gmx.net", "mail.com", "fastmail.com", "fastmail.fm", "hey.com",
    "tuta.com", "tutanota.com", "mailfence.com", "hushmail.com", "runbox.com", "mailbox.org",
    "posteo.de", "posteo.net", "disroot.org", "riseup.net", "startmail.com", "duck.com",
    "web.de", "t-online.de", "freenet.de", "online.de", "arcor.de", "seznam.cz", "centrum.cz",
    "atlas.cz", "volny.cz", "wp.pl", "o2.pl", "interia.pl", "onet.pl", "poczta.pl", "libero.it",
    "virgilio.it", "email.it", "aruba.it", "tiscali.it", "orange.fr", "free.fr", "sfr.fr",
    "wanadoo.fr", "laposte.net", "btinternet.com", "btopenworld.com", "sky.com", "talktalk.net",
    "virginmedia.com", "plus.net", "rogers.com", "shaw.ca", "bell.net", "telus.net",
    "videotron.ca", "bigpond.com", "optusnet.com.au", "telstra.com", "rediffmail.com", "sify.com",
    "indiatimes.com", "qq.com", "163.com", "126.com", "sina.com", "sohu.com", "yeah.net",
    "foxmail.com", "naver.com", "daum.net", "hanmail.net", "mail.kz", "ukr.net", "i.ua",
    "mail.ua", "mail.bg", "abv.bg", "zoznam.sk", "azet.sk",
}

class SocialProspectsSpider(scrapy.Spider):
    name = "social_prospects"

    def __init__(self, start_urls=None, keywords=None, platforms="facebook,instagram,twitter",
                 max_pages=100, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [u.strip() for u in (start_urls or "").split(",") if u.strip()]
        if not self.start_urls:
            raise ValueError("start_urls is required. Supply public search/result URLs or public profile/page URLs.")
        self.keywords = [k.strip().lower() for k in (keywords or "").split("|") if k.strip()] or KEYWORDS
        self.platforms = {p.strip().lower() for p in platforms.split(",") if p.strip()}
        self.max_pages = max(1, int(max_pages))
        self.seen = set()
        self.count = 0

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, errback=self.errback, dont_filter=True)

    def parse(self, response):
        if self.count >= self.max_pages or response.url in self.seen:
            return
        self.seen.add(response.url)
        self.count += 1

        host = (urlparse(response.url).hostname or "").lower()
        platform = next((p for p, domain in PLATFORMS.items() if host == domain or host.endswith("." + domain)), "")
        if platform and platform not in self.platforms:
            return

        title = response.css("title::text").get(default="").strip()
        description = response.css('meta[name="description"]::attr(content)').get(default="").strip()
        body = " ".join(response.css("body ::text").getall())
        visible_text = f"{title} {description} {body}"
        lower = visible_text.lower()

        matched_keywords = [k for k in self.keywords if k in lower]
        all_emails = sorted(set(EMAIL_RE.findall(visible_text)))
        matched_emails = [
            e for e in all_emails
            if e.rsplit("@", 1)[-1].lower() in EMAIL_DOMAINS
        ]

        if matched_keywords or matched_emails:
            yield {
                "platform": platform or "other",
                "url": response.url,
                "title": title,
                "description": description,
                "matched_keywords": matched_keywords,
                "emails": matched_emails,
            }

        if self.count >= self.max_pages:
            return

        for href in response.css("a::attr(href)").getall():
            next_url = response.urljoin(href)
            next_host = (urlparse(next_url).hostname or "").lower()
            if not next_host:
                continue
            if next_host == host or next_host.endswith("." + host):
                yield scrapy.Request(next_url, callback=self.parse, errback=self.errback)

    def errback(self, failure):
        self.logger.warning("Request failed: %s", failure.request.url)
