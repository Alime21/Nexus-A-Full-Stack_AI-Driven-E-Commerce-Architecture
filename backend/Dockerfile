#SUMMARY: This file sets up the Python environment, installs the libraries,
#imports our code, and prepares the application for publication on port 8000.

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


