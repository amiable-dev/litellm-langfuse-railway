FROM python:3.12-slim

RUN pip install --no-cache-dir \
    requests \
    redis \
    psycopg2-binary \
    schedule

WORKDIR /app

COPY monitor.py .

EXPOSE 8080

CMD ["python3", "monitor.py"]
