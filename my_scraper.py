import os, requests, time, random, urllib.parse
from faker import Faker

def run_scraper():
    engine = os.getenv('ENGINE', 'google')
    depth = int(os.getenv('DEPTH', '10'))
    manual_query = os.getenv('UI_QUERY')
    
    fake = Faker()
    timestamp = time.strftime("%Y%m%d_%H%M")
    file_path = f'harvest_{timestamp}.txt'
    
    print(f"--- Starting {depth}-Page Harvest: {file_path} ---", flush=True)

    for page in range(depth):
        # LOGIC: Use manual query if provided, otherwise auto-generate
        if manual_query:
            full_query = manual_query
        else:
            full_query = f'"{fake.first_name()}" CEO "@talktalk.net"'
        
        print(f"--- Page {page+1} | Query: {full_query} ---", flush=True)
        
        url = f"https://www.{engine}.com/search?q={full_query.replace(' ', '+')}"
        if engine != 'duckduckgo':
            url += f"&start={page * 10}"

        try:
            time.sleep(random.uniform(15, 25))
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
            
            if response.status_code == 200:
                # Decoding removes %22 junk seen in image_e89af1.png
                clean_content = urllib.parse.unquote(response.text)
                
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n--- PAGE {page+1} | {full_query} ---\n")
                    f.write(clean_content)
                print(f"SUCCESS: Page {page+1} saved.", flush=True)
            else:
                print(f"Blocked (Status {response.status_code})", flush=True)
                break 
        except Exception as e:
            print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    run_scraper()
