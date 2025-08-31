import pdfplumber
import re

# pdf_path = "Mid Term Schedule Summer 2025 V7.pdf"
pdf_path = "./exam schedule pdfs/Final Spring 2025/Final%20Schedule%20Spring%202025.pdf"

header_printed = False  # Track if header has been printed

# Regex to match time ranges
time_pattern = re.compile(
    r'(\d{1,2}:\d{2}\s?[APap][Mm])\s*-\s*(\d{1,2}:\d{2}\s?[APap][Mm])'
)

with pdfplumber.open(pdf_path) as pdf:
    total_pages = len(pdf.pages)
    
    for i in range(total_pages):
        page = pdf.pages[i]
        print(f"\n--- Page {i+1} ---")
        tables = page.extract_tables()

        if tables:
            table = tables[0]
            
            for j, row in enumerate(table):
                # Skip header if already printed
                if j == 0:
                    if not header_printed:
                        print(row)
                        header_printed = True
                    continue

                # Check each cell for a time range
                start_time = end_time = None
                for cell in row:
                    if cell:
                        match = time_pattern.search(cell)
                        if match:
                            start_time, end_time = match.groups()
                            break

                # Only append Start/End columns if a time range is found
                if start_time and end_time:
                    new_row = row + [start_time, end_time]
                else:
                    new_row = row

                print(new_row)
        else:
            print("No tables found on this page.")

