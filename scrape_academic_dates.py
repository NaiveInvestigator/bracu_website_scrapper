import time
import cloudscraper
from bs4 import BeautifulSoup

# Configuration
base_url = "https://www.bracu.ac.bd/academic/{semester}/{year}/rss.xml"
semesters = ["spring", "summer", "fall"]
year = 2025
max_retries = 10  # maximum attempts per URL
retry_delay = 5   # seconds to wait before retrying

scraper = cloudscraper.create_scraper()

for semester in semesters:
    url = base_url.format(semester=semester, year=year)
    print(f"\nFetching RSS for {semester.capitalize()} {year}: {url}")

    for attempt in range(1, max_retries + 1):
        try:
            response = scraper.get(url)
            if response.status_code == 403:
                print(f"Attempt {attempt}: 403 Forbidden, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                continue

            response.raise_for_status()
            soup = BeautifulSoup(response.text, "xml")

            for event in soup.find_all("event"):
                title = event.title.text if event.title else "N/A"
                link = event.link.text if event.link else "N/A"
                start_date = event.find("start-date").text if event.find("start-date") else "N/A"
                end_date = event.find("end-date").text if event.find("end-date") else "N/A"
                date_range = event.date.text if event.date else "N/A"

                print(f"\nTitle: {title}")
                print(f"Link: {link}")
                print(f"Start: {start_date}")
                print(f"End: {end_date}")
                print(f"Date: {date_range}")
            print("-"*80)

            break  # success, exit retry loop

        except Exception as e:
            print(f"Attempt {attempt}: Error - {e}, retrying in {retry_delay}s...")
            time.sleep(retry_delay)
    else:
        print(f"Failed to fetch {semester} RSS after {max_retries} attempts.")

