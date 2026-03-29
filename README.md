# Photo.ai

Photo.ai is an ultra-premium, full-stack AI image processing application. It enables users to effortlessly detect, segment, and securely manipulate objects within images using state-of-the-art machine learning models—all powered through a beautifully crafted, glassmorphic web interface.

## ✨ Features

- **Advanced Object Detection**: Powered by Ultralytics YOLOv8 for rapidly recognizing precise bounding boxes of objects within user uploads.
- **Neural Inpainting & Segmentation**: Utilizes a custom U-Net architecture to perfectly isolate, remove, or effortlessly replace backgrounds behind detected objects.
- **Ultra-Premium UI**: Fully responsive, dark-themed Glassmorphism frontend with animated micro-interactions (built purely in vanilla HTML/CSS/JS for high performance).
- **Secure Authentication**: Custom user registration and complete login flows using SQLAlchemy, capable of connecting to PostgreSQL (Supabase) or falling back to local SQLite.
- **Production-Ready Rate Limiting**: API endpoints are guarded against spam and brute-force attacks via endpoint-specific `slowapi` rate limits.
- **Built for Deployment**: Specifically configured for containerized deployment on Render (includes configured `Procfile`, flexible environment variables, and memory-aware configuration).

## 🛠️ Technology Stack

- **Backend Web Server**: FastAPI, Uvicorn, Slowapi, Python-Multipart
- **Database & ORM**: SQLAlchemy, psycopg2-binary
- **AI & Computer Vision**: OpenCV, NumPy, Ultralytics (YOLO), TensorFlow
- **Frontend**: Vanilla HTML5, CSS3, Vanilla JS

## 🚀 Local Development Setup

### 1. Requirements
- Python 3.9+
- Recommended: A dedicated Python Virtual Environment.

### 2. Installation
Clone the repository and install all required ML and server dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
To connect to a production Supabase/PostgreSQL database, create a `.env` file at the root of the project with your connection string:
```bash
DATABASE_URL=postgresql://postgres:[password]...
SECRET_KEY=your_secure_secret_key
```
*(If no `DATABASE_URL` is provided, the app will gracefully fall back to a local `db.sqlite` file).*

### 4. Running the Backend Server
Navigate into the `backend` directory and start the Uvicorn ASGI server:
```bash
cd backend
python -m uvicorn code:app --reload
```
The FastAPI documentation will be available locally at `http://127.0.0.1:8000/docs`.

### 5. Running the Frontend
Because the frontend is built entirely statically, you do not need a complicated framework to run it. You can simply open the files in your browser:
- Open `frontend/main_interface.html` to view the primary unified dashboard.
- Or, utilize an extension like **VS Code Live Server** on port `5500` to serve the HTML dynamically.

## ☁️ Deployment (Render)
This project is configured right out of the box for Render!
1. Create a new **Web Service** on Render.
2. Link your Git repository.
3. Because a `Procfile` is located in the root directory, Render will automatically detect the start command:
   ```bash
   web: cd backend && uvicorn code:app --host 0.0.0.0 --port $PORT
   ```
4. *Important:* Ensure you upgrade your Render instance to a tier with **at least 1GB - 2GB RAM**, as YOLOv8 and TensorFlow U-Net loaded into memory will easily crash the free tier instances.
