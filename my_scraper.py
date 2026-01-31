import os, requests, re, time, random, csv, urllib.parse
from faker import Faker

def extract_emails(text):
    """Decodes URL junk and extracts valid email patterns"""
    decoded = urllib.parse.unquote(text)
    return re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', decoded)

def run_scraper():
    # Setup unique CSV file for the run
    timestamp = time.strftime("%Y%m%d_%H%M")
    file_path = f'harvest_{timestamp}.csv'
    
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Email', 'Source_URL', 'Query', 'Date'])

    engine = os.getenv('ENGINE', 'google')
    depth = int(os.getenv('DEPTH', '3'))
    manual_query = os.getenv('UI_QUERY')
    target_domains = ['talktalk.net', 'gmx.com', 'tiscali.co.uk']
    
    fake = Faker()
    print(f"--- Extraction Mode Active: {file_path} ---", flush=True)

    for page in range(depth):
        query = manual_query if manual_query else f'"{fake.first_name()}" CEO "@talktalk.net"'
        print(f"--- Processing Page {page+1} ---", flush=True)
        
        search_url = f"https://www.{engine}.com/search?q={query.replace(' ', '+')}"
        if engine != 'duckduckgo': search_url += f"&start={page * 10}"

        try:
            time.sleep(random.uniform(15, 25))
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            res = requests.get(search_url, headers=headers, timeout=20)
            
            if res.status_code == 200:
                # Find links that aren't search engine internal links
                links = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', res.text)
                clean_links = [l for l in links if "google" not in l and "facebook" not in l]
                
                # CURRENT LIMIT: Visiting the top 5 unique links per page
                target_links = list(set(clean_links))[:5] 
                
                for link in target_links:
                    try:
                        print(f"Visiting: {link}", flush=True)
                        site_res = requests.get(link, headers=headers, timeout=10)
                        emails = extract_emails(site_res.text)
                        
                        valid = [e.lower() for e in emails if any(d in e.lower() for d in target_domains)]
                        
                        if valid:
                            with open(file_path, 'a', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                for email in set(valid):
                                    writer.writerow([email, link, query, time.strftime("%Y-%m-%d")])
                    except:
                        continue
            else:
                print(f"Blocked (Status {res.status_code})", flush=True)
                break 
        except Exception as e:
            print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    run_scraper()
