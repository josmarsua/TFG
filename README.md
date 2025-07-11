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
      <img src="https://github.com/user-attachments/assets/acaf248d-2fa8-4d6b-96f4-640d5b7e1abb" width="400" />
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/69cd59d9-a5c1-4797-9718-8f8a7a305762" width="400" />
    </td>
  </tr>
  <tr>
    <td>
      <img src="https://github.com/user-attachments/assets/5f1a9e41-9098-458e-832d-bf995952d626" width="400" />
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/b9a1114f-5f2c-46ce-aea1-523a065857ef" width="400" />
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




