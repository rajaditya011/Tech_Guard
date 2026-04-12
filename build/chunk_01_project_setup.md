# Chunk 01 — Project Setup

**Goal**: Create the complete folder structure, all pinned dependencies, environment template, and Docker configuration.
**Estimated Time**: 20 minutes
**Dependencies**: Chunk 00
**Unlocks**: Chunk 02 (Backend Core)

---

## 01.1 — Folder Structure Creation Script (setup_structure.sh)

Run this script from the project root to create the entire directory tree.

```bash
#!/bin/bash
# HomeGuardian AI — Folder Structure Setup
# Run from project root: bash setup_structure.sh

echo "Creating HomeGuardian AI directory structure..."

# Backend directories
mkdir -p backend/routers
mkdir -p backend/services
mkdir -p backend/utils
mkdir -p backend/data
mkdir -p backend/models
mkdir -p backend/clips

# Frontend directories (will be initialized by Vite in Chunk 06)
mkdir -p frontend/public/demo
mkdir -p frontend/src/contexts
mkdir -p frontend/src/stores
mkdir -p frontend/src/hooks
mkdir -p frontend/src/components/layout
mkdir -p frontend/src/components/shared
mkdir -p frontend/src/components/old-device
mkdir -p frontend/src/components/dashboard
mkdir -p frontend/src/pages

# Other directories
mkdir -p design
mkdir -p security
mkdir -p build
mkdir -p nginx
mkdir -p scripts

echo "Directory structure created successfully."
```

---

## 01.2 — Backend Dependencies (backend/requirements.txt)

```
# HomeGuardian AI — Python Dependencies
# All versions pinned for reproducibility

# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
aiofiles==23.2.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Database
# SQLite is built into Python — no package needed

# MQTT
paho-mqtt==1.6.1

# Computer Vision
opencv-python==4.8.1.78
ultralytics==8.0.227

# Machine Learning
scikit-learn==1.3.2
numpy==1.26.2
scipy==1.11.4

# AI Narrative Generation
anthropic==0.7.8

# Push Notifications
firebase-admin==6.2.0

# Rate Limiting
slowapi==0.1.9

# WebSocket
websockets==12.0

# Utilities
python-dotenv==1.0.0
Pillow==10.1.0
```

---

## 01.3 — Frontend Dependencies (frontend/package.json)

This is a template. Chunk 06 will initialize the full Vite project, but this defines the dependencies.

```json
{
  "name": "homeguardian-frontend",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext js,jsx"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.1",
    "zustand": "^4.4.7",
    "@tanstack/react-query": "^5.13.4",
    "framer-motion": "^10.16.16",
    "socket.io-client": "^4.7.2",
    "clsx": "^2.0.0"
  },
  "devDependencies": {
    "vite": "^5.0.8",
    "@vitejs/plugin-react": "^4.2.1",
    "tailwindcss": "^3.3.6",
    "postcss": "^8.4.32",
    "autoprefixer": "^10.4.16",
    "eslint": "^8.55.0",
    "eslint-plugin-react": "^7.33.2",
    "eslint-plugin-react-hooks": "^4.6.0"
  }
}
```

---

## 01.4 — Environment Template (.env)

```bash
# ============================================================
# HomeGuardian AI — Environment Configuration
# ============================================================
# Copy this file to .env and fill in your values.
# Variables marked [DEMO_SAFE] are not required when DEMO_MODE=true.

# --- Demo Mode ---
# Set to true to run without any external API keys.
# All features work with synthetic data.
DEMO_MODE=true

# --- Claude API [DEMO_SAFE] ---
# Get your key: https://console.anthropic.com/
CLAUDE_API_KEY=

# --- Firebase Cloud Messaging [DEMO_SAFE] ---
# Get from: Firebase Console > Project Settings > Cloud Messaging
FCM_SERVER_KEY=

# --- MQTT Broker ---
# Default: localhost:1883 (Eclipse Mosquitto)
MQTT_BROKER_URL=localhost
MQTT_PORT=1883

# --- Database ---
# SQLite database file path (relative to backend/)
DB_PATH=data/homeguardian.db

# --- YOLO Model ---
# Path to YOLOv8 weights (relative to backend/)
YOLO_MODEL_PATH=models/yolov8n.pt

# --- Behavioral Baseline ---
# Number of days for baseline learning period
BASELINE_DAYS=14

# Anomaly score threshold (0.0 to 1.0)
ANOMALY_THRESHOLD=0.65

# --- Clip Extraction ---
# Seconds of pre-event frames to include in clip
CLIP_PRE_SECONDS=5

# Seconds of post-event frames to capture
CLIP_POST_SECONDS=10

# --- Authentication ---
# JWT secret key (generate a strong random string)
JWT_SECRET=homeguardian-dev-secret-change-in-production

# JWT access token expiry in minutes
JWT_ACCESS_EXPIRY_MINUTES=15

# JWT refresh token expiry in days
JWT_REFRESH_EXPIRY_DAYS=7

# --- CORS ---
# Comma-separated list of allowed origins
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# --- Server ---
# Backend server port
BACKEND_PORT=8000

# Frontend dev server port
FRONTEND_PORT=5173
```

