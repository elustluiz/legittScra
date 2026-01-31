import requests
from bs4 import BeautifulSoup
import csv
import time

def run_scraper():
    # The URL we are targeting
    url = "https://quotes.toscrape.com/"
    
    # Send request with a "User-Agent" to look like a real browser
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        quotes = soup.find_all('div', class_='quote')
        
        with open('results.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Text', 'Author'])
            
            for q in quotes:
                text = q.find('span', class_='text').text
                author = q.find('small', class_='author').text
                writer.writerow([text, author])
        
        print("Success! Data saved to results.csv")
    else:
        print(f"Failed to fetch page. Status code: {response.status_code}")

if __name__ == "__main__":
    run_scraper()
