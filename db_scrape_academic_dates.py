import time
import cloudscraper
from bs4 import BeautifulSoup
import mysql.connector
from datetime import datetime

# MySQL configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",  # your MySQL password
    "database": "bracu_info"
}

# RSS configuration
base_url = "https://www.bracu.ac.bd/academic/{semester}/{year}/rss.xml"
semesters = ["spring", "summer", "fall"]
end_year = 2014
max_retries = 10
retry_delay = 5

# Determine current year dynamically
current_year = datetime.now().year

# Initialize scraper
scraper = cloudscraper.create_scraper()

# Connect to MySQL
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

def parse_date(date_str):
    """Parse date using the exact format from the RSS feed."""
    try:
        return datetime.strptime(date_str, "%d/%m/%Y - %H:%M").date()
    except (ValueError, TypeError):
        return None

for year in range(current_year, end_year - 1, -1):  # current year down to 2010
    for semester in semesters:
        url = base_url.format(semester=semester, year=year)
        print(f"Fetching RSS for {semester.capitalize()} {year}: {url}")

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
                    event_name = event.title.text.strip() if event.title else "N/A"
                    start_date_str = event.find("start-date").text.strip() if event.find("start-date") else None
                    end_date_str = event.find("end-date").text.strip() if event.find("end-date") else None

                    start_date = parse_date(start_date_str)
                    end_date = parse_date(end_date_str)

                    if start_date and end_date:
                        cursor.execute(
                            "INSERT INTO AcademicDates (event_name, start_date, end_date) VALUES (%s, %s, %s)",
                            (event_name, start_date, end_date)
                        )
                        conn.commit()

                break  # exit retry loop if successful

            except Exception as e:
                print(f"Attempt {attempt}: Error - {e}, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
        else:
            print(f"Failed to fetch {semester} {year} RSS after {max_retries} attempts.")

cursor.close()
conn.close()
print("Done inserting academic dates into database.")