---

## 01.5 — Git Ignore (.gitignore)

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.egg
*.egg-info/
dist/
build/
.eggs/
*.so
.venv/
venv/
env/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Environment
.env
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project data
backend/data/*.db
backend/clips/*.mp4
backend/models/*.pt
backend/firebase-credentials.json

# Build output
frontend/dist/
*.tar.gz
```

---

## 01.6 — Docker Compose (docker-compose.yml)

```yaml
version: '3.8'

services:
  # ---- MQTT Broker ----
  mqtt-broker:
    image: eclipse-mosquitto:2
    container_name: homeguardian-mqtt
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mosquitto/config:/mosquitto/config
      - ./mosquitto/data:/mosquitto/data
      - ./mosquitto/log:/mosquitto/log
    restart: unless-stopped

  # ---- Backend API ----
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: homeguardian-api
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./backend/data:/app/data
      - ./backend/clips:/app/clips
      - ./backend/models:/app/models
    depends_on:
      - mqtt-broker
    restart: unless-stopped

  # ---- Frontend ----
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: homeguardian-frontend
    ports:
      - "5173:80"
    depends_on:
      - api
    restart: unless-stopped

  # ---- Nginx Reverse Proxy ----
  nginx:
    image: nginx:1.25-alpine
    container_name: homeguardian-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
      - frontend
    restart: unless-stopped
```

---

## 01.7 — Mosquitto Configuration (mosquitto/config/mosquitto.conf)

```
# HomeGuardian AI — Mosquitto Configuration

# Listener for MQTT connections
listener 1883
protocol mqtt

# Listener for WebSocket connections (optional)
listener 9001
protocol websockets

# Allow anonymous connections (development only)
allow_anonymous true

# Persistence
persistence true
persistence_location /mosquitto/data/

# Logging
log_dest stdout
log_type all
connection_messages true
```

---

## 01.8 — Backend Dockerfile (backend/Dockerfile)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data clips models

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 01.9 — Frontend Dockerfile (frontend/Dockerfile)

```dockerfile
FROM node:18-alpine as build

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# Serve with Nginx
FROM nginx:1.25-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 01.10 — Frontend Nginx Config (frontend/nginx.conf)

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # React SPA — route all requests to index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## 01.11 — Nginx Reverse Proxy Config (nginx/nginx.conf)

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    server {
        listen 80;
        server_name localhost;

        # API routes
        location /api/ {
            proxy_pass http://api/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket routes
        location /ws/ {
            proxy_pass http://api/ws/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_read_timeout 86400;
        }

        # Frontend (catch-all)
        location / {
            proxy_pass http://frontend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

---

## Verification

```bash
# 1. Run the structure creation script
bash setup_structure.sh

# 2. Verify the directory tree exists
find . -type d | head -30

# 3. Verify .env template exists
cat .env | head -5

# 4. Install backend dependencies (in a virtual environment)
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Verify Docker Compose config is valid
docker-compose config --quiet && echo "Docker Compose config OK"

# 6. Start MQTT broker
docker-compose up -d mqtt-broker
docker-compose logs mqtt-broker | tail -5

# 7. Run diagnostics to confirm progress
cd ..
python diagnostics.py
```

Expected: Directory structure created. Dependencies install without errors. Docker Compose config validates. MQTT broker starts. Diagnostics shows more PASS results than before.
