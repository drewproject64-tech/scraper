# Social Prospect Scraper

Scrapy Cloud spider for processing publicly accessible pages on Facebook, Instagram, Twitter/X, or other sites.

Spider: `social_prospects`

Arguments:
- `start_urls`: comma-separated public URLs to process
- `platforms`: facebook,instagram,twitter
- `keywords`: optional keywords separated by `|`; defaults to the built-in Telegram advertising/marketing list
- `max_pages`: default 100

The spider extracts only emails publicly present in the retrieved page HTML and filters them to the requested public email domains.

Important: this is not a login or anti-bot bypass tool. It does not access private profiles, bypass CAPTCHAs, or defeat access controls. Social platforms may also return limited/JavaScript-rendered content to automated clients.

For broad keyword discovery, use a permitted public search source or provide public profile/page URLs as `start_urls`, then let the spider inspect those pages.

Example:
`start_urls=https://example.com/public-page&platforms=facebook,instagram,twitter&max_pages=100`

