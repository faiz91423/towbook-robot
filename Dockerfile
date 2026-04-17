# Use the official Microsoft Playwright image which contains all OS dependencies!
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install the browser binaries 
RUN playwright install chromium

COPY . .

# Expose the API port
EXPOSE 5000

# Start the Flask web server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120", "app:app"]
