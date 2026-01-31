import os, requests, re, time, random, csv
from faker import Faker
from bs4 import BeautifulSoup

def extract_emails_from_text(text):
    """High-sensitivity regex for finding emails in raw text"""
    return re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)

def run_scraper():
    file_path = 'results.csv'
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Email', 'Source_URL', 'Date'])

    engine = os.getenv('ENGINE', 'google')
    manual_query = os.getenv('UI_QUERY')
    target_domains = ["talktalk.net", "gmx.com", "tiscali.co.uk"]
    
    # 1. Generate Search URL
    query = manual_query if manual_query else f'"CEO" "{Faker().city()}" "@talktalk.net"'
    search_url = f"https://www.{engine}.com/search?q={query.replace(' ', '+')}"
    
    print(f"--- Searching {engine}: {query} ---", flush=True)

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(search_url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            # 2. Find all links on the search page
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if "/url?q=" in href: # Google specific link format
                    links.append(href.split("/url?q=")[1].split("&")[0])
                elif href.startswith("http") and "google" not in href:
                    links.append(href)

            # 3. Visit each link to find emails
            for link in list(set(links))[:5]: # Limit to top 5 links to avoid timeouts
                print(f"Visiting: {link}", flush=True)
                try:
                    site_res = requests.get(link, headers=headers, timeout=15)
                    found = extract_emails_from_text(site_res.text)
                    
                    valid = [e.lower() for e in found if any(d in e.lower() for d in target_domains)]
                    
                    if valid:
                        with open(file_path, 'a', newline='') as f:
                            writer = csv.writer(f)
                            for email in set(valid):
                                writer.writerow(["Target", email, link, time.strftime("%Y-%m-%d")])
                        print(f"SUCCESS: Found {len(set(valid))} emails on {link}", flush=True)
                except:
                    continue
        else:
            print(f"Search engine blocked (Status {response.status_code})", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    run_scraper()
