FROM python:3.10-slim
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg libgl1 libglib2.0-0 git curl unzip \
 && rm -rf /var/lib/apt/lists/*

COPY backend/ /app
COPY video_analysis/ /video_analysis

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Añadir video_analysis al PYTHONPATH para que sea importable desde app.py
ENV PYTHONPATH="${PYTHONPATH}:/app/video_analysis"

# Exponer el puerto en el que corre Flask
EXPOSE 5000

# Comando para ejecutar Flask
CMD ["python", "app.py"]
