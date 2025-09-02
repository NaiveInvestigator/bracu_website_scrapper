import cloudscraper
from bs4 import BeautifulSoup
import mysql.connector
import re
import json

def decode_cf_email(e):
    """Decode Cloudflare-protected emails"""
    r = int(e[:2], 16)
    return "".join(
        chr(int(e[i:i+2], 16) ^ r)
        for i in range(2, len(e), 2)
    )

# === CONFIG ===
url = "https://www.bracu.ac.bd/contact"
db_config = {
    "host": "localhost",
    "user": "root",       # change if needed
    "password": "",       # put your MySQL password
    "database": "bracu_info"
}

# === DB SETUP ===
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

def insert_contact(name=None, emails=None, hours=None, phones=None):
    cursor.execute("""
        INSERT INTO ContactInfo (name, emails, hours, phone_no)
        VALUES (%s, %s, %s, %s)
    """, (
        name,
        json.dumps(emails) if emails else None,
        hours,
        json.dumps(phones) if phones else None
    ))
    conn.commit()

# === SCRAPER ===
scraper = cloudscraper.create_scraper()
response = scraper.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

blocks = soup.find_all("div", class_="block-content")

if len(blocks) >= 3:
    third_div = blocks[2]

    # Decode Cloudflare emails
    for span in third_div.find_all("span", class_="__cf_email__"):
        cf_encoded = span.get("data-cfemail")
        if cf_encoded:
            span.string = decode_cf_email(cf_encoded)

    tables = third_div.find_all("table")
    total_tables = len(tables)

    # === Matches we care about ===
    matches = ["phone", "ivr", "email", "hours"]

    for idx, table in enumerate(tables, start=1):
        text = table.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        if idx <= total_tables - 2:  # First 4 structured tables
            if not lines:
                continue

            name = lines[0]
            info = {m: [] for m in matches}
            current_key = None

            for line in lines[1:]:
                # Check if line contains any keyword
                found_key = None
                for m in matches:
                    if m.lower() in line.lower():
                        found_key = m
                        break

                if found_key:
                    current_key = found_key
                elif current_key:
                    info[current_key].append(line)

            # Extract values
            emails = []
            if info["email"]:
                for line in info["email"]:
                    emails.extend(re.findall(r'[\w\.-]+@[\w\.-]+', line))

            phones = []
            if info["phone"] or info["ivr"]:
                for line in info["phone"] + info["ivr"]:
                    phones.extend(re.findall(r'(\+?\d[\d\s\-,()]+)', line))

            for idx, phone in enumerate(phones):
                if "880" not in phone:
                    phones.pop(idx)
                else:
                    phones[idx] = "+" + re.sub(r'\D', '', phone[1:])

            hours = " ".join(info["hours"]) if info["hours"] else None

            insert_contact(
                name,
                sorted(set(emails)) if emails else None,
                hours,
                sorted(set(phones)) if phones else None
            )

        else:  # Last 2 tables (Name | Email format)
            for row in table.find_all("tr"):
                cells = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]
                if len(cells) >= 2:
                    name = cells[0]
                    emails = re.findall(r'[\w\.-]+@[\w\.-]+', cells[1])
                    insert_contact(name, emails, None, None)

else:
    print("Less than 3 blocks found")

cursor.close()
conn.close()

