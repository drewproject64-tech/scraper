# Scraper — Scrapy Cloud

A small Scrapy project for collecting data from publicly accessible web pages. It extracts page metadata and contact emails that are publicly present in the HTML.

## Spider: public_pages

Arguments:
- start_url: required
- keyword: optional
- max_pages: optional, default 20

Example:
scrapy crawl public_pages -a start_url=https://example.com -a keyword=marketing -a max_pages=20 -O results.csv

The spider does not log in, bypass CAPTCHAs, access private profiles, or defeat access controls. Only publicly accessible page content is processed.

## Deploy to Scrapy Cloud

pip install shub
shub login
shub deploy 878830

Never commit API keys, passwords, cookies, or other secrets.
