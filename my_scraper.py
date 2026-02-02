import os, requests, re, time, random, csv, urllib.parse
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess

# 1. THE EXTRACTION ENGINE (Inspired by ansifi tool)
class DeepEmailSpider(CrawlSpider):
    name = 'deep_email_spider'
    rules = (Rule(LinkExtractor(allow=(), deny_extensions=()), callback='parse_item', follow=True),)

    def __init__(self, *args, **kwargs):
        super(DeepEmailSpider, self).__init__(*args, **kwargs)
        self.start_urls = [kwargs.get('url')]
        self.allowed_domains = [kwargs.get('url').split("//")[-1].split("/")[0]]
        self.target_domains = ['talktalk.net', 'gmx.com', 'tiscali.co.uk']
        self.output_file = kwargs.get('output_file')

    def parse_item(self, response):
        # Extract emails from the actual website source
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response.text)
        valid = {e.lower() for e in emails if any(d in e.lower() for d in self.target_domains)}
        
        if valid:
            with open(self.output_file, 'a', newline='') as f:
                writer = csv.writer(f)
                for email in valid:
                    writer.writerow([email, response.url, time.strftime("%Y-%m-%d")])
        return None

# 2. THE SEARCH ENGINE HARVESTER
def run_master_harvest():
    engine = os.getenv('ENGINE', 'google')
    manual_query = os.getenv('UI_QUERY')
    depth = int(os.getenv('DEPTH', '1'))
    
    timestamp = time.strftime("%Y%m%d_%H%M")
    results_file = f'final_leads_{timestamp}.csv'
    
    # Initialize CSV
    with open(results_file, 'w', newline='') as f:
        writer = csv.writer(f); writer.writerow(['Email', 'Source_URL', 'Date'])

    # Search for sites
    search_query = manual_query if manual_query else '"CEO" "@talktalk.net"'
    print(f"--- Searching {engine} for leads... ---", flush=True)
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    search_url = f"https://www.{engine}.com/search?q={search_query.replace(' ', '+')}"
    
    try:
        res = requests.get(search_url, headers=headers, timeout=20)
        # Extract 20 unique website links from the search results
        links = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', res.text)
        target_sites = list(set([l for l in links if "google" not in l and "facebook" not in l]))[:20]

        # 3. RUN DEEP CRAWL ON EACH SITE
        process = CrawlerProcess({'USER_AGENT': 'Mozilla/5.0', 'LOG_LEVEL': 'INFO'})
        for site in target_sites:
            print(f"Launching Deep Crawl on: {site}", flush=True)
            process.crawl(DeepEmailSpider, url=site, output_file=results_file)
        process.start()
    except Exception as e:
        print(f"Master Error: {e}", flush=True)

if __name__ == "__main__":
    run_master_harvest()
