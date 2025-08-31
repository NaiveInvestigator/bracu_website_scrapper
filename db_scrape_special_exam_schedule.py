import pdfplumber
import mysql.connector
import os
import re
from datetime import datetime

# === CONFIG ===
base_folder = "./exam schedule pdfs"
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",   # put your MySQL password
    "database": "bracu_info"
}

# === HELPERS ===
def parse_date(date_str):
    """Try multiple date formats and return MySQL DATE"""
    if not date_str or date_str.strip() == "":
        return None
    date_str = date_str.strip()

    formats = ["%d-%b-%y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d %B %Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None

def parse_time_range(time_str):
    """Parse exam time into (start, end) using multiple regex formats."""
    if not time_str or time_str.strip() == "":
        return (None, None)

    time_str = time_str.replace(" ", "").upper()

    # List of regex patterns for different formats
    patterns = [
        r"(\d{1,2}:\d{2}[AP]M)-(\d{1,2}:\d{2}[AP]M)",   # with dash
        r"(\d{1,2}:\d{2}[AP]M)(\d{1,2}:\d{2}[AP]M)",    # no dash
        # r"(\d{1,2}[AP]M)-(\d{1,2}[AP]M)",               # without minutes, with dash (e.g., 9AM-11AM)
        # r"(\d{1,2}[AP]M)(\d{1,2}[AP]M)"                 # without minutes, no dash (e.g., 9AM11AM)
    ]

    for pattern in patterns:
        match = re.match(pattern, time_str)
        if match:
            start_raw, end_raw = match.groups()

            # Try parsing both HH:MM and HH formats
            for fmt in ["%I:%M%p", "%I%p"]:
                try:
                    start = datetime.strptime(start_raw, fmt).time()
                    end = datetime.strptime(end_raw, fmt).time()
                    return (start, end)
                except ValueError:
                    continue

    return (None, None)

def safe_get(key):
    key_lower = key.lower()
    # Find the first column whose header contains the key substring
    idx = next((i for k, i in header_map.items() if key_lower in k.lower()), None)
    return row[idx].strip() if idx is not None and row[idx] else "N/A"


conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()
header_map = {}

for root, dirs, files in os.walk(base_folder):
    for filename in files:
        if not filename.lower().endswith(".pdf"):
            continue
        # skip if filename contains mid, final, exam, or schedule
        if any(sub in filename.lower() for sub in ["mid", "final", "exam", "schedule"]):
            continue

        pdf_path = os.path.join(root, filename)
        course_code = filename[:6]
        exam_type = os.path.basename(root) or "N/A"

        print(f"Processing {pdf_path}...")

        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                for i in range(total_pages):
                    tables = pdf.pages[i].extract_tables()
                    if not tables:
                        continue

                    table = tables[0]
                    header_idx = -1

                    # --- Step 1: find header in first 5 rows ---
                    for idx in range(min(5, len(table))):
                        row = table[idx]
                        if not row:
                            continue
                        if any("schedule" in str(c).lower() for c in row):
                            continue
                        if any("sl" in str(c).lower() for c in row):
                            header_idx = idx
                            header_map = {}
                            # build header_map
                            for col_idx, col in enumerate(row):
                                if col:
                                    header_map[col.lower().strip()] = col_idx
                            break

                    # --- Step 2: start row automatically becomes header_idx + 1 ---
                    start_row = header_idx + 1

                    # print("start_row", start_row)
                    # --- Step 3: process data rows ---
                    for row in table[start_row:]:
                        if not row:
                            continue

                        student_id = safe_get("id")
                        section    = safe_get("section")
                        date_str   = safe_get("date")
                        time_str   = safe_get("time")
                        room       = safe_get("room")
                        # print(student_id, section, date_str, time_str,room)

                        exam_date = parse_date(date_str) or datetime(1900, 1, 1).date()
                        start_time, end_time = parse_time_range(time_str)

                        if not start_time: start_time = datetime(1900,1,1,0,0).time()
                        if not end_time: end_time = datetime(1900,1,1,0,0).time()

                        cursor.execute("""
                            INSERT INTO ExamSchedule
                            (type, course_code, section, date, start_time, end_time, room_no, dept, student_id)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """, (
                            exam_type,
                            course_code,
                            section,
                            exam_date,
                            start_time,
                            end_time,
                            room,
                            "N/A",
                            student_id
                        ))
                print(f"✅ Finished {pdf_path}")
                print("-"*50)
        except Exception as e:
                    print(f"❌ Skipping {pdf_path} due to error: {e}")
                    print("-"*50)

conn.commit()
cursor.close()
conn.close()
print("✅ All PDFs processed!")
