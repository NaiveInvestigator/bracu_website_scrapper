CREATE DATABASE bracu_info;
USE bracu_info;

-- ==============================
-- Announcements
-- ==============================
CREATE TABLE Announcements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL UNIQUE,
    message TEXT,
    published_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
-- Exam Schedule
-- ==============================
CREATE TABLE ExamSchedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(100) NOT NULL,
    course_code VARCHAR(50) NOT NULL,
    section VARCHAR(50),
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    room_no VARCHAR(50),
    dept VARCHAR(100),
    student_id VARCHAR(50) NOT NULL
);

-- ==============================
-- Academic Dates
-- ==============================
CREATE TABLE AcademicDates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_name VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL
);

-- ==============================
-- News
-- ==============================
CREATE TABLE News (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    image_url JSON,
    published_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
-- Transport Info
-- ==============================
create table Transport (
    route_id int auto_increment primary key,
    route_name varchar(255) not null,
    stoppage varchar(255) not null,
    first_pickup_time time,
    second_pickup_time time,
    first_dropoff_time time,
    second_dropoff_time time,
    phone_no varchar(20)
);

-- ==============================
-- General Contact Info
-- ==============================
CREATE TABLE ContactInfo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    emails JSON,
    hours VARCHAR(255),
    phone_no JSON
);


-- ==============================
-- People
-- ==============================
CREATE TABLE People (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(500) NOT NULL UNIQUE,
    image_url VARCHAR(500),
    about TEXT
);
