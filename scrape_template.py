import cloudscraper
from bs4 import BeautifulSoup

url = "https://www.bracu.ac.bd/contact"

# Create scraper to bypass Cloudflare
scraper = cloudscraper.create_scraper()
response = scraper.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# Find all the "block-content content" divs
blocks = soup.find_all("div", class_="block-content content")

if len(blocks) >= 3:
    third_block = blocks[2]   # index 2 = 3rd item
    print(third_block.get_text(separator="\n", strip=True))
else:
    print("Less than 3 blocks found")

