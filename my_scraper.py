import os, re, time, random, urllib.parse, html
from faker import Faker
from playwright.sync_api import sync_playwright
# FIX: Updated import for latest playwright-stealth
from playwright_stealth import Stealth

def lite_16_extractor(text):
    """Lite 1.6 logic: Decode, Extract, Deduplicate"""
    clean_text = html.unescape(urllib.parse.unquote(text))
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    found = re.findall(email_pattern, clean_text)
    return sorted(list(set([e.lower() for e in found])))

def run_stealth_harvest():
    engine = os.getenv('ENGINE', 'google')
    manual_query = os.getenv('UI_QUERY')
    fake = Faker()
    
    timestamp = time.strftime("%Y%m%d_%H%M")
    file_path = f'harvest_{timestamp}.txt'
    
    # 1. Initialize Stealth Browser
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=fake.chrome())
        page = context.new_page()
        
        # FIX: Updated stealth application method
        stealth = Stealth()
        stealth.apply_stealth_sync(page)

        all_content = ""
        depth = 5 
        
        for p_idx in range(depth):
            query = manual_query if manual_query else f'"{fake.first_name()}" CEO "@talktalk.net"'
            url = f"https://www.{engine}.com/search?q={urllib.parse.quote(query)}&start={p_idx * 10}"
            
            print(f"Scraping Page {p_idx+1}: {url}")
            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                time.sleep(random.uniform(5, 10))
                all_content += page.content()
            except Exception as e:
                print(f"Error on page {p_idx+1}: {e}")
                page.screenshot(path="debug_screenshot.png")
                break

        emails = lite_16_extractor(all_content)
        
        if emails:
            with open(file_path, 'w', encoding='utf-8') as f:
                for i in range(0, len(emails), 500):
                    f.write(f"--- BATCH {(i//500)+1} ---\n" + "\n".join(emails[i:i+500]) + "\n\n")
            print(f"SUCCESS: Found {len(emails)} leads.")
        else:
            print("ZERO RESULTS: Check debug_screenshot.png")
            page.screenshot(path="debug_screenshot.png")
            
        browser.close()

if __name__ == "__main__":
    run_stealth_harvest()
