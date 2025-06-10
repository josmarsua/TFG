# 🏀 Basketlytics

**Basketlytics** es una plataforma web inteligente para el análisis automático de partidos de baloncesto a partir de vídeos. Utiliza modelos de detección y algoritmos de visión por computador para ofrecer estadísticas avanzadas, visualizaciones enriquecidas y un análisis táctico del juego.

Tactical and statistical analysis in professional basketball typically relies on proprietary tools and manual processes, which limit accessibility in amateur or semi-professional contexts. This project presents a fully automated solution for basketball game analysis based solely on video input, requiring no specialized sensors or equipment. The implemented system leverages computer vision and deep learning techniques to detect and track players, the ball, and referees; automatically assigns teams through color-based clustering; and projects spatial positions onto a virtual top-down court view using homography. Furthermore, it infers ball possession, detects key events such as shots and passes, and generates dynamic visualizations that are rendered within an interactive web application accessible via browser.

**Keywords**: computer vision, basketball, deep learning, YOLO, sports analytics, action detection.

---

## 🚀 Funcionalidades

- 📹 **Subida de vídeo** desde el navegador
- 🧠 **Detección de objetos** con modelos de aprendizaje profundo (YOLO)
- 👕 **Asignación automática de equipos** mediante clustering K-Means
- ⏱️ **Estadísticas avanzadas de posesión**
- 🏀 **Detección de eventos clave (tiros, pases)**
- 📐 **Homografía y proyección a vista táctica** utilizando homografía y transformación de perspectiva
- 🎨 **Generación de vídeo final anotado**
<table>
  <tr>
    <td>
      ![vistapaginaprincipal](https://github.com/user-attachments/assets/fce9dc75-f036-41d1-999b-20853d0151e3)
    </td>
    <td>
      ![vistaregister](https://github.com/user-attachments/assets/3854daf5-42a8-48bf-995f-7467074eaaa2)
    </td>
  </tr>
  <tr>
    <td>
      ![vistadashboard](https://github.com/user-attachments/assets/4f44a562-91d4-497c-b11b-caf36f91c3aa)
    </td>
    <td>
      ![vistaprocess](https://github.com/user-attachments/assets/1e94f6be-f212-4965-8ff1-3809fbce1caa)
    </td>
  </tr>
</table>

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

- 📦 **Modelos preentrenados**: [https://drive.google.com/drive/folders/1znXEIR6sPuR8oprElCuK32V6d7o2L1AJ?usp=sharing] Estos modelos deben incluirse en ```video_analysis/models```
- 📁 **Repositorio**: [https://github.com/josmarsua/TFG](https://github.com/josmarsua/TFG)
- 📄 **Memoria del proyecto**: *(enlace por definir)*
- 🎥 **Vídeo demo**:
[![capturademo](https://github.com/user-attachments/assets/5007a073-8e90-4fcd-be6e-08c31bec096f)](https://www.youtube.com/watch?v=n4v1BjWUU1c&ab_channel=Jos%C3%A9Mart%C3%ADnezSu%C3%A1rez)




