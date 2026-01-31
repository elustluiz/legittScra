import os, requests, time, random, urllib.parse
from faker import Faker

def run_scraper():
    engine = os.getenv('ENGINE', 'google')
    depth = int(os.getenv('DEPTH', '3'))
    manual_query = os.getenv('UI_QUERY')
    
    fake = Faker()
    # Unique timestamp for this specific run
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    file_path = f'harvest_{timestamp}.txt'

    for page in range(depth):
        full_query = manual_query if manual_query else f'"{fake.first_name()}" CEO "@talktalk.net"'
        
        print(f"--- Harvesting Page {page+1} to {file_path} ---", flush=True)
        url = f"https://www.{engine}.com/search?q={full_query.replace(' ', '+')}"
        if engine != 'duckduckgo': url += f"&start={page * 10}"

        try:
            time.sleep(random.uniform(15, 30))
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
            
            if response.status_code == 200:
                # Decoding removes the %22 junk seen in image_e89af1.png
                clean_text = urllib.parse.unquote(response.text)
                
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n--- PAGE {page+1} HARVEST | QUERY: {full_query} ---\n")
                    f.write(clean_text)
                print(f"SUCCESS: Page {page+1} data saved.", flush=True)
            else:
                print(f"Blocked on page {page+1} (Status {response.status_code})", flush=True)
                break 
        except Exception as e:
            print(f"Error on page {page+1}: {e}", flush=True)

if __name__ == "__main__":
    run_scraper()
