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
-- Facebook Posts
-- ==============================
CREATE TABLE FacebookPosts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    page_id VARCHAR(100) NOT NULL,
    message TEXT,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    permalink VARCHAR(500),
    fetched_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
-- Club Page
-- ==============================
CREATE TABLE ClubPage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_name VARCHAR(255) NOT NULL,
    page_id VARCHAR(100) NOT NULL
);

-- ==============================
-- Exam Schedule
-- ==============================
CREATE TABLE ExamSchedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(10) NOT NULL,
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
    published_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
-- Transport (Main Voucher Info)
-- ==============================
CREATE TABLE Transport (
    route_id INT AUTO_INCREMENT PRIMARY KEY,
    route_name VARCHAR(255) NOT NULL,
    stoppages TEXT,
    first_pickup_time TIME,
    second_pickup_time TIME,
    dropoff_time TIME
);

-- ==============================
-- Transport Fare
-- ==============================
CREATE TABLE TransportFare (
    id INT AUTO_INCREMENT PRIMARY KEY,
    route_id INT NOT NULL,
    fare DECIMAL(10,2) NOT NULL,
    proof_file VARCHAR(500),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (route_id) REFERENCES Transport(route_id) ON DELETE CASCADE
);

-- ==============================
-- Transport Contact Info
-- ==============================
CREATE TABLE TransportContactInfo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    route_id INT NOT NULL,
    phone_no VARCHAR(20),
    FOREIGN KEY (route_id) REFERENCES Transport(route_id) ON DELETE CASCADE
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
CREATE TABLE IF NOT EXISTS People (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(500) NOT NULL UNIQUE,
    text TEXT
);
