import cloudscraper
from bs4 import BeautifulSoup

# Target URL
url = "https://www.bracu.ac.bd/students-transport-service"

# Create a scraper session
scraper = cloudscraper.create_scraper(delay=2)

# Fetch page
response = scraper.get(url)
if response.status_code != 200:
    print(f"Failed to fetch page: {response.status_code}")
    exit()

# Parse with BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

# Get all contact info
columns = soup.select("div.columns.medium-6.small-12")
route_contact_info_list = []
for col in columns:
    # Find all <li> inside this column
    items = col.select("ul li")
    for li in items:
        strong = li.find("strong")
        phone_no = li.get_text(strip=True).replace(strong.get_text(strip=True), "").strip()
        route_contact_info_list.append(phone_no)

# Find all divs with class block-content
divs = soup.select("div.block-content.content")

if len(divs) >= 3:
    third_div = divs[2]  # 3rd div (0-based index)
    
    # Find all accordion items inside the 3rd div
    accordion_items = third_div.select("li.accordion-item")

    
    if not accordion_items:
        print("No Routes Found")
    else:
        for index, item in enumerate(accordion_items[:-2]):
            # Extract the title
            title_tag = item.select_one("a.accordion-title")
            route_name = title_tag.get_text(strip=True) if title_tag else "No title"
            
            # Extract the body content
            body_tag = item.select_one("div.accordion-content")
            route_details = body_tag.get_text(separator="\n", strip=True) if body_tag else "No content"
            
            print(f"Title: {route_name}")
            print("Body:")
            print(route_details)
            print("Route Contact Info:")
            print(route_contact_info_list[index])
            print("-" * 80)

        print("First Dropoff timings")
        first_dropoff_timings = accordion_items[-2].select_one("div.accordion-content").get_text(separator="\n", strip=True)
        print(first_dropoff_timings)

        print("-" * 80)

        print("Second Dropoff timings")
        second_dropoff_timings = accordion_items[-1].select_one("div.accordion-content").get_text(separator="\n", strip=True)
        print(second_dropoff_timings)


else:
    print("Less than 3 block-content divs found")

