import os, requests, time, random, csv, urllib.parse
from faker import Faker

def run_scraper():
    # 1. Initialize the Harvest file
    file_path = 'raw_harvest.csv'
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Location', 'SearchQuery', 'RawTextDump'])

    engine = os.getenv('ENGINE', 'google')
    loc = os.getenv('UI_LOCATION')
    raw_d = os.getenv('UI_DOMAINS', 'talktalk.net, gmx.com')
    target_domains = [d.strip() for d in raw_d.split(',')]
    
    fake = Faker()
    roles = ["CEO", "Owner", "Manager", "Director", "Treasurer"]
    
    # We will run 5 different searches to give you a big block of text
    for attempt in range(5):
        role = random.choice(roles)
        name = fake.first_name()
        location = loc if loc else f"{fake.city()}, {fake.country()}"
        domain_query = " OR ".join([f'"@{d}"' for d in target_domains])
        full_query = f'"{name}" {role} "{location}" {domain_query}'
        
        print(f"--- Harvesting Page {attempt+1}: {role} in {location} ---", flush=True)
        url = f"https://www.{engine}.com/search?q={full_query.replace(' ', '+')}"

        try:
            # Human-like delay to keep the VPN IP alive
            time.sleep(random.uniform(10, 20))
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
            
            if response.status_code == 200:
                # DECODE EVERYTHING: This fixes the %22 junk you saw earlier
                decoded_content = urllib.parse.unquote(response.text)
                
                # We save the raw text dump into the CSV
                with open(file_path, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([location, full_query, decoded_content])
                print(f"SUCCESS: Page content harvested.", flush=True)
            else:
                print(f"Blocked by {engine} (Status {response.status_code}).", flush=True)
        except Exception as e:
            print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    run_scraper()
