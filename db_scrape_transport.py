import cloudscraper
from bs4 import BeautifulSoup
import mysql.connector
from datetime import datetime

# === CONFIG ===
url = "https://www.bracu.ac.bd/students-transport-service"
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",  # your MySQL password
    "database": "bracu_info"
}

# === SCRAPE PAGE ===
scraper = cloudscraper.create_scraper(delay=2)
response = scraper.get(url)
if response.status_code != 200:
    print(f"Failed to fetch page: {response.status_code}")
    exit()

soup = BeautifulSoup(response.text, "html.parser")

# === GET ROUTE CONTACT INFO ===
columns = soup.select("div.columns.medium-6.small-12")
route_contact_info_list = []
for col in columns:
    items = col.select("ul li")
    for li in items:
        strong = li.find("strong")
        phone_no = li.get_text(strip=True).replace(strong.get_text(strip=True), "").strip()
        route_contact_info_list.append(phone_no)

# === GET DROP OFF TIMINGS ===
divs = soup.select("div.block-content.content")
if len(divs) < 3:
    print("Less than 3 block-content divs found")
    exit()

third_div = divs[2]
accordion_items = third_div.select("li.accordion-item")

# Last two accordion items are dropoff timings
first_dropoff_timings_text = accordion_items[-2].select_one("div.accordion-content").get_text(separator="\n", strip=True)
second_dropoff_timings_text = accordion_items[-1].select_one("div.accordion-content").get_text(separator="\n", strip=True)

# Parse dropoff timings into dict: route_no -> time
def parse_dropoff_lines(text):
    timings = {}
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    i = 0
    while i < len(lines) - 1:  # at least 2 lines needed
        route_info = lines[i]
        # If ':' not in route_info, join with next line(s)
        while ":" not in route_info and i+1 < len(lines)-1:
            i += 1
            route_info += " " + lines[i]
        # Next line is time
        time_str = lines[i+1]
        try:
            time_obj = datetime.strptime(time_str, "%I:%M %p").time()
            # Extract destination between "to" and ":"
            if "to" in route_info and ":" in route_info:
                start = route_info.index("to") + 3
                end = route_info.index(":")
                destination = route_info[start:end].strip()
                timings[destination] = time_obj
        except:
            pass
        i += 2  # move to next pair
    return timings

first_dropoff_timings = parse_dropoff_lines(first_dropoff_timings_text)
print(first_dropoff_timings)
second_dropoff_timings = parse_dropoff_lines(second_dropoff_timings_text)
print(second_dropoff_timings)
# === CONNECT TO DB ===
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# === INSERT ROUTE DATA ===
for index, item in enumerate(accordion_items[:-2]):
    title_tag = item.select_one("a.accordion-title")
    route_name = title_tag.get_text(strip=True) if title_tag else "No title"
    
    # Extract route number from route_name
    route_no = route_name.split("Route-")[-1].split(":")[0].strip()

    body_tag = item.select_one("div.accordion-content")
    if not body_tag:
        continue

    # Remove all <tr> that contain <strong> tags
    # SO this remove the headings
    for tr in body_tag.select("tr"):
        if tr.find("strong"):
            tr.decompose()  # remove from the DOM


    # Filter body lines
    # body_lines = [line for line in body_tag.get_text(separator="\n", strip=True).splitlines() if not any(sub in line for sub in ignore_substrings)]
    # body_lines = [line for line in body_tag.get_text(separator="\n", strip=True).splitlines()]
    # body_lines = body_tag.get_text(separator="\n", strip=True).splitlines()[7:]
    body_lines = body_tag.get_text(separator="\n", strip=True).splitlines()

    # Now process stoppages in chunks of 3 (stoppage, first pickup, second pickup), and will add I + 1 only if there is a valid time 
    # to hande cases where might be only 1 pickup time
    i = 0
    while i < len(body_lines):
        stoppage = body_lines[i]
        i += 1
        try:
            first_pickup = datetime.strptime(body_lines[i], "%I:%M %p").time()
            i += 1
        except:
            first_pickup = None
        try:
            second_pickup = datetime.strptime(body_lines[i], "%I:%M %p").time()
            i+= 1
        except:
            second_pickup = None

        # Find destination substring in route name
        first_dropoff = None
        second_dropoff = None
        for dest, time in first_dropoff_timings.items():
            if dest in route_name:  # substring match
                first_dropoff = time
                break

        for dest, time in second_dropoff_timings.items():
            if dest in route_name:
                second_dropoff = time
                break



        phone_no = route_contact_info_list[index] if index < len(route_contact_info_list) else None

        # Insert into DB
        cursor.execute("""
            INSERT INTO Transport
            (route_name, stoppage, first_pickup_time, second_pickup_time, first_dropoff_time, second_dropoff_time, phone_no)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (route_name, stoppage, first_pickup, second_pickup, first_dropoff, second_dropoff, phone_no))
        conn.commit()



cursor.close()
conn.close()
print("Data inserted successfully.")

