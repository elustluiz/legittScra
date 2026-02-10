import os, requests, re, time, random, urllib.parse
from faker import Faker

def lite_16_batch_extractor(text, batch_size=500):
    """Lite 1.6 Logic: Extract, Deduplicate, and Group by 500"""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    # 1. Clean and Parse
    decoded_text = urllib.parse.unquote(text)
    found_emails = re.findall(email_pattern, decoded_text)
    
    # 2. Deduplicate and Sort
    unique_emails = sorted(list(set([e.lower() for e in found_emails])))
    
    # 3. Batching Logic
    batched_output = []
    for i in range(0, len(unique_emails), batch_size):
        batch_num = (i // batch_size) + 1
        batched_output.append(f"--- BATCH {batch_num} (Count: {len(unique_emails[i:i+batch_size])}) ---")
        batched_output.extend(unique_emails[i:i+batch_size])
        batched_output.append("\n") # Add space between groups
        
    return "\n".join(batched_output), len(unique_emails)

def run_scraper():
    engine = os.getenv('ENGINE', 'google')
    manual_query = os.getenv('UI_QUERY')
    depth = int(os.getenv('DEPTH', '10')) # Higher depth for larger batches
    
    timestamp = time.strftime("%Y%m%d_%H%M")
    output_file = f'lite16_batched_{timestamp}.txt'
    
    fake = Faker()
    all_raw_data = ""

    print(f"--- Lite 1.6 High-Volume Batcher Active ---", flush=True)

    for page in range(depth):
        query = manual_query if manual_query else f'"{fake.first_name()}" CEO "@talktalk.net"'
        print(f"Page {page+1}: {query}", flush=True)
        
        url = f"https://www.{engine}.com/search?q={query.replace(' ', '+')}"
        if engine != 'duckduckgo': url += f"&start={page * 10}"

        try:
            time.sleep(random.uniform(10, 20))
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
            if res.status_code == 200:
                all_raw_data += res.text
            else:
                break
        except:
            continue

    # Apply Lite 1.6 Batching
    clean_content, total_count = lite_16_batch_extractor(all_raw_data, batch_size=500)
    
    if total_count > 0:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(clean_content)
        print(f"SUCCESS: {total_count} leads saved in batches of 500 to {output_file}", flush=True)
    else:
        print("Zero leads found. Check your search query.", flush=True)

if __name__ == "__main__":
    run_scraper()
