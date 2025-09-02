pip install bs4 cloudscraper lxml mysql-connector-python pdfplumber "fastapi[standard-no-fastapi-cloud-cli]" uvicorn sqlalchemy pydantic 

pip install pymysql # Just in case mysql-connector doesnt work

pdfminer.six gets installed along side with pdfplumber

run the main.py api file using
uvicorn main:app --reload 
or
fastapi dev test.py

Useful SQL Commands:


show tables;
DROP TABLE People;
select * from People;
select url, image_url from People;


Setup mysql docker:
https://docs.cvat.ai/docs/administration/basics/installation/

docker run --name mysql-server -e MYSQL_ALLOW_EMPTY_PASSWORD=yes -p 3306:3306 -d mysql:oraclel
inux9

docker exec -it mysql-server /bin/bash

mysql -u root



After reboot or stopping sql container, no need to run whole command
Do:

docker start mysql-server
