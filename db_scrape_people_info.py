import cloudscraper
from bs4 import BeautifulSoup
import time
from db import MySQLDatabase

# Connect to DB
db = MySQLDatabase(host="localhost", user="root", password="", database="bracu_info")

scraper = cloudscraper.create_scraper()

page = 1
while True:
    sitemap_url = f"https://www.bracu.ac.bd/sitemap.xml?page={page}"
    r = scraper.get(sitemap_url)
    if r.status_code != 200:
        break

    soup = BeautifulSoup(r.content, "lxml-xml")
    urls = soup.find_all("url")
    people_links = [u for u in urls if "/people/" in u.loc.text]
    if not people_links:
        print("No more people links found.")
        break

    for u in people_links:
        link = u.loc.text
        print(f"\n--- {link} ---")

        # Stop if URL already exists in DB
        if db.exists("People", "url", link):
            print("Duplicate URL found in DB. Stopping.")
            exit()

        r2 = scraper.get(link)
        soup2 = BeautifulSoup(r2.content, "html.parser")
        divs = soup2.find_all("div", class_="block-content content")

        text = "No 3rd block-content div found"
        if len(divs) >= 3:
            text = divs[2].get_text(separator="\n", strip=True)
            if text.startswith("From Bangladesh to the World"):
                text = "Info not found"

        print(text[:200], "..." if len(text) > 200 else "")  # preview

        # Insert into DB
        db.insert("People", {
            "url": link,
            "text": text
        })

        time.sleep(1)

    page += 1
    time.sleep(2)

db.close()

