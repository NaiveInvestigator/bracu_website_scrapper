import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from db import MySQLDatabase
from datetime import datetime
import re

# --- Initialize DB ---
db = MySQLDatabase(database="bracu_info")
db.execute("""
CREATE TABLE IF NOT EXISTS Announcements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    message TEXT,
    published_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY (url)
)
""")

scraper = cloudscraper.create_scraper()
base_url = "https://www.bracu.ac.bd"
page = 0

def parse_date(date_str):
    date_str_clean = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
    try:
        dt = datetime.strptime(date_str_clean, "%B %d, %Y - %I:%M%p")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None

try:
    stop_scraping = False

    while not stop_scraping:
        url = f"{base_url}/news-archive/announcements?page={page}"
        response = scraper.get(url)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.select("article.node-announcement")
        if not articles:
            break

        for article in articles:
            title_tag = article.select_one("h2.page-h1 a")
            title = title_tag.get_text(strip=True) if title_tag else "No title"
            relative_link = title_tag['href'] if title_tag else None
            full_url = urljoin(base_url, relative_link) if relative_link else None

            message = ""
            if full_url:
                linked_resp = scraper.get(full_url)
                linked_soup = BeautifulSoup(linked_resp.text, "html.parser")
                content_divs = linked_soup.select("div.block-content.content")
                if len(content_divs) >= 3:
                    content_div = content_divs[2]
                    links = []
                    message = content_div.get_text(separator="\n", strip=True)
                    for a_tag in content_div.find_all("a", href=True):
                        links.append("https:" + a_tag['href'])
                    if links:
                        message += "\nEmbedded Page Links:\n" + "\n".join(links)

            # Parse published date
            date_tag = article.select_one("span.date-display-single")
            published_date = parse_date(date_tag.get_text(strip=True)) if date_tag else None

            # Stop if URL already exists
            if full_url and db.exists("Announcements", "url", full_url):
                print(f"Announcement URL already exists: {full_url}. Stopping scraper.")
                stop_scraping = True
                break

            # Insert into DB
            db.insert("Announcements", {
                "title": title,
                "url": full_url,
                "message": message,
                "published_date": published_date
            })
            print(f"Saved: {title}")
            time.sleep(1)

        page += 1
        time.sleep(3)
finally:
    db.close()

