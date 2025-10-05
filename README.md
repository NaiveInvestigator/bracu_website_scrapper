# FastAPI + MySQL Setup

This project uses **FastAPI**, **MySQL**, and supporting Python libraries for scraping, data processing, and API development.

---

## 📦 Installation

Install the required Python packages:

```bash
pip install bs4 cloudscraper lxml mysql-connector-python pdfplumber "fastapi[standard-no-fastapi-cloud-cli]" uvicorn sqlalchemy pydantic
```

Optional (in case `mysql-connector` doesn’t work):

```bash
pip install pymysql
```

> **Note**: Installing `pdfplumber` will also install `pdfminer.six` automatically. No need to install them seperately.

---

## 🚀 Running the API

Run the main API (`main.py`) using **FastAPI**:

```bash
fastapi dev api.py
```

---

## 🗄️ Useful SQL Commands

```sql
SHOW TABLES;
DROP TABLE People;
SELECT * FROM People;
SELECT url, image_url FROM People;
```

---

## 🐳 MySQL Docker Setup

Follow [CVAT’s Docker setup guide](https://docs.cvat.ai/docs/administration/basics/installation/) if you are on ubuntu 22.
Or check the [Docker official site](https://docs.docker.com/engine/install)
Or use [Dockers Convenience Install Script](https://get.docker.com/)

### Start a MySQL container:

```bash
docker run --name mysql-server -e MYSQL_ALLOW_EMPTY_PASSWORD=yes -p 3306:3306 -d mysql:oraclelinux9
```

### Enter the container:

```bash
docker exec -it mysql-server /bin/bash
```

### Access MySQL:

```bash
mysql -u root
```

---

## 🔄 Restarting MySQL After Reboot

If the container is stopped or the system reboots, you don’t need to run the full command again.
Just restart the container:

```bash
docker start mysql-server
```

---
