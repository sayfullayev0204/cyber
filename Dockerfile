# Python image
FROM python:3.10-slim

# Loyihaga kerakli paketlarni o'rnatish
WORKDIR /app
COPY requirements.txt /app/

RUN apt-get update

# 2. tzdata va boshqa kerakli paketlar o'rnatilsin
RUN apt-get install -y tzdata

RUN pip install --no-cache-dir -r requirements.txt 


ENV TZ=Asia/Tashkent

# Loyihani joylash
COPY . /app/

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
