from python:latest

workdir /app

copy requirements.txt requirements.txt
run pip3 install -r requirements.txt

copy . .

cmd ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

