# 🏀 Basketlytics

**Basketlytics** es una plataforma web inteligente para el análisis automático de partidos de baloncesto a partir de vídeos. Utiliza modelos de detección y algoritmos de visión por computador para ofrecer estadísticas avanzadas, visualizaciones enriquecidas y un análisis táctico del juego.

---

## 🚀 Funcionalidades

- 📹 **Subida de vídeo** desde el navegador
- 🧠 **Detección de objetos** con modelos de aprendizaje profundo
- 👕 **Asignación automática de equipos**
- ⏱️ **Estadísticas avanzadas de posesión**
- 🏀 **Detección de eventos clave (tiros, pases)**
- 📐 **Homografía y proyección a vista táctica**
- 🎨 **Generación de vídeo final anotado**

---

## 📦 Requisitos

### Instalación local (modo desarrollo)

- Python v3.10 o superior
- Node.js v18
- Sistema operativo: Ubuntu/Debian 20.04 o superior / Windows 10 o superior
- Recomendado: GPU compatible con CUDA 12.4

---

## 🧪 Instalación en local

```bash
# Clonar repositorio
git clone https://github.com/josmarsua/TFG
cd TFG

# Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python backend/app.py

# Frontend
cd frontend
npm install
npm run dev
```

## 🐳 Despliegue con Docker

### Opción A: Máquina con GPU (CUDA 12.4) – Rama `main`

```bash
git checkout main
docker compose up --build -d
```
### Opción B: Despliegue en AWS (solo CPU) – Rama `aws`

```bash
git checkout aws
docker compose up --build -d
```
## 📚 Recursos del proyecto

- 📁 **Repositorio**: [https://github.com/josmarsua/TFG](https://github.com/josmarsua/TFG)
- 📄 **Memoria del proyecto**: *(enlace por definir)*
- 🎥 **Vídeo demo**: *(por añadir)*




