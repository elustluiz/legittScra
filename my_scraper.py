import os
import requests
import re
import time
import random
import csv
from faker import Faker

def get_free_proxies():
    """Fallback proxy source for Phase 2"""
    print("Sourcing fallback proxies...", flush=True)
    sources = [
        "https://www.proxy-list.download/api/v1/get?type=https",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
    ]
    proxies = []
    for url in sources:
        try:
            response = requests.get(url, timeout=10)
            proxies.extend([p.strip() for p in response.text.split('\n') if p.strip()])
        except: continue
    return list(set(proxies))

def run_scraper():
    # 1. Input Configuration
    engine = os.getenv('ENGINE', 'google')
    raw_domains = os.getenv('UI_DOMAINS') or os.getenv('TARGET_DOMAINS', 'gmx.com')
    target_domains = [d.strip() for d in raw_domains.split(',')]
    keywords = os.getenv('UI_KEYWORDS') or os.getenv('SEARCH_BASE_QUERY', 'CEO')
    
    fake = Faker('en_US')
    name = fake.first_name()
    domain_query = " OR ".join([f'"@{d}"' for d in target_domains])
    full_query = f"{name} {keywords} {domain_query}"
    
    # 2. Engine Routing
    if engine == 'bing': base_url = "https://www.bing.com/search?q="
    elif engine == 'duckduckgo': base_url = "https://html.duckduckgo.com/html/?q="
    else: base_url = "https://www.google.com/search?q="

    proxy_pool = []
    use_proxy = False # Start with the VPN connection

    print(f"Phase 1: Attempting search via VPN tunnel...", flush=True)

    page = 0
    while page < 3:
        start_idx = page * 10
        url = f"{base_url}{full_query.replace(' ', '+')}"
        if engine != 'duckduckgo': url += f"&start={start_idx}"
        
        # Determine if we use the VPN IP or a Proxy IP
        proxies_config = None
        if use_proxy:
            if not proxy_pool: proxy_pool = get_free_proxies()
            current_p = random.choice(proxy_pool)
            proxies_config = {"http": f"http://{current_p}", "https": f"http://{current_p}"}
            print(f"Phase 2: Rotating Proxy -> {current_p}", flush=True)

        try:
            time.sleep(random.uniform(10, 25)) # Human-like delay
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, 
                                    proxies=proxies_config, timeout=15)
            
            if response.status_code == 200:
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response.text)
                valid = [[name, e.lower(), time.strftime("%Y-%m-%d"), engine] 
                         for e in emails if any(d in e.lower() for d in target_domains)]
                
                if valid:
                    file_exists = os.path.isfile('results.csv')
                    with open('results.csv', 'a', newline='') as f:
                        writer = csv.writer(f)
                        if not file_exists: 
                            writer.writerow(['Name','Email Address','Date Found','Source Engine'])
                        writer.writerows(valid)
                    print(f"SUCCESS: Found {len(valid)} target emails.", flush=True)
                page += 1
            
            elif response.status_code == 429:
                print("IP Blocked (Status 429). Activating Fallback...", flush=True)
                use_proxy = True
            else:
                print(f"Unexpected Status {response.status_code}. Swapping IP...", flush=True)
                use_proxy = True
                
        except Exception as e:
            print(f"Network error: {e}. Moving to next IP...", flush=True)
            use_proxy = True
            continue

if __name__ == "__main__":
    run_scraper()
