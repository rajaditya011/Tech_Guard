# HomeGuardian AI — Adaptive Intelligence Security System

**Version**: 1.0.0
**Last Updated**: 2026-04-11
**Status**: Scaffolding Complete — Ready for Build

---

## 1. Project Identity

| Field              | Value                                                                              |
| ------------------ | ---------------------------------------------------------------------------------- |
| **Project Name**   | HomeGuardian AI                                                                    |
| **Tagline**        | Understanding behavior, not just detecting movement.                               |
| **Challenge**      | Hackathon Challenge 06 — Smart Home Security Monitor                               |
| **Core Philosophy**| Self-learning AI nervous system for homes that detects intent-level anomalies       |
| **Architecture**   | Dual-portal (Old Device sensor nodes + New Device owner dashboard) with AI hub     |

---

## 2. Complete File Map

```
home_guard_ai/
|
|-- README.md                           # THIS FILE — Master AI context map
|-- IMPLEMENTATION_PLAN.md              # Full technical specification (v1.0)
|-- CHANGELOG.md                        # Version history and AI session log
|-- COMMANDS.md                         # Human-only copy-paste command shortcuts
|-- TEAMMATE_GUIDE.md                   # Non-technical presentation guide
|-- ui/                                 # Premium React landing page (Celestial theme)
|   |-- src/App.tsx                      # Main app with Starfield, GoldDust, ShootingStars
|   |-- src/components/                  # FeatureCards, Architecture, DemoSection, TechStack
|   |-- src/index.css                    # Celestial gold design system
|
|-- build/
|   |-- chunk_00_manifest_diagnostics.md   # Build manifest + diagnostics script
|   |-- chunk_01_project_setup.md          # Folder structure, deps, env, Docker
|   |-- chunk_02_backend_core.md           # FastAPI, DB, JWT, MQTT, WebSocket
|   |-- chunk_03_sensor_pipeline.md        # MQTT ingestion, frame buffering, streaming
|   |-- chunk_04_ml_anomaly_engine.md      # Baseline, YOLO, Isolation Forest, fusion
|   |-- chunk_05_intelligence_response.md  # Clip extraction, Claude, alerts, comms
|   |-- chunk_06_frontend_shell.md         # React+Vite, design tokens, routing
|   |-- chunk_07_old_device_portal.md      # Old device enrollment, stream, baseline UI
|   |-- chunk_08_new_device_dashboard.md   # Owner dashboard, floor plan, alerts, AI
|   |-- chunk_09_secret_weapon_deploy.md   # Prediction engine, security, deployment
|
|-- design/
|   |-- UI_DESIGN_PROMPTS.md            # Component visual specs and design tokens
|
|-- security/
|   |-- SECURITY_CHECKLIST.md           # 60+ item security audit checklist
```

---

## 3. AI Handoff Protocol

### Session Start (Every AI Must Do This)

1. **Read** `CHANGELOG.md` — find the last entry, understand current state.
2. **Read** `README.md` (this file) — understand the build order and status.
3. **Read** the relevant `build/chunk_XX_*.md` file for the next incomplete chunk.
4. **Run diagnostics** (see Section 7) to confirm the current environment state.
5. **Begin work** on the next incomplete chunk only.

### Session End (Every AI Must Do This)

1. **Update** `CHANGELOG.md` — add a new entry using the template at the bottom.
2. **Update** the Build Status Table below — mark chunks as complete/in-progress.
3. **Run diagnostics** to verify everything still passes.
4. **Note** any blockers, known issues, or decisions made for the next AI session.

---

## 4. Build Order — Dependency Graph

```
Chunk 00: Manifest + Diagnostics
    |
Chunk 01: Project Setup (folders, deps, env)
    |
Chunk 02: Backend Core (FastAPI, DB, auth, MQTT, WS)
    |
    +-------+-------+
    |               |
Chunk 03:       Chunk 06:
Sensor Pipeline  Frontend Shell
    |               |
Chunk 04:       Chunk 07:
ML + Anomaly     Old Device Portal
    |               |
Chunk 05:       Chunk 08:
Intelligence     New Device Dashboard
    |               |
    +-------+-------+
            |
        Chunk 09:
        Secret Weapon + Security + Deploy
```

