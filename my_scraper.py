import os
import requests
import re
import time
import random
import csv
from faker import Faker

def get_free_proxies():
    """Sources IPs automatically from multiple public providers"""
    print("Sourcing fresh IPs from public providers...")
    sources = [
        "https://www.proxy-list.download/api/v1/get?type=https",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt"
    ]
    proxies = []
    for url in sources:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                extracted = response.text.split('\n')
                proxies.extend([p.strip() for p in extracted if p.strip()])
        except:
            continue
    print(f"Total IPs sourced: {len(proxies)}")
    return list(set(proxies)) # Remove duplicates

def run_scraper():
    # 1. Inputs & Interface Logic
    engine = os.getenv('ENGINE', 'google')
    raw_domains = os.getenv('UI_DOMAINS') or os.getenv('TARGET_DOMAINS', 'gmx.com')
    target_domains = [d.strip() for d in raw_domains.split(',')]
    keywords = os.getenv('UI_KEYWORDS') or os.getenv('SEARCH_BASE_QUERY', 'CEO')
    
    # Source the IPs
    proxy_pool = get_free_proxies()
    
    fake = Faker('en_US')
    name = fake.first_name()
    domain_query = " OR ".join([f'"@{d}"' for d in target_domains])
    full_query = f"{name} {keywords} {domain_query}"
    
    # 2. Engine Selector
    if engine == 'bing':
        base_url = "https://www.bing.com/search?q="
    elif engine == 'duckduckgo':
        base_url = "https://html.duckduckgo.com/html/?q="
    else:
        base_url = "https://www.google.com/search?q="

    # 3. Scraping Loop
    page = 0
    while page < 3:
        start_idx = page * 10
        url = f"{base_url}{full_query.replace(' ', '+')}"
        if engine != 'duckduckgo': url += f"&start={start_idx}"
        
        # IP Selection Logic
        current_proxy = random.choice(proxy_pool) if proxy_pool else None
        proxies = {"http": f"http://{current_proxy}", "https": f"http://{current_proxy}"} if current_proxy else None

        try:
            time.sleep(random.uniform(15, 30))
            print(f"Using IP: {current_proxy} on {engine.upper()}...")
            
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, proxies=proxies, timeout=20)
            
            if response.status_code == 429:
                print("IP Blocked (Captcha). Swapping IP...")
                if current_proxy in proxy_pool: proxy_pool.remove(current_proxy)
                continue # Retry same page with different IP
                
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
                page += 1
            else: break
        except Exception as e:
            print(f"Connection Error with {current_proxy}. Rotating...")
            if current_proxy in proxy_pool: proxy_pool.remove(current_proxy)
            continue

if __name__ == "__main__":
    run_scraper()
