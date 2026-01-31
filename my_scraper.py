import os, requests, time, random, csv, urllib.parse
from faker import Faker

def run_scraper():
    file_path = 'raw_harvest.csv'
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'QueryUsed', 'RawTextDump'])

    engine = os.getenv('ENGINE', 'google')
    manual_query = os.getenv('UI_QUERY')
    loc = os.getenv('UI_LOCATION')
    raw_d = os.getenv('UI_DOMAINS', 'talktalk.net, gmx.com')
    target_domains = [d.strip() for d in raw_d.split(',')]
    
    fake = Faker()
    roles = ["CEO", "Owner", "Manager", "Director"]

    for attempt in range(3): # Harvest 3 pages of results
        # LOGIC: Use manual query if provided, otherwise auto-generate
        if manual_query:
            full_query = manual_query
        else:
            role = random.choice(roles)
            name = fake.first_name()
            location = loc if loc else f"{fake.city()}, {fake.country()}"
            domain_query = " OR ".join([f'"@{d}"' for d in target_domains])
            full_query = f'"{name}" {role} "{location}" {domain_query}'
        
        print(f"--- Harvesting Page {attempt+1} ---", flush=True)
        print(f"Query: {full_query}", flush=True)
        
        # Add pagination to the query
        url = f"https://www.{engine}.com/search?q={full_query.replace(' ', '+')}"
        if engine != 'duckduckgo':
            url += f"&start={attempt * 10}"

        try:
            time.sleep(random.uniform(12, 25))
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
            
            if response.status_code == 200:
                decoded_content = urllib.parse.unquote(response.text)
                with open(file_path, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([time.strftime("%Y-%m-%d %H:%M"), full_query, decoded_content])
                print(f"SUCCESS: Data dumped to {file_path}", flush=True)
            else:
                print(f"Blocked (Status {response.status_code})", flush=True)
        except Exception as e:
            print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    run_scraper()
