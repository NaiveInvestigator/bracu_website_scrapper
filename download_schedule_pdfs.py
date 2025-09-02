import mysql.connector
import cloudscraper
import os
import time
import re

# Base folder to save PDFs
base_folder = "exam schedule pdfs"
os.makedirs(base_folder, exist_ok=True)

# Initialize cloudscraper
scraper = cloudscraper.create_scraper()

# Maximum number of retries
MAX_RETRIES = 5
RETRY_DELAY = 3

def fetch_and_download_exam_schedule_pdfs():
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="bracu_info"
        )
        cursor = conn.cursor(dictionary=True)

        # Run query
        query = "SELECT title, message FROM Announcements WHERE title LIKE %s"
        cursor.execute(query, ["%exam schedule%"])

        # Fetch results
        results = cursor.fetchall()
        for row in results:
            title = row["title"]
            message = row["message"]

            # Determine folder name from title
            folder_name = get_folder_name_from_title(title)
            full_folder_path = os.path.join(base_folder, folder_name)
            os.makedirs(full_folder_path, exist_ok=True)

            if "Embedded Page Links :" in message:
                content_after = message.split("Embedded Page Links :", 1)[1].strip()
                urls = [url.strip() for url in content_after.splitlines() if url.strip()]
                for url in urls:
                    download_pdf_with_retry(url, full_folder_path)
            else:
                print(f"No Embedded Page Links found in message: {title}")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_folder_name_from_title(title):
    # Detect exam type
    title_lower = title.lower()
    if "final" in title_lower:
        exam_type = "Final"
    elif "mid" in title_lower:
        exam_type = "Mid"
    else:
        exam_type = "Other"

    # Detect semester and year
    match = re.search(r"(Spring|Fall|Summer)\s+\d{4}", title, re.IGNORECASE)
    semester = match.group(0) if match else "Unknown Semester"

    return f"{exam_type} {semester}".strip()

def download_pdf_with_retry(url, folder_path):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = scraper.get(url)
            if response.status_code == 404:
                print(f"404 Not Found: {url}, skipping download.")
                break  # do not retry on 404
            response.raise_for_status()  # raise exception for other bad status
            filename = os.path.join(folder_path, url.split("/")[-1])
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Downloaded: {filename}")
            break  # success, exit loop
        except Exception as e:
            # Only retry if it's not a 404
            if "404" in str(e):
                print(f"404 Error encountered, skipping: {url}")
                break
            print(f"Attempt {attempt} failed for {url}: {e}")
            if attempt < MAX_RETRIES:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"Failed to download {url} after {MAX_RETRIES} attempts.")

if __name__ == "__main__":
    fetch_and_download_exam_schedule_pdfs()

