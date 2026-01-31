import os, requests, re, time, random, csv, urllib.parse
from faker import Faker

def extract_emails(text):
    """Decodes URL encoding and captures email patterns"""
    # Fixes the encoding issues seen in your earlier results
    decoded = urllib.parse.unquote(text)
    return re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', decoded)

def run_scraper():
    # Setup unique CSV file for your project
    timestamp = time.strftime("%Y%m%d_%H%M")
    file_path = f'harvest_{timestamp}.csv'
    
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Email', 'Source_URL', 'Query', 'Date'])

    engine = os.getenv('ENGINE', 'google')
    depth = int(os.getenv('DEPTH', '3'))
    manual_query = os.getenv('UI_QUERY')
    target_domains = ['talktalk.net', 'gmx.com', 'tiscali.co.uk']
    
    # NEW: Contact Keyword Generator
    contact_keywords = ["Contact Us", "About", "Staff", "Management", "Inquiry"]
    fake = Faker()

    print(f"--- Deep Scan Mode: 20 sites/page with Keyword Rotation ---", flush=True)

    for page in range(depth):
        # Rotate contact keywords to find high-value pages
        suffix = random.choice(contact_keywords)
        if manual_query:
            full_query = f"{manual_query} {suffix}"
        else:
            full_query = f'"{fake.first_name()}" CEO {suffix} "@talktalk.net"'
        
        print(f"--- Page {page+1} | Searching: {full_query} ---", flush=True)
        search_url = f"https://www.{engine}.com/search?q={full_query.replace(' ', '+')}"
        if engine != 'duckduckgo': search_url += f"&start={page * 10}"

        try:
            time.sleep(random.uniform(15, 30)) # Stealth delay
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            res = requests.get(search_url, headers=headers, timeout=20)
            
            if res.status_code == 200:
                # Extract and visit links
                links = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', res.text)
                clean_links = [l for l in links if "google" not in l and "facebook" not in l]
                target_links = list(set(clean_links))[:20] 
                
                for link in target_links:
                    try:
                        print(f"Visiting: {link}", flush=True)
                        site_res = requests.get(link, headers=headers, timeout=12)
                        emails = extract_emails(site_res.text)
                        
                        valid = [e.lower() for e in emails if any(d in e.lower() for d in target_domains)]
                        
                        if valid:
                            with open(file_path, 'a', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                for email in set(valid):
                                    writer.writerow([email, link, full_query, time.strftime("%Y-%m-%d")])
                                    print(f"  [+] Found: {email}", flush=True)
                    except:
                        continue
            else:
                print(f"Blocked (Status {res.status_code})", flush=True)
                break 
        except Exception as e:
            print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    run_scraper()
