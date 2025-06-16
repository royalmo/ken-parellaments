FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app .

EXPOSE 4200

CMD ["gunicorn", "-b", "0.0.0.0:4200", "app:app"]
