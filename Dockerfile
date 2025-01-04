FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY . .

# Create upload directories
RUN mkdir -p static/uploads/covers static/uploads/hero

# Set permissions
RUN chmod -R 755 static/uploads

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
