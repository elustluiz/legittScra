import os, requests, re, time, random, csv
from faker import Faker

def get_free_proxies():
    """Phase 2 Fallback Proxies"""
    print("Sourcing fallback proxies...", flush=True)
    sources = ["https://www.proxy-list.download/api/v1/get?type=https"]
    try:
        r = requests.get(sources[0], timeout=10)
        return [p.strip() for p in r.text.split('\n') if p.strip()]
    except: return []

def run_scraper():
    # 1. Always initialize the CSV to fix the 'No Changes' error
    if not os.path.exists('results.csv'):
        with open('results.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Name','Email','Role','Location','Date','Source'])

    engine = os.getenv('ENGINE', 'google')
    loc = os.getenv('UI_LOCATION')
    raw_d = os.getenv('UI_DOMAINS', 'talktalk.net, gmx.com')
    target_domains = [d.strip() for d in raw_d.split(',')]
    
    fake = Faker()
    # Dynamic Rotation
    roles = ["CEO", "Owner", "Manager", "Director", "Treasurer"]
    
    proxy_pool = []
    use_proxy = False
    max_retries = 5 # Number of different names/roles to try if first search fails
    
    for attempt in range(max_retries):
        role = random.choice(roles)
        name = fake.first_name()
        location = loc if loc else f"{fake.city()}, {fake.country()}"
        
        # Broad Search Query
        domain_query = " OR ".join([f'"@{d}"' for d in target_domains])
        full_query = f'"{name}" {role} "{location}" {domain_query}'
        
        print(f"--- Attempt {attempt+1}: Searching {role} ({name}) in {location} ---", flush=True)
        
        url = f"https://www.{engine}.com/search?q={full_query.replace(' ', '+')}"
        proxies = None
        if use_proxy:
            if not proxy_pool: proxy_pool = get_free_proxies()
            if proxy_pool:
                p = random.choice(proxy_pool)
                proxies = {"http": f"http://{p}", "https": f"http://{p}"}

        try:
            time.sleep(random.uniform(8, 15))
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, 
                                    proxies=proxies, timeout=12)
            
            if response.status_code == 200:
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response.text)
                valid = [[name, e.lower(), role, location, time.strftime("%Y-%m-%d"), engine] 
                         for e in emails if any(d in e.lower() for d in target_domains)]
                
                if valid:
                    with open('results.csv', 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerows(valid)
                    print(f"SUCCESS: Found {len(valid)} emails. Ending run.", flush=True)
                    break # Stop retrying once data is found
                else:
                    print("No emails found. Retrying with new identity...", flush=True)
            else:
                print(f"Blocked (Status {response.status_code}). Switching to Proxy Phase...", flush=True)
                use_proxy = True
        except:
            use_proxy = True
            continue

if __name__ == "__main__":
    run_scraper()
