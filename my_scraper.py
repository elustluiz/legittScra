import os, requests, re, time, random, csv
from faker import Faker

def get_free_proxies():
    print("Sourcing fallback proxies...", flush=True)
    sources = ["https://www.proxy-list.download/api/v1/get?type=https"]
    try:
        r = requests.get(sources[0], timeout=10)
        return [p.strip() for p in r.text.split('\n') if p.strip()]
    except: return []

def run_scraper():
    engine = os.getenv('ENGINE', 'google')
    loc = os.getenv('UI_LOCATION')
    raw_d = os.getenv('UI_DOMAINS') or os.getenv('TARGET_DOMAINS', 'gmx.com')
    target_domains = [d.strip() for d in raw_d.split(',')]
    keywords = os.getenv('UI_KEYWORDS') or os.getenv('SEARCH_BASE_QUERY', 'CEO')
    
    fake = Faker()
    location = loc if loc else f"{fake.city()}, {fake.country()}"
    name = fake.first_name()
    full_query = f"{name} {keywords} \"{location}\" " + " OR ".join([f'"@{d}"' for d in target_domains])
    
    base_url = f"https://www.{engine}.com/search?q={full_query.replace(' ', '+')}"
    proxy_pool = []
    use_proxy = False

    print(f"Targeting: {location}\nUsing Engine: {engine}", flush=True)

    page = 0
    while page < 3:
        url = base_url + (f"&start={page*10}" if engine != 'duckduckgo' else "")
        proxies = None
        if use_proxy:
            if not proxy_pool: proxy_pool = get_free_proxies()
            if proxy_pool:
                p = random.choice(proxy_pool)
                proxies = {"http": f"http://{p}", "https": f"http://{p}"}
                print(f"Phase 2: Swapping to Proxy {p}", flush=True)

        try:
            # STRICT 10s TIMEOUT prevents "hanging"
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, 
                                    proxies=proxies, timeout=10)
            
            if response.status_code == 200:
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response.text)
                valid = [[name, e.lower(), location, time.strftime("%Y-%m-%d"), engine] 
                         for e in emails if any(d in e.lower() for d in target_domains)]
                
                if valid:
                    file_exists = os.path.isfile('results.csv')
                    with open('results.csv', 'a', newline='') as f:
                        writer = csv.writer(f)
                        if not file_exists: writer.writerow(['Name','Email','Location','Date','Source'])
                        writer.writerows(valid)
                    print(f"Saved {len(valid)} results.", flush=True)
                page += 1
            else:
                print(f"Blocked (Status {response.status_code}). Rotating...", flush=True)
                use_proxy = True
        except:
            print("Connection failed. Rotating...", flush=True)
            use_proxy = True

if __name__ == "__main__":
    run_scraper()
