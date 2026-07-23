# Gunakan Official Playwright Python Base Image (sudah include Chromium & browser dependencies)
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# Set working directory
WORKDIR /app

# Copy repo files
COPY . .

# Install Scrapling package dengan semua dependensi fetchers ([fetchers])
RUN pip install --no-cache-dir ".[fetchers]"

# Install Playwright / Patchright browser binaries
RUN python -m patchright install chromium

# Expose Port 5000
EXPOSE 5000

# Command jalankan REST API microservice (gunakan -u agar log langsung muncul di docker logs)
CMD ["python", "-u", "server.py"]