---

## 5. Build Status Table

| Chunk | Name                            | Depends On  | Parallel OK | Status      |
| ----- | ------------------------------- | ----------- | ----------- | ----------- |
| 00    | Manifest and Diagnostics        | None        | --          | COMPLETE    |
| 01    | Project Setup                   | 00          | No          | COMPLETE    |
| 02    | Backend Core                    | 01          | No          | COMPLETE    |
| 03    | Sensor Data Pipeline            | 02          | Yes (w/ 06) | COMPLETE    |
| 04    | ML and Anomaly Detection        | 03          | No          | COMPLETE    |
| 05    | Intelligence Response Layer     | 04          | No          | COMPLETE    |
| 06    | Frontend Shell and Design       | 02          | Yes (w/ 03) | COMPLETE    |
| 07    | Old Device Portal               | 06          | Yes (w/ 04) | COMPLETE    |
| 08    | New Device Dashboard            | 06          | Yes (w/ 05) | COMPLETE    |
| 09    | Secret Weapon + Security + Deploy | 05, 08    | No          | COMPLETE    |

---

## 6. Tech Stack Table

| Layer           | Technology               | Version    | Purpose                                  |
| --------------- | ------------------------ | ---------- | ---------------------------------------- |
| Backend API     | Python                   | 3.11+      | Core language                            |
| Backend API     | FastAPI                  | 0.104+     | REST API and WebSocket server            |
| Database        | SQLite                   | 3.x        | Lightweight persistent storage           |
| IoT Messaging   | Eclipse Mosquitto        | 2.0+       | Self-hosted MQTT broker                  |
| IoT Client      | paho-mqtt                | 1.6+       | Python MQTT client                       |
| Object Detection| Ultralytics YOLOv8       | 8.0+       | Human detection on video frames          |
| Computer Vision | OpenCV                   | 4.8+       | Frame processing and clip encoding       |
| ML / Stats      | scikit-learn             | 1.3+       | Isolation Forest, DBSCAN clustering      |
| AI Narratives   | Claude API (Anthropic)   | Latest     | Incident narrative generation            |
| Push Notify     | Firebase Admin SDK       | 6.x        | FCM push notifications                   |
| Auth            | python-jose              | 3.3+       | JWT token management                     |
| Rate Limiting   | slowapi                  | 0.1+       | API rate limiting                        |
| Frontend        | React                    | 18.x       | UI framework                             |
| Build Tool      | Vite                     | 5.x        | Frontend build and dev server            |
| CSS Framework   | TailwindCSS              | 3.x        | Utility-first styling                    |
| State Mgmt      | Zustand                  | 4.x        | Lightweight state management             |
| Routing         | react-router-dom         | 6.x        | Client-side routing                      |
| Data Fetching   | react-query              | 5.x        | Server state management                  |
| Animations      | framer-motion            | 10.x       | UI animations and transitions            |
| WebSocket       | socket.io-client         | 4.x        | Real-time client communication           |
| Reverse Proxy   | Nginx                    | 1.25+      | Reverse proxy with SSL                   |
| Containers      | Docker + docker-compose  | 24.x / 2.x| Service orchestration                    |

---

## 7. API Keys Table

| Service                | URL to Get Key                                     | Free Tier Limits                            |
| ---------------------- | -------------------------------------------------- | ------------------------------------------- |
| Claude API (Anthropic) | https://console.anthropic.com/                     | $5 free credit on signup                    |
| Firebase (FCM)         | https://console.firebase.google.com/               | Unlimited push notifications (free)         |
| MQTT (Mosquitto)       | Self-hosted — no key needed                        | N/A — runs locally                          |
| YOLO (Ultralytics)     | pip install ultralytics — no key needed             | Free for non-commercial, local inference    |

