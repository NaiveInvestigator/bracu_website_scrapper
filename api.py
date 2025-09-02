from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import create_engine, text
import json
from datetime import timedelta, datetime, date
import calendar


## Helper Functions
def format_time(seconds):
    if seconds is None:
        return None

    if isinstance(seconds, timedelta):
        td = seconds
    else:
        td = timedelta(seconds=float(seconds))

    # Format into HH:MM:SS
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


# Database config
DB_USER = "root"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_NAME = "bracu_info"

# DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=False)

app = FastAPI(title="BRACU Info API")

app.mount("/client/", StaticFiles(directory="client"), name="client")

@app.get("/")
def read_root():
    return FileResponse("client/index.html")

@app.get("/announcements")
def get_announcements(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    limit: Optional[int] = Query(None, description="Max number of results to return")
):

    sql_conditions = []

    if start_date:
        sql_conditions.append("published_date >= :start_date")
    if end_date:
        sql_conditions.append("published_date <= :end_date")

    sql = "SELECT * FROM Announcements"
    if sql_conditions:
        sql += " WHERE " + " AND ".join(sql_conditions)
        sql += " ORDER BY published_date DESC"
    else:
        sql += " ORDER BY published_date DESC LIMIT 10"

    if limit:
        sql += " LIMIT :limit"


    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    if limit:
        params["limit"] = limit

    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        rows = [dict(row._mapping) for row in result]

    return rows

@app.get("/exam-schedule")
def get_exam_schedule(
    exam_type: str = Query(..., description="Exam type, e.g. Final Fall 2022, Mid Spring 2025"),  # required
    course_code: str = Query(..., description="Course code, e.g. CSE331"),  # required
    section: Optional[str] = None,
    student_id: Optional[str] = None
):
    sql_conditions = []

    if exam_type:
        sql_conditions.append("type = :type")
    if course_code:
        sql_conditions.append("course_code = :course_code")
    if section:
        sql_conditions.append("section = :section")
    if student_id:
        sql_conditions.append("student_id = :end_date")

    sql = "SELECT * FROM ExamSchedule"
    if sql_conditions:
        sql += " WHERE " + " AND ".join(sql_conditions)
        sql += " ORDER BY section ASC"

    filters = {}
    if exam_type:
        filters["type"] = exam_type
    if course_code:
        filters["course_code"] = course_code
    if section:
        filters["section"] = section
    if student_id:
        filters["student_id"] = student_id

    with engine.connect() as conn:
        result = conn.execute(text(sql), filters)
        rows = []
        for row in result:
            r = dict(row._mapping)
            if "start_time" in r and r["start_time"] is not None:
                r["start_time"] = format_time(r["start_time"])
            if "end_time" in r and r["end_time"] is not None:
                r["end_time"] = format_time(r["end_time"])
            rows.append(r)
    return rows

@app.get("/academic-dates")
def get_academic_dates(
    event_name: Optional[str] = None,
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD")
):
    sql = "SELECT * FROM AcademicDates"
    conditions = []
    params = {}

    if event_name:
        conditions.append("event_name LIKE :event_name")
        params["event_name"] = f"%{event_name}%"

    if start_date and end_date:
        conditions.append("start_date <= :end_date AND start_date >= :start_date")
        params["start_date"] = start_date
        params["end_date"] = end_date

    elif start_date:
        conditions.append("start_date = :start_date")
        params["start_date"] = start_date
    elif end_date:
        conditions.append("end_date = :end_date")
        params["end_date"] = end_date
    
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY start_date ASC"
    else:
        # If no conditions are given just give all the ecents of the current year
        current_year = datetime.now().year
        sql += f" WHERE start_date >= '{current_year}-01-01' AND start_date <= '{current_year}-12-31'" 
        sql += " ORDER BY start_date ASC"

    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        rows = [dict(row._mapping) for row in result]

    return rows

@app.get("/news")
def get_news(
    title: Optional[str] = None,
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    exact_date: Optional[str] = Query(None, description="YYYY-MM-DD")
):
    sql = "SELECT * FROM News"
    conditions = []
    params = {}

    if title:
        conditions.append("title = :title")
        params["title"] = title
    if start_date:
        conditions.append("published_date >= :start_date")
        params["start_date"] = start_date
    if end_date:
        conditions.append("published_date <= :end_date")
        params["end_date"] = end_date
    if exact_date:
        conditions.append("published_date = :exact_date")
        params["exact_date"] = exact_date

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY published_date ASC"

    if not conditions:
        # If no conditions give the news of the current month
        today = date.today()
        current_year = today.year
        current_month = today.month

        first_day = date(current_year, current_month, 1)
        last_day = date(current_year, current_month, calendar.monthrange(current_year, current_month)[1])

        first_day_str = first_day.strftime("%Y-%m-%d")
        last_day_str = last_day.strftime("%Y-%m-%d")

        sql += f" WHERE published_date >= '{first_day_str}' AND published_date <= '{last_day_str}'"
        sql += " ORDER BY published_date ASC"

    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        rows = [dict(row._mapping) for row in result]

    # Parse JSON field
    for item in rows:
        if item.get("image_url"):
            try:
                item["image_url"] = json.loads(item["image_url"])
            except Exception:
                item["image_url"] = None

    return rows

@app.get("/transport")
def get_transport(route_id: Optional[int] = None):
    sql = "SELECT * FROM Transport"
    params = {}

    if route_id:
        sql += " WHERE route_name LIKE :route_id"
        params["route_id"] = f"%Route-{route_id:02}%" # :02 make it pad with zeros to make it 2 digits.

    sql += " ORDER BY route_id ASC"

    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        rows = []
        for row in result:
            r = dict(row._mapping)
            if "first_pickup_time" in r and r["first_pickup_time"] is not None:
                r["first_pickup_time"] = format_time(r["first_pickup_time"])
            if "second_pickup_time" in r and r["second_pickup_time"] is not None:
                r["second_pickup_time"] = format_time(r["second_pickup_time"])
            if "first_dropoff_time" in r and r["first_dropoff_time"] is not None:
                r["first_dropoff_time"] = format_time(r["first_dropoff_time"])
            if "second_dropoff_time" in r and r["second_dropoff_time"] is not None:
                r["second_dropoff_time"] = format_time(r["second_dropoff_time"])
            rows.append(r)
    return rows

@app.get("/contact-info")
def get_contact_info(
    name: Optional[str] = None,
    id: Optional[int] = None
):

    if name is not None and id is not None:
        raise HTTPException(status_code=400, detail="Cannot provide both name and id")

    sql = "SELECT * FROM ContactInfo"
    params = {}

    if name:
        sql += " WHERE name LIKE :name"
        params["name"] = f"%{name}%"
    elif id:
        sql += " WHERE " + "id = :id"
        params["id"] = id

    sql += " ORDER BY id DESC"

    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        rows = [dict(row._mapping) for row in result]

    # Parse JSON fields
    for item in rows:
        if item.get("emails"):
            try:
                item["emails"] = json.loads(item["emails"])
            except Exception:
                item["emails"] = None
        if item.get("phone_no"):
            try:
                item["phone_no"] = json.loads(item["phone_no"])
            except Exception:
                item["phone_no"] = None

    return rows

@app.get("/people")
def get_people(name: Optional[str] = None):
    sql = "SELECT * FROM People"
    params = {}

    if name:
        sql += " WHERE url LIKE :name"
        params["name"] = f"%{name}%"
        sql += " ORDER BY id DESC"
    else:
        sql += " ORDER BY id DESC LIMIT :limit"
        params["limit"] = 50


    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        rows = [dict(row._mapping) for row in result]

    return rows
