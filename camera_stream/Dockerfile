# Python 3.9-slim asosidagi rasmni tanlaymiz
FROM python:3.9-slim

# Konsol chiqishlarini buferlamaslik uchun
ENV PYTHONUNBUFFERED=1

# Tizim paketlarini yangilab, ffmpeg va boshqa kerakli kutubxonalarni o'rnatamiz
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Ishchi katalogni yaratamiz
WORKDIR /app

# requirements.txt faylini nusxalab, Python paketlarini o'rnatamiz
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Ilovaning qolgan kodlarini nusxalash
COPY . .

# 8000-portni ochamiz
EXPOSE 8000

# Uvicorn orqali ilovani 0.0.0.0:8000 da ishga tushiramiz
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]