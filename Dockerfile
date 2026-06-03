FROM python:3.12-slim

WORKDIR /app

# Cài đặt system dependencies cho OpenCV, PaddleOCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=10000

EXPOSE 10000

# Hỗ trợ biến PORT từ hosting (Render, Railway...) với fallback về SERVER_PORT
CMD ["sh", "-c", "export SERVER_PORT=${PORT:-$SERVER_PORT} && python main.py"]