**IMPORTANT**: The project MUST work without ANY API keys via `DEMO_MODE=true`. All external API calls are bypassed with pre-loaded synthetic data in demo mode.

---

## 8. Diagnostics System

The diagnostics script is defined in `build/chunk_00_manifest_diagnostics.md`. It tests:

| Test                        | What It Checks                                     |
| --------------------------- | -------------------------------------------------- |
| Python version              | Python 3.11+ installed                             |
| Node version                | Node 18+ installed                                 |
| pip packages                | All requirements.txt packages importable           |
| npm packages                | All package.json deps installed                    |
| .env file                   | .env exists and contains all required variables    |
| SQLite writable             | Can create/write to DB file                        |
| MQTT broker                 | Mosquitto reachable on configured host:port        |
| OpenCV import               | cv2 imports successfully                           |
| YOLO weights                | Model file exists at configured path               |
| Claude API key              | Key present and valid (or DEMO_MODE=true)          |
| FCM credentials             | Firebase credentials file exists (or DEMO_MODE)    |
| WebSocket server            | WS endpoint starts and accepts connections         |

Each test outputs `[PASS]` or `[FAIL]` with an exact fix command.

Run diagnostics:
```bash
python diagnostics.py
```

---

## 9. Rules for All AI Workers

1. **Follow chunk files exactly.** Each chunk in `build/` contains complete, copy-paste-ready code. Do not improvise when a chunk provides exact code.
2. **Use design tokens.** All colors, spacing, typography, and animation values MUST use CSS custom properties defined in `design/UI_DESIGN_PROMPTS.md`. Never hardcode visual values.
3. **Demo mode is required.** Every feature MUST work with `DEMO_MODE=true` and zero API keys. Pre-loaded demo data for all four scenarios (Normal Routine, Late Night Anomaly, Casing Simulation, Full Intrusion Prediction).
4. **Log to CHANGELOG.md.** Every AI session must add a timestamped entry documenting what was built, modified, and any decisions made.
5. **Both portals always present.** Never remove or disable either the Old Device Portal or the New Device Dashboard. They are separate authenticated experiences.
6. **Theme always works.** Every UI component must render correctly in both light and dark themes. Test both before marking a frontend chunk complete.
7. **Security from day one.** Input sanitization, parameterized SQL, CORS, rate limiting, MQTT access control. Follow `security/SECURITY_CHECKLIST.md`.
8. **Verify each chunk.** Run the verification commands at the end of each chunk file before moving to the next.
9. **No emojis.** Use professional text markers, numbered lists, and colored badges throughout all files and UI.
10. **Production quality.** This is production-grade work. Clean code, proper error handling, meaningful variable names, documented functions.
11. **Respect dependency order.** Follow the build order graph. Do not skip ahead.
12. **Preserve existing work.** When building a new chunk, verify that all previously completed chunks still function correctly.

---

## 10. UI Flexibility Notice

The user interface is designed for rapid iteration:

- **All CSS uses custom properties (variables).** Changing one variable updates the entire application globally.
- **Components are modular.** Any component can be replaced, restyled, or removed without breaking other components.
- **Theme switching is instant.** A single class toggle on `<html>` switches between light and dark themes.
- **Layout is responsive.** All layouts use CSS Grid and Flexbox with relative units.
- **Design tokens are centralized.** See `design/UI_DESIGN_PROMPTS.md` for the complete token system.

Any AI can redesign any component by modifying its tokens and component file without touching the rest of the system.

---

## Quick Start for New AI Sessions

```
1. Read CHANGELOG.md          -- What has been done?
2. Read this README.md         -- What is the plan?
3. Check Build Status Table    -- What is next?
4. Read the next chunk file    -- What exactly to build?
5. Build it                    -- Follow the chunk exactly
6. Verify it                   -- Run chunk verification commands
7. Update CHANGELOG.md         -- Log your work
8. Update Build Status Table   -- Mark chunk status
```
