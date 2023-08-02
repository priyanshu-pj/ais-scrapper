FROM python:3.11

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip

RUN pip3 install flask requests

CMD ["python3", "app.py"]
