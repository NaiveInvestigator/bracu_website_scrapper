import cloudscraper
from bs4 import BeautifulSoup

# Initialize cloudscraper
scraper = cloudscraper.create_scraper()

# Base URL
base_url = "https://www.bracu.ac.bd"
main_url = f"{base_url}/news-archive"

# Fetch the main page
response = scraper.get(main_url)
if response.status_code != 200:
    print(f"Failed to fetch {main_url}, status code: {response.status_code}")
    exit()

# Parse the main page
soup = BeautifulSoup(response.text, "html.parser")

# Find all divs with class "block-content content"
blocks = soup.find_all("div", class_="block-content content")

# Make sure there are at least 3 divs
if len(blocks) < 3:
    print("Less than 3 content blocks found.")
    exit()

# Get the 3rd block
target_block = blocks[2]

# Extract all a tags that start with /news
links = [a for a in target_block.find_all("a", href=True) if a['href'].startswith("/news")]

for link in links:
    title = link.get_text(strip=True)
    url = base_url + link['href']  # Make full URL
    
    print(f"Title: {title}")
    print(f"URL: {url}")
    
    # Fetch the page of the link
    page_resp = scraper.get(url)
    if page_resp.status_code != 200:
        print(f"  Failed to fetch {url}")
        continue
    
    # Parse the page
    page_soup = BeautifulSoup(page_resp.text, "html.parser")
    page_blocks = page_soup.find_all("div", class_="block-content content")
    
    if len(page_blocks) < 3:
        print("  Less than 3 content blocks on the page.")
        continue
    
    page_content_block = page_blocks[2]
    
    # Get text
    page_content = page_content_block.get_text(separator="\n", strip=True)
    print(f"Content:\n{page_content}\n")
    
    # Get all image URLs
    images = page_content_block.find_all("img", src=True)
    if images:
        print("Images:")
        for img in images:
            print(f"  {img['src']}")
    
    print("-"*50 + "\n")

