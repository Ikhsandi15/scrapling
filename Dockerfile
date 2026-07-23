# Gunakan Official Playwright Python Base Image (sudah include Chromium & browser dependencies)
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# Set working directory
WORKDIR /app

# Copy requirements & install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright / Patchright browser binaries
RUN python -m patchright install chromium

# Copy aplikasi scraper
COPY . .

# Expose Port 5000
EXPOSE 5000

# Command jalankan REST API microservice
CMD ["python", "server.py"]