import cloudscraper
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import Error

def decode_cf_email(e):
    """Decode Cloudflare-protected emails"""
    r = int(e[:2], 16)
    return "".join(
        chr(int(e[i:i+2], 16) ^ r)
        for i in range(2, len(e), 2)
    )


# === CONFIG ===
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "bracu_info"

scraper = cloudscraper.create_scraper()

# Connect to MySQL
try:
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()
except Error as e:
    print(f"Error connecting to MySQL: {e}")
    exit()

page = 1
while True:
    sitemap_url = f"https://www.bracu.ac.bd/sitemap.xml?page={page}"
    r = scraper.get(sitemap_url)
    if r.status_code != 200:
        break

    # Parse sitemap
    soup = BeautifulSoup(r.content, "lxml-xml")
    urls = soup.find_all("url")
    people_links = [u for u in urls if "/people/" in u.loc.text]
    if not people_links:
        break

    for u in people_links:
        link = u.loc.text
        r2 = scraper.get(link, allow_redirects=True)

        # Skip if redirected to homepage
        if r2.url.rstrip("/") == "https://www.bracu.ac.bd":
            print(f"Skipped: {link}")
            continue

        soup2 = BeautifulSoup(r2.content, "html.parser")
        divs = soup2.find_all("div", class_="block-content content")
        if len(divs) >= 3:
            # Decode Cloudflare emails
            for span in divs[2].find_all("span", class_="__cf_email__"):
                cf_encoded = span.get("data-cfemail")
                if cf_encoded:
                    span.string = decode_cf_email(cf_encoded)


            about_text = divs[2].get_text(separator="\n", strip=True)
            imgs = divs[2].find_all("img")
            image_url = imgs[0].get("src") if imgs and imgs[0].get("src") else None

            # Insert into database
            try:
                cursor.execute("""
                    INSERT INTO People (url, image_url, about)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        image_url = VALUES(image_url),
                        about = VALUES(about)
                """, (link, image_url, about_text))
                conn.commit()
                print(f"Inserted: {link}")

            except Error as e:
                print(f"Error inserting {link}: {e}")

    page += 1

# Close connection
cursor.close()
conn.close()

