import cloudscraper
from bs4 import BeautifulSoup

def decode_cf_email(e):
    """Decode Cloudflare-protected emails"""
    r = int(e[:2], 16)
    return "".join(
        chr(int(e[i:i+2], 16) ^ r)
        for i in range(2, len(e), 2)
    )

url = "https://www.bracu.ac.bd/contact"

# Create scraper
scraper = cloudscraper.create_scraper()
response = scraper.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# Find all "block-content" divs
blocks = soup.find_all("div", class_="block-content")

if len(blocks) >= 3:
    third_div = blocks[2]

    # Decode Cloudflare emails inside this block
    for span in third_div.find_all("span", class_="__cf_email__"):
        cf_encoded = span.get("data-cfemail")
        if cf_encoded:
            span.string = decode_cf_email(cf_encoded)

    address = third_div.find("div", class_="text-18-28 theme-color-primary")
    if address:
        print("\n==== Address & General Info ====\n")
        print(address.get_text(separator="\n", strip=True))

    # Grab all tables under this block
    tables = third_div.find_all("table")
    total_tables = len(tables)

    for idx, table in enumerate(tables, start=1):
        print(f"\n==== Table {idx} ====\n")
        
        # For the last 2 tables, print row by row with cells separated by " | "
        if idx > total_tables - 2:
            for row in table.find_all("tr"):
                cells = []
                for cell in row.find_all(["td", "th"]):
                    # Join all child strings in the cell with spaces
                    text_parts = []
                    for child in cell.descendants:
                        if isinstance(child, str):
                            text_parts.append(child.strip())
                    cell_text = " ".join([t for t in text_parts if t])
                    cells.append(cell_text)
                if cells:
                    print(" | ".join(cells))
        else:
            # For other tables, print all text with \n
            print(table.get_text(separator="\n", strip=True))

else:
    print("Less than 3 blocks found")

