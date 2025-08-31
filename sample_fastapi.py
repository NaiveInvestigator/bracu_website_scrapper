from fastapi import FastAPI, Query
import mysql.connector

app = FastAPI()

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # your MySQL password
        database="bracu_info"
    )

# -----------------------
# Announcements
# -----------------------
@app.get("/announcements")
def search_announcements(q: str = Query(..., description="Search title or message")):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "SELECT * FROM Announcements WHERE title LIKE %s OR message LIKE %s"
        cursor.execute(sql, (f"%{q}%", f"%{q}%"))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        return {"results": results}
    finally:
        cursor.close()
        conn.close()

# -----------------------
# Facebook Posts
# -----------------------
@app.get("/facebook_posts")
def search_facebook_posts(q: str = Query(..., description="Search page_id or message")):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "SELECT * FROM FacebookPosts WHERE page_id LIKE %s OR message LIKE %s"
        cursor.execute(sql, (f"%{q}%", f"%{q}%"))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        return {"results": results}
    finally:
        cursor.close()
        conn.close()

# -----------------------
# Club Page
# -----------------------
@app.get("/club_page")
def search_club_page(q: str = Query(..., description="Search group_name or page_id")):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "SELECT * FROM ClubPage WHERE group_name LIKE %s OR page_id LIKE %s"
        cursor.execute(sql, (f"%{q}%", f"%{q}%"))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        return {"results": results}
    finally:
        cursor.close()
        conn.close()

# -----------------------
# Exam Schedule
# -----------------------
@app.get("/exam_schedule")
def search_exam_schedule(q: str = Query(..., description="Search course_code, section, dept, or student_id")):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT * FROM ExamSchedule 
            WHERE course_code LIKE %s 
            OR section LIKE %s 
            OR dept LIKE %s 
            OR student_id LIKE %s
        """
        cursor.execute(sql, (f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%"))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        return {"results": results}
    finally:
        cursor.close()
        conn.close()

# -----------------------
# Academic Dates
# -----------------------
@app.get("/academic_dates")
def search_academic_dates(q: str = Query(..., description="Search event_name")):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "SELECT * FROM AcademicDates WHERE event_name LIKE %s"
        cursor.execute(sql, (f"%{q}%",))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        return {"results": results}
    finally:
        cursor.close()
        conn.close()

# -----------------------
# News
# -----------------------
@app.get("/news")
def search_news(q: str = Query(..., description="Search title or message")):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "SELECT * FROM News WHERE title LIKE %s OR message LIKE %s"
        cursor.execute(sql, (f"%{q}%", f"%{q}%"))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        return {"results": results}
    finally:
        cursor.close()
        conn.close()

# -----------------------
# People
# -----------------------
@app.get("/people")
def search_people(q: str = Query(..., description="Search url or text")):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "SELECT * FROM People WHERE url LIKE %s OR text LIKE %s"
        cursor.execute(sql, (f"%{q}%", f"%{q}%"))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        return {"results": results}
    finally:
        cursor.close()
        conn.close()

