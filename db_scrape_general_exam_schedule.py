import pdfplumber
import mysql.connector
from datetime import datetime
import os

def get_col_index(headers, keyword):
    for idx, h in enumerate(headers):
        if keyword.lower() in str(h).lower():
            return idx
    return None

def parse_date(date_str):
    if not date_str or date_str == "N/A":
        return None
    
    # Possible date formats in PDF
    formats = ["%Y-%m-%d", "%d-%b-%y", "%d-%b-%Y", "%d %B %Y", "%m/%d/%Y"]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    
    return None


# MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # replace with your password
    database="bracu_info"
)
cursor = conn.cursor()

# Base folder containing exam schedule PDFs
base_folder = "./exam schedule pdfs"

# Loop through subfolders
for root, dirs, files in os.walk(base_folder):
    for file in files:
        if file.lower().endswith(".pdf") and ("mid" in file.lower() or "final" in file.lower() or "exam" in file.lower() or "schedule" in file.lower()):
            pdf_path = os.path.join(root, file)

            # Use folder name as exam type (like "Final Fall 2022")
            exam_type = os.path.basename(root) or "N/A"
            print(f"\nProcessing: {pdf_path}")
            print("Exam type:", exam_type)

            # Default student ID
            student_id = "N/A"

            try:
                with pdfplumber.open(pdf_path) as pdf:
                    total_pages = len(pdf.pages)
                    for i in range(total_pages):
                        page = pdf.pages[i]
                        tables = page.extract_tables()

                        if not tables:
                            continue

                        table = tables[0]

                        # Find header row index
                        # header_index = None
                        header_index = -1
                        for idx, row in enumerate(table):
                            if row and any("course" in str(c).lower() for c in row):
                                header_index = idx
                                break

                        # if header_index is None:
                        #     continue

                        headers = table[header_index]
                        data_rows = table[header_index + 1:]

                        for row in data_rows:
                            if not row or all(cell is None for cell in row):
                                continue

                            # Map columns
                            course_code = row[get_col_index(headers, "course")] if get_col_index(headers, "course") is not None else "N/A"
                            section = row[get_col_index(headers, "section")] if get_col_index(headers, "section") is not None else "N/A"
                            date_str = row[get_col_index(headers, "date")] if get_col_index(headers, "date") is not None else "N/A"
                            start_time_str = row[get_col_index(headers, "start time")] if get_col_index(headers, "start time") is not None else "N/A"
                            end_time_str = row[get_col_index(headers, "end time")] if get_col_index(headers, "end time") is not None else "N/A"
                            room_no = row[get_col_index(headers, "room")] if get_col_index(headers, "room") is not None else "N/A"
                            dept = row[get_col_index(headers, "dept")] if get_col_index(headers, "dept") is not None else "N/A"

                            # Convert date and time
                            date = parse_date(date_str)

                            try:
                                start_time = datetime.strptime(start_time_str.strip(), "%I:%M %p").time()
                            except:
                                start_time = None

                            try:
                                end_time = datetime.strptime(end_time_str.strip(), "%I:%M %p").time()
                            except:
                                end_time = None

                            # Insert into MySQL
                            sql = """
                                INSERT INTO ExamSchedule 
                                (type, course_code, section, date, start_time, end_time, room_no, dept, student_id)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """
                            cursor.execute(sql, (
                                exam_type,
                                course_code or "N/A",
                                section or "N/A",
                                date,
                                start_time,
                                end_time,
                                room_no or "N/A",
                                dept or "N/A",
                                student_id
                            ))
                            conn.commit()
            except Exception as e:
                print(f"Error processing {pdf_path}: {e}")

cursor.close()
conn.close()
print("\nAll PDF data inserted into MySQL successfully!")

