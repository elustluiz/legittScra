import os, re, time, random, urllib.parse, html
from faker import Faker
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

def run_paginated_harvest():
    engine = os.getenv('ENGINE', 'google')
    manual_query = os.getenv('UI_QUERY')
    fake = Faker()
    
    timestamp = time.strftime("%Y%m%d_%H%M")
    file_path = f'harvest_{timestamp}.txt'
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        Stealth().apply_stealth_sync(page) # Apply stealth masks

        # Initial Search
        query = manual_query if manual_query else f'"{fake.first_name()}" CEO "@talktalk.net"'
        url = f"https://www.{engine}.com/search?q={urllib.parse.quote(query)}"
        page.goto(url, wait_until="networkidle", timeout=60000)

        all_content = ""
        max_pages = 10 # Limit to 10 pages for stability

        for p_idx in range(max_pages):
            print(f"Scraping Page {p_idx + 1}...")
            
            # Step 1: Mimic human scrolling to the bottom
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(random.uniform(3, 7))
            
            # Step 2: Extract current page content
            all_content += page.content()

            # Step 3: Find and click the 'Next' button
            # Google's ID for the 'Next' button is often 'pnnext'
            next_button = page.locator("#pnnext") 
            
            if next_button.is_visible():
                print("Clicking 'Next' button...")
                next_button.click()
                # Wait for navigation to complete
                page.wait_for_load_state("networkidle")
            else:
                print("No more pages found.")
                break

        # Extraction and Batching Logic (Lite 1.6 Style)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html.unescape(all_content))
        unique_emails = sorted(list(set([e.lower() for e in emails])))
        
        if unique_emails:
            with open(file_path, 'w', encoding='utf-8') as f:
                for i in range(0, len(unique_emails), 500):
                    f.write(f"--- BATCH {(i//500)+1} ---\n" + "\n".join(unique_emails[i:i+500]) + "\n\n")
            print(f"SUCCESS: {len(unique_emails)} leads saved.")
        else:
            page.screenshot(path="debug_screenshot.png") # Capture if empty

        browser.close()

if __name__ == "__main__":
    run_paginated_harvest()
