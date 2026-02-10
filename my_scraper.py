import os, requests, re, time, random, urllib.parse
from faker import Faker

def lite_16_extractor(text, separator='\n'):
    """Implements the Lite 1.6 logic: Pattern matching + Deduplication + Formatting"""
    # Standard Lite 1.6 Regex pattern
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    # 1. Parsing: URL Unquoting to handle obfuscated emails
    decoded_text = urllib.parse.unquote(text)
    
    # 2. Extraction: Find all matches in the block
    found_emails = re.findall(email_pattern, decoded_text)
    
    # 3. Deduplication: Lite 1.6 automatically removes duplicates
    unique_emails = sorted(list(set([e.lower() for e in found_emails])))
    
    # 4. Formatting: Joins emails using the specified separator (Lite 1.6 default is newline)
    return separator.join(unique_emails)

def run_scraper():
    engine = os.getenv('ENGINE', 'google')
    manual_query = os.getenv('UI_QUERY')
    depth = int(os.getenv('DEPTH', '5'))
    
    # Unique filename for this batch
    timestamp = time.strftime("%Y%m%d_%H%M")
    output_file = f'lite16_harvest_{timestamp}.txt'
    
    fake = Faker()
    all_raw_data = ""

    print(f"--- Lite 1.6 Bulk Mode: {engine.upper()} ---", flush=True)

    for page in range(depth):
        query = manual_query if manual_query else f'"{fake.first_name()}" CEO "@talktalk.net"'
        print(f"Processing Page {page+1} for: {query}", flush=True)
        
        url = f"https://www.{engine}.com/search?q={query.replace(' ', '+')}"
        if engine != 'duckduckgo': url += f"&start={page * 10}"

        try:
            # Lite 1.6 style requires capturing the full HTML source first
            time.sleep(random.uniform(10, 20))
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            res = requests.get(url, headers=headers, timeout=20)
            
            if res.status_code == 200:
                all_raw_data += res.text
            else:
                print(f"Engine blocked (Status {res.status_code})", flush=True)
                break
        except Exception as e:
            print(f"Error: {e}", flush=True)

    # Apply Lite 1.6 logic to the entire harvested block
    clean_list = lite_16_extractor(all_raw_data)
    
    if clean_list:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(clean_list)
        print(f"SUCCESS: Extracted leads saved to {output_file}", flush=True)
    else:
        print("No emails found in this batch.", flush=True)

if __name__ == "__main__":
    run_scraper()
