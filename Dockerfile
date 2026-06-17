FROM python:3.12-slim

WORKDIR /app

# ── System dependencies ─────────────────────────────────────────────────────
# libgl1 + libglib2.0-0: OpenCV headless vẫn cần libGL + glib
# libgomp1: PaddlePaddle OpenMP
# Không cần libsm6, libxext6, libxrender1, ffmpeg (chỉ cần với opencv full GUI)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ── Python dependencies ──────────────────────────────────────────────────────
# Copy requirements trước để Docker cache layer này khi code thay đổi
COPY requirements.txt .

# Cài paddlepaddle trước (package lớn nhất, pip resolve tốt hơn khi tách riêng)
# --no-cache-dir: không lưu cache pip trong image
# Tách 2 lệnh RUN để Docker cache từng layer riêng
RUN pip install --no-cache-dir --upgrade pip setuptools \
    && pip install --no-cache-dir paddlepaddle==2.6.2

RUN pip install --no-cache-dir \
    paddleocr==2.7.3 \
    opencv-python-headless==4.11.0.86 \
    numpy==1.26.4 \
    Pillow==11.2.1

RUN pip install --no-cache-dir \
    fastapi==0.115.12 \
    uvicorn==0.34.3 \
    sqlalchemy==2.0.41 \
    psycopg2-binary==2.9.10 \
    httpx==0.28.1 \
    python-dotenv==1.1.0 \
    cloudinary==1.42.1

# ── Application code ─────────────────────────────────────────────────────────
COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=10000

# Tắt PIR API của Paddle (tránh warning khởi động)
ENV FLAGS_enable_pir_api=0

EXPOSE 10000

# Hỗ trợ biến PORT từ hosting (Render, Railway...) với fallback về SERVER_PORT
CMD ["sh", "-c", "export SERVER_PORT=${PORT:-$SERVER_PORT} && python main.py"]