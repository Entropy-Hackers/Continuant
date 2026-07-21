FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ templates/

# Runs as a non-root user; only ever reads read-only-mounted audit dirs.
RUN useradd --create-home --uid 10001 dashboard
USER dashboard

EXPOSE 8090
CMD ["gunicorn", "--bind", "0.0.0.0:8090", "--workers", "2", "app:app"]
