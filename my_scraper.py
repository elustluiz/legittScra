import os, requests, re, time, random, urllib.parse
from faker import Faker

def lite_16_batch_extractor(text, batch_size=500):
    """Lite 1.6 Logic: Extract, Deduplicate, and Group"""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    decoded_text = urllib.parse.unquote(text)
    found_emails = re.findall(email_pattern, decoded_text)
    unique_emails = sorted(list(set([e.lower() for e in found_emails])))
    
    batched_output = []
    for i in range(0, len(unique_emails), batch_size):
        batch_num = (i // batch_size) + 1
        batched_output.append(f"--- BATCH {batch_num} (Count: {len(unique_emails[i:i+batch_size])}) ---")
        batched_output.extend(unique_emails[i:i+batch_size])
        batched_output.append("\n")
        
    return "\n".join(batched_output), len(unique_emails)

def run_scraper():
    engine = os.getenv('ENGINE', 'google')
    manual_query = os.getenv('UI_QUERY')
    # Automatically reads '20' from the workflow dropdown
    depth = int(os.getenv('DEPTH', '20')) 
    
    timestamp = time.strftime("%Y%m%d_%H%M")
    output_file = f'harvest_{timestamp}.txt'
    
    fake = Faker()
    all_raw_data = ""

    print(f"--- Starting {depth}-Page High Volume Harvest ---", flush=True)

    for page in range(depth):
        query = manual_query if manual_query else f'"{fake.first_name()}" CEO "@talktalk.net"'
        print(f"Page {page+1}: {query}", flush=True)
        
        # Start parameter increases by 10 per page
        url = f"https://www.{engine}.com/search?q={query.replace(' ', '+')}&start={page * 10}"

        try:
            # Extended delay for 20-page safety
            time.sleep(random.uniform(15, 25))
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
            if res.status_code == 200:
                all_raw_data += res.text
            else:
                print(f"Blocked at page {page+1}", flush=True)
                break
        except:
            continue

    clean_content, total_count = lite_16_batch_extractor(all_raw_data)
    
    if total_count > 0:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(clean_content)
        print(f"SUCCESS: {total_count} leads saved in batches of 500.", flush=True)
    else:
        print("No leads found. Verify query filters.", flush=True)

if __name__ == "__main__":
    run_scraper()
