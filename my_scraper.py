import os
import requests
import re
import time
import random
import csv
from faker import Faker

def get_free_proxies():
    try:
        url = "https://www.proxy-list.download/api/v1/get?type=https"
        return [p.strip() for p in requests.get(url, timeout=10).text.split('\r\n') if p.strip()]
    except: return []

def run_scraper():
    # 1. Inputs
    engine = os.getenv('ENGINE', 'google')
    raw_domains = os.getenv('UI_DOMAINS') or os.getenv('TARGET_DOMAINS', 'gmx.com')
    target_domains = [d.strip() for d in raw_domains.split(',')]
    keywords = os.getenv('UI_KEYWORDS') or os.getenv('SEARCH_BASE_QUERY', 'CEO')
    
    fake = Faker('en_US')
    name = fake.first_name()
    domain_query = " OR ".join([f'"@{d}"' for d in target_domains])
    full_query = f"{name} {keywords} {domain_query}"
    
    # 2. Engine Logic
    # DuckDuckGo uses 'q' for query but handles pagination differently (html version used for scraping)
    if engine == 'bing':
        base_url = "https://www.bing.com/search?q="
    elif engine == 'duckduckgo':
        base_url = "https://html.duckduckgo.com/html/?q="
    else:
        base_url = "https://www.google.com/search?q="

    proxy_list = get_free_proxies()
    
    # 3. Scraping Loop
    page = 0
    while page < 3:
        # Google/Bing use 'start', DDG HTML is usually a single long scroll or specific 'v' params
        start_idx = page * 10
        url = f"{base_url}{full_query.replace(' ', '+')}"
        if engine != 'duckduckgo': # Add pagination for Google/Bing
            url += f"&start={start_idx}"
        
        current_proxy = random.choice(proxy_list) if proxy_list else None
        proxies = {"http": f"http://{current_proxy}", "https": f"http://{current_proxy}"} if current_proxy else None

        try:
            time.sleep(random.uniform(15, 30))
            print(f"Scraping {engine.upper()} for {name}...")
            
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, proxies=proxies, timeout=20)
            
            if response.status_code == 200:
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response.text)
                valid = [[name, e.lower(), time.strftime("%Y-%m-%d"), engine] 
                         for e in emails if any(d in e.lower() for d in target_domains)]
                
                if valid:
                    file_exists = os.path.isfile('results.csv')
                    with open('results.csv', 'a', newline='') as f:
                        writer = csv.writer(f)
                        if not file_exists: writer.writerow(['Name','Email','Date','Source'])
                        writer.writerows(valid)
                    print(f"Saved {len(valid)} results.")
                
                # Stop if no 'next' found (Simplified for DDG)
                if engine == 'duckduckgo' or "Next" not in response.text: break
                page += 1
            else: 
                print(f"Blocked or Error: {response.status_code}")
                break
        except Exception as e: 
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    run_scraper()
