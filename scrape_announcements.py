import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

scraper = cloudscraper.create_scraper()
base_url = "https://www.bracu.ac.bd"

page = 0  # Drupal pages start at 0
while True:
    url = f"{base_url}/news-archive/announcements?page={page}"
    response = scraper.get(url)
    
    if response.status_code != 200:
        print(f"Failed to fetch page {page}, status code: {response.status_code}")
        break

    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.select("article.node-announcement")
    
    if not articles:
        print("No more announcements found.")
        break

    for article in articles:
        # Title and relative link
        title_tag = article.select_one("h2.page-h1 a")
        title = title_tag.get_text(strip=True) if title_tag else "No title"
        relative_link = title_tag['href'] if title_tag else None
        full_url = urljoin(base_url, relative_link) if relative_link else None

        # Visit the linked page to get the message
        message = ""
        if full_url:
            linked_resp = scraper.get(full_url)
            linked_soup = BeautifulSoup(linked_resp.text, "html.parser")
            
            # Get all divs with class "block-content content"
            content_divs = linked_soup.select("div.block-content.content")
            
            # Only process the 3rd div (index 2)
            if len(content_divs) >= 3:
                content_div = content_divs[2]
                links = []
                message = content_div.get_text(separator="\n", strip=True)
                # Find any <a> tags inside the div
                for a_tag in content_div.find_all("a", href=True):
                    link = a_tag['href']
                    if "https:" not in link:
                        link = "https:" + link
                    links.append(link)

                message += "\nEmbedded Page Links :\n"
                message += "\n".join(links)

            date_tag = linked_soup.select_one("span.date-display-single")
            published_date = date_tag.get_text(strip=True) if date_tag else None

        # Print results
        print(f"Title: {title}")
        print(f"URL: {full_url}")
        print(f"Published Date: {published_date}")
        print(f"Message:\n{message}\n")
        print("-" * 80)
        time.sleep(1)

    page += 1
    time.sleep(3)

