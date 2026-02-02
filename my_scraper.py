import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re
import os
import csv
import time

class EmailSpider(CrawlSpider):
    name = 'email_spider'
    
    # Logic: Follow internal links to find deeper pages like /contact or /about
    rules = (
        Rule(LinkExtractor(allow=(), deny_extensions=()), callback='parse_item', follow=True),
    )

    def __init__(self, *args, **kwargs):
        super(EmailSpider, self).__init__(*args, **kwargs)
        # Use the provided URL from GitHub Actions or a default
        self.start_url = kwargs.get('url', 'https://www.talktalk.co.uk')
        self.start_urls = [self.start_url]
        self.allowed_domains = [self.start_url.split("//")[-1].split("/")[0]]
        self.target_domains = ['talktalk.net', 'gmx.com', 'tiscali.co.uk']
        
        # Unique CSV for your ProBook results
        self.results_file = f"test_harvest_{time.strftime('%Y%m%d_%H%M')}.csv"
        with open(self.results_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Email', 'Source_URL', 'Status'])

    def parse_item(self, response):
        # Scan raw HTML text for emails
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response.text)
        
        valid_found = False
        for email in set(emails):
            email_lower = email.lower()
            # Only save if it matches your target list
            if any(domain in email_lower for domain in self.target_domains):
                valid_found = True
                with open(self.results_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([email_lower, response.url, 'SUCCESS'])
        
        if valid_found:
            self.logger.info(f"MATCH FOUND on {response.url}")
        return None
