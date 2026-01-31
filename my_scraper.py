import os, requests, time, random, csv, urllib.parse
from faker import Faker

def run_scraper():
    # 1. Capture Environment Variables
    engine = os.getenv('ENGINE', 'google')
    depth = int(os.getenv('DEPTH', '3'))
    manual_query = os.getenv('UI_QUERY')
    mode = os.getenv('UI_MODE', 'csv_rows')
    loc = os.getenv('UI_LOCATION')
    raw_d = os.getenv('UI_DOMAINS', 'talktalk.net, gmx.com')
    target_domains = [d.strip() for d in raw_d.split(',')]
    
    fake = Faker()
    roles = ["CEO", "Owner", "Manager", "Director"]

    # 2. Generate a Unique Timestamped Filename
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    file_ext = 'csv' if mode == 'csv_rows' else 'txt'
    file_path = f'harvest_{timestamp}.{file_ext}'

    # 3. Loop through Search Depth
    for page in range(depth):
        if manual_query:
            full_query = manual_query
        else:
            role = random.choice(roles)
            name = fake.first_name()
            location = loc if loc else f"{fake.city()}, {fake.country()}"
            domain_query = " OR ".join([f'"@{d}"' for d in target_domains])
            full_query = f'"{name}" {role} "{location}" {domain_query}'
        
        print(f"--- Harvesting Page {page+1} of {depth} | Engine: {engine} ---", flush=True)
        
        # Build URL with pagination
        url = f"https://www.{engine}.com/search?q={full_query.replace(' ', '+')}"
        if engine != 'duckduckgo':
            url += f"&start={page * 10}"

        try:
            # Random delay for stealth
            time.sleep(random.uniform(15, 30))
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
            
            if response.status_code == 200:
                # Clean URL-encoded characters (e.g. %22)
                content = urllib.parse.unquote(response.text)
                
                if mode == 'csv_rows':
                    file_exists = os.path.exists(file_path)
                    with open(file_path, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        if not file_exists: 
                            writer.writerow(['Timestamp', 'Query', 'RawContent'])
                        writer.writerow([time.strftime("%Y-%m-%d %H:%M"), full_query, content])
                else:
                    with open(file_path, 'a', encoding='utf-8') as f:
                        f.write(f"\n--- PAGE {page+1} HARVEST | QUERY: {full_query} ---\n")
                        f.write(content)
                
                print(f"SUCCESS: Page {page+1} data saved to {file_path}", flush=True)
            else:
                print(f"Blocked on page {page+1} (Status {response.status_code})", flush=True)
                break 
        except Exception as e:
            print(f"Error on page {page+1}: {e}", flush=True)
            continue

if __name__ == "__main__":
    run_scraper()
