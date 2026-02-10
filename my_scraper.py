import os, requests, re, time, random, urllib.parse
from faker import Faker

def lite_16_batch_test(text, batch_size=500):
    """Lite 1.6 Logic: Pattern Matching, Deduplication, and Batching"""
    # Pattern to find valid emails in raw HTML
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    # Clean the raw data to reveal hidden emails
    decoded_text = urllib.parse.unquote(text)
    found_emails = re.findall(email_pattern, decoded_text)
    
    # Remove duplicates and sort alphabetically (Lite 1.6 style)
    unique_emails = sorted(list(set([e.lower() for e in found_emails])))
    
    # Organize into batches of 500
    batched_output = []
    for i in range(0, len(unique_emails), batch_size):
        batch_num = (i // batch_size) + 1
        batched_output.append(f"--- TEST BATCH {batch_num} (Total: {len(unique_emails[i:i+batch_size])}) ---")
        batched_output.extend(unique_emails[i:i+batch_size])
        batched_output.append("\n")
        
    return "\n".join(batched_output), len(unique_emails)

def run_test_scraper():
    engine = os.getenv('ENGINE', 'google')
    # Using a broad test query to ensure we capture data
    manual_query = os.getenv('UI_QUERY', 'contact "@talktalk.net"')
    depth = 10 # 10 pages ensure a larger dataset for the test
    
    timestamp = time.strftime("%Y%m%d_%H%M")
    output_file = f'test_lite16_batch_{timestamp}.txt'
    
    all_raw_data = ""
    print(f"--- DIAGNOSTIC TEST: Lite 1.6 Batching (10 Pages) ---", flush=True)

    for page in range(depth):
        print(f"Harvesting Page {page+1}...", flush=True)
        url = f"https://www.{engine}.com/search?q={manual_query.replace(' ', '+')}&start={page * 10}"
        
        try:
            time.sleep(random.uniform(10, 20)) # Stealth delay to avoid blocks
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            res = requests.get(url, headers=headers, timeout=20)
            if res.status_code == 200:
                all_raw_data += res.text
            else:
                print(f"Blocked on Page {page+1} (Status {res.status_code})", flush=True)
                break
        except Exception as e:
            print(f"Error on Page {page+1}: {e}", flush=True)

    # Apply batching logic
    clean_content, total_count = lite_16_batch_test(all_raw_data, batch_size=500)
    
    if total_count > 0:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(clean_content)
        print(f"TEST SUCCESS: {total_count} leads saved to {output_file}", flush=True)
    else:
        print("TEST FAILED: No emails found. Try a broader search query.", flush=True)

if __name__ == "__main__":
    run_test_scraper()
