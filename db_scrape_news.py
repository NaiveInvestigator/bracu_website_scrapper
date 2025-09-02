import cloudscraper
from bs4 import BeautifulSoup
import mysql.connector
import json
from datetime import datetime
import re

def clean_ordinal_date(date_str: str):
    """Remove ordinal suffixes like st, nd, rd, th from day numbers."""
    return re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)


# === CONFIG ===
base_url = "https://www.bracu.ac.bd"

db_config = {
    "host": "localhost",
    "user": "root",      # change if needed
    "password": "",      # add your MySQL password
    "database": "bracu_info"
}

# === MYSQL CONNECTION ===
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# === SCRAPER ===
scraper = cloudscraper.create_scraper()
page_num = 0
while True:
    main_url = f"{base_url}/news-archive?page={page_num}"
    print(f"Fetching: {main_url}")
    # Fetch the main page
    response = scraper.get(main_url)
    if response.status_code == 404:
        break
    if response.status_code != 200:
        print(f"Failed to fetch {main_url}, status code: {response.status_code}")
        exit()

    # Parse the main page
    soup = BeautifulSoup(response.text, "html.parser")

    # Remove parent of pagination div
    pagination_div = soup.find("div", class_="item-list item-list-pagination")
    if pagination_div:
        pagination_div.decompose()

    # Find all divs with class "block-content content"
    blocks = soup.find_all("div", class_="block-content content")

    if len(blocks) < 3:
        print("Less than 3 content blocks found.")
        exit()

    # Target block
    target_block = blocks[2]

    # Extract all a tags that start with /news
    links = [a for a in target_block.find_all("a", href=True) if a['href'].startswith("/news")]

    for link in links:
        title = link.get_text(strip=True)
        url = base_url + link['href']

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
        message = page_content_block.get_text(separator="\n", strip=True)

        # Collect all images
        images = [img['src'] for img in page_content_block.find_all("img", src=True)]
        image_json = json.dumps(images) if images else json.dumps([])

        # === Get published date ===
        date_tag = page_soup.select_one("span.date-display-single")
        pub_date_sql = None
        if date_tag:
            published_date = clean_ordinal_date(date_tag.get_text(strip=True))
            try:
                pub_date_sql = datetime.strptime(published_date, "%B %d, %Y")
            except Exception as e:
                print(f"  Could not parse date '{published_date}' for {title}: {e}")

        # Insert into DB
        try:
            cursor.execute("""
                INSERT INTO News (title, message, image_url, published_date)
                VALUES (%s, %s, %s, %s)
            """, (title, message, image_json, pub_date_sql))
            conn.commit()
            print(f"Inserted: {title} ({pub_date_sql})")
        except Exception as e:
            print(f"Error inserting {title}: {e}")
    page_num += 1
# Close DB connection
cursor.close()
conn.close()

