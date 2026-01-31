import os, requests, re, time, random, csv, urllib.parse
from faker import Faker

def get_existing_emails(file_path):
    """Reads the CSV and returns a set of already saved emails"""
    emails = set()
    if os.path.exists(file_path):
        with open(file_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'EmailAddress' in row:
                    emails.add(row['EmailAddress'].lower().strip())
    return emails

def clean_and_extract_emails(raw_html, target_domains, existing_emails):
    """Decodes, extracts, and filters out duplicates"""
    decoded_text = urllib.parse.unquote(raw_html)
    all_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', decoded_text)
    
    unique_new = []
    for email in all_emails:
        e_clean = email.lower().strip().strip('"').strip("'")
        # Only add if it matches domain AND isn't already in our CSV
        if any(d in e_clean for d in target_domains) and e_clean not in existing_emails:
            unique_new.append(e_clean)
            existing_emails.add(e_clean) # Add to set to prevent duplicates in same run
    return list(set(unique_new))

def run_scraper():
    file_path = 'results.csv'
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Name','EmailAddress','Role','Location','Date','Source'])

    existing_emails = get_existing_emails(file_path)
    engine = os.getenv('ENGINE', 'google')
    loc = os.getenv('UI_LOCATION')
    raw_d = os.getenv('UI_DOMAINS', 'talktalk.net, gmx.com')
    target_domains = [d.strip() for d in raw_d.split(',')]
    
    fake = Faker()
    roles = ["CEO", "Owner", "Manager", "Director"]
    
    for attempt in range(5):
        role = random.choice(roles)
        name = fake.first_name()
        location = loc if loc else f"{fake.city()}, {fake.country()}"
        full_query = f'"{name}" {role} "{location}" ' + " OR ".join([f'"@{d}"' for d in target_domains])
        
        print(f"--- Attempt {attempt+1}: Harvesting {engine.upper()} for {role} ---", flush=True)
        url = f"https://www.{engine}.com/search?q={full_query.replace(' ', '+')}"

        try:
            time.sleep(random.uniform(10, 20))
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            
            if response.status_code == 200:
                new_emails = clean_and_extract_emails(response.text, target_domains, existing_emails)
                
                if new_emails:
                    with open(file_path, 'a', newline='') as f:
                        writer = csv.writer(f)
                        for email in new_emails:
                            writer.writerow([name, email, role, location, time.strftime("%Y-%m-%d"), engine])
                    print(f"SUCCESS: Added {len(new_emails)} new unique leads.", flush=True)
                else:
                    print("No new unique emails found in this search.", flush=True)
            else:
                print(f"Engine blocked (Status {response.status_code}).", flush=True)
        except Exception as e:
            print(f"Connection error: {e}", flush=True)

if __name__ == "__main__":
    run_scraper()
