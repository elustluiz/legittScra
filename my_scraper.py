import os, requests, re, time, random, urllib.parse, html
from faker import Faker

def lite_16_extractor(text):
    """Lite 1.6 logic: Decode, Extract, Deduplicate"""
    clean_text = html.unescape(urllib.parse.unquote(text))
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    found = re.findall(email_pattern, clean_text)
    return sorted(list(set([e.lower() for e in found])))

def run_scraper():
    # Log the VPN IP for tracking
    try:
        ip_info = requests.get('https://ipapi.co/json/', timeout=10).json()
        print(f"--- VPN Active: {ip_info['ip']} ({ip_info['city']}, {ip_info['country_name']}) ---", flush=True)
    except:
        print("--- VPN active but location hidden ---", flush=True)

    engine = os.getenv('ENGINE', 'google')
    manual_query = os.getenv('UI_QUERY')
    depth = 20
    
    timestamp = time.strftime("%Y%m%d_%H%M")
    file_path = f'harvest_{timestamp}.txt'
    fake = Faker()
    
    all_data = ""
    for page in range(depth):
        query = manual_query if manual_query else f'"{fake.first_name()}" CEO "@talktalk.net"'
        url = f"https://www.{engine}.com/search?q={urllib.parse.quote(query)}&start={page * 10}"
        
        try:
            headers = {'User-Agent': fake.chrome()}
            time.sleep(random.uniform(20, 30))
            
            res = requests.get(url, headers=headers, timeout=20)
            if res.status_code == 200:
                all_data += res.text
                print(f"Page {page+1} captured.", flush=True)
            elif res.status_code == 429:
                print(f"Rate limited on page {page+1}. Stopping to save data.", flush=True)
                break
        except: continue

    emails = lite_16_extractor(all_data)
    if emails:
        with open(file_path, 'w', encoding='utf-8') as f:
            # Group into batches of 500
            for i in range(0, len(emails), 500):
                f.write(f"--- BATCH {(i//500)+1} (Size: {len(emails[i:i+500])}) ---\n")
                f.write("\n".join(emails[i:i+500]) + "\n\n")
        print(f"SUCCESS: {len(emails)} emails saved in batches of 500.", flush=True)
    else:
        print("No leads found. The search engine might be serving a CAPTCHA.", flush=True)

if __name__ == "__main__":
    run_scraper()
