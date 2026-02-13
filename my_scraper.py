import os, requests, re, time, random, urllib.parse, html
from faker import Faker
from playwright.sync_api import sync_playwright

def capture_debug_screenshot(url):
    """Captures the search page with a longer timeout for CI stability"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000) # Final buffer for animations
            page.screenshot(path="debug_screenshot.png", full_page=True)
            print("DEBUG: Diagnostic screenshot captured.")
        except Exception as e:
            print(f"DEBUG: Failed to take screenshot: {e}")
        finally:
            browser.close()

def run_scraper():
    engine = os.getenv('ENGINE', 'google')
    manual_query = os.getenv('UI_QUERY')
    fake = Faker()
    
    query = manual_query if manual_query else f'"{fake.first_name()}" CEO "@talktalk.net"'
    target_url = f"https://www.{engine}.com/search?q={urllib.parse.quote(query)}"
    
    print(f"--- Target URL: {target_url} ---")
    
    try:
        # Standard Lite 1.6 Extraction Logic
        headers = {'User-Agent': fake.chrome()}
        res = requests.get(target_url, headers=headers, timeout=20)
        
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html.unescape(res.text))
        
        if not emails:
            print("ZERO RESULTS: Triggering diagnostic screenshot...")
            capture_debug_screenshot(target_url)
        else:
            print(f"SUCCESS: Found {len(set(emails))} leads.")
            # Save leads logic...
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        capture_debug_screenshot(target_url)

if __name__ == "__main__":
    run_scraper()
