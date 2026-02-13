import os, requests, re, time, random, urllib.parse, html
from faker import Faker
from playwright.sync_api import sync_playwright

def capture_debug_screenshot(url):
    """Captures the search page if zero results are found"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.screenshot(path="debug_screenshot.png", full_page=True)
        browser.close()
    print("DEBUG: Screenshot saved as debug_screenshot.png", flush=True)

def lite_16_extractor(text):
    clean_text = html.unescape(urllib.parse.unquote(text))
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    found = re.findall(email_pattern, clean_text)
    return sorted(list(set([e.lower() for e in found])))

def run_scraper():
    engine = os.getenv('ENGINE', 'google')
    manual_query = os.getenv('UI_QUERY')
    depth = 20
    timestamp = time.strftime("%Y%m%d_%H%M")
    file_path = f'harvest_{timestamp}.txt'
    fake = Faker()
    
    all_data = ""
    last_url = ""
    for page in range(depth):
        query = manual_query if manual_query else f'"{fake.first_name()}" CEO "@talktalk.net"'
        last_url = f"https://www.{engine}.com/search?q={urllib.parse.quote(query)}&start={page * 10}"
        
        try:
            headers = {'User-Agent': fake.chrome()}
            time.sleep(random.uniform(20, 30))
            res = requests.get(last_url, headers=headers, timeout=20)
            if res.status_code == 200:
                all_data += res.text
            else:
                break
        except: continue

    emails = lite_16_extractor(all_data)
    if not emails:
        # Trigger the screenshot if no results were harvested
        capture_debug_screenshot(last_url)
        print("ZERO RESULTS: Check the 'Artifacts' tab for the diagnostic screenshot.", flush=True)
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            for i in range(0, len(emails), 500):
                f.write(f"--- BATCH {(i//500)+1} ---\n" + "\n".join(emails[i:i+500]) + "\n\n")
        print(f"SUCCESS: {len(emails)} leads found.", flush=True)

if __name__ == "__main__":
    run_scraper()
