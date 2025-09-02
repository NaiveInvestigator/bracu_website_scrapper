import cloudscraper
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper()

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
        print(f"\n--- {link} ---")
        r2 = scraper.get(link, allow_redirects=True)

        # Check if redirected to the homepage
        if r2.url.rstrip("/") == "https://www.bracu.ac.bd":
            print("Redirected to homepage — skipping")
            continue

        soup2 = BeautifulSoup(r2.content, "html.parser")
        divs = soup2.find_all("div", class_="block-content content")
        if len(divs) >= 3:
            text = divs[2].get_text(separator="\n", strip=True)
            print(text)

            imgs = divs[2].find_all("img")
            img_urls = [img.get("src") for img in imgs if img.get("src")]
            print(img_urls)
        else:
            print("No 3rd block-content div found")

    page += 1

