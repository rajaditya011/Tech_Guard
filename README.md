# Tech Guard (HomeGuardian AI) — Adaptive Intelligence Security System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Tech Guard** is a self-learning AI nervous system for smart homes designed to detect intent-level anomalies rather than simple movement. By bridging "Old Device" sensor nodes with a sophisticated "New Device" owner dashboard, it provides a comprehensive security layer that understands behavior.

## 🚀 Overview

- **Project Name**: Tech Guard (HomeGuardian AI)
- **Tagline**: Understanding behavior, not just detecting movement.
- **Challenge**: Hackathon Challenge 06 — Smart Home Security Monitor
- **Philosophy**: Intent-level anomaly detection using dual-portal architecture.

---

## ✨ Key Features

- **Dual-Portal Architecture**: Separate authenticated experiences for sensor nodes (Old Devices) and owner dashboards (New Devices).
- **Behavioral Analysis**: Uses YOLOv8 and Isolation Forests to detect intent, not just motion.
- **Real-time Monitoring**: Low-latency video streaming and MQTT-based sensor data pipeline.
- **AI-Generated Narratives**: Integration with Claude API for human-readable incident reports.
- **Democratic Deployment**: Works with legacy hardware (old smartphones/tablets) as sensor nodes.

---

## 🛠️ Tech Stack

| Layer           | Technology               | Purpose                                  |
| --------------- | ------------------------ | ---------------------------------------- |
| **Backend**     | Python (FastAPI)         | Core REST API and WebSocket server        |
| **Database**    | SQLite                   | Lightweight persistent storage           |
| **IoT/Messaging**| Mosquitto (MQTT)         | Local IoT message broker                 |
| **Computer Vision**| OpenCV & YOLOv8         | Object detection and frame processing    |
| **Machine Learning**| scikit-learn            | Anomaly detection engines                |
| **Frontend**    | React + Vite             | Modern, responsive user interface        |
| **Styling**     | TailwindCSS              | Utility-first responsive design          |
| **Orchestration**| Docker / Compose         | Containerized service management         |

---

## 📦 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional, for full stack)

### Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/hairy-progress123/Tech_guard.git
   cd Tech_guard
   ```

2. **Environment Configuration**:
   Create a `.env` file in the root directory and populate it with your keys (or use `DEMO_MODE=true` for testing without API keys).

3. **Quick Start (Manual)**:
   Use the provided `Makefile` to start services:
   ```bash
   make dev          # Start backend + frontend in parallel
   ```

4. **Docker Deployment**:
   ```bash
   make build        # Build images
   make up           # Start the full stack
   ```

### Diagnostics
Run the system diagnostics to ensure your environment is configured correctly:
```bash
python diagnostics.py
```

---

## 📂 Project Structure

- `/backend`: FastAPI server, ML logic, and database management.
- `/frontend`: React dashboard and owner portal.
- `/ui`: Premium celestial-themed landing page.
- `/mosquitto`: MQTT broker configuration.
- `/security`: Security audit checklists and hardening guides.
- `/design`: UI/UX design tokens and design system documentation.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 🤖 For AI Contributors

If you are an AI assistant working on this project, please refer to [AI_GUIDELINES.md](AI_GUIDELINES.md) for internal protocols, build orders, and rules.
