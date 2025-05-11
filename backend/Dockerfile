FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Instalar Python 3.10 y otras dependencias del sistema
RUN apt-get update && apt-get install -y \
    python3.10 python3-pip python3.10-venv \
    libgl1 libglib2.0-0 ffmpeg git curl unzip \
 && ln -sf /usr/bin/python3.10 /usr/bin/python \
 && ln -sf /usr/bin/pip3 /usr/bin/pip \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar código fuente
COPY backend/ /app
COPY video_analysis/ /video_analysis

# Instalar dependencias de Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
