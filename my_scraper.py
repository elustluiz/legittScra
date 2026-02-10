import os, requests, re, time, random, urllib.parse
from faker import Faker

def run_scraper():
    engine = os.getenv('ENGINE', 'google')
    manual_query = os.getenv('UI_QUERY')
    
    fake = Faker()
    # Unique timestamp for your ProBook file management
    timestamp = time.strftime("%Y%m%d_%H%M")
    file_path = f'harvest_{timestamp}.txt'
    
    # BROAD QUERY: Removed the '-email' restriction to ensure we find leads
    full_query = manual_query if manual_query else f'"{fake.first_name()}" CEO "@talktalk.net"'
    
    print(f"--- Searching {engine}: {full_query} ---", flush=True)
    
    url = f"https://www.{engine}.com/search?q={full_query.replace(' ', '+')}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    try:
        time.sleep(random.uniform(10, 20))
        res = requests.get(url, headers=headers, timeout=20)
        
        if res.status_code == 200:
            # Lite 1.6 Logic: Extract and clean email patterns
            decoded_text = urllib.parse.unquote(res.text)
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', decoded_text)
            unique_emails = sorted(list(set([e.lower() for e in emails])))

            if unique_emails:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(unique_emails))
                print(f"SUCCESS: {len(unique_emails)} emails saved to {file_path}", flush=True)
            else:
                print("Zero emails found in search results.", flush=True)
        else:
            print(f"Blocked by {engine} (Status {res.status_code})", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    run_scraper()
