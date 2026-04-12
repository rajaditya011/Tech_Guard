# Chunk 00 — Manifest and Diagnostics

**Goal**: Create the build order tracker, status table, and self-test diagnostics script.
**Estimated Time**: 15 minutes
**Dependencies**: None
**Unlocks**: Chunk 01 (Project Setup)

---

## 00.1 — Build Manifest (build_manifest.json)

This file tracks what has been built and what remains. Every AI session updates this file.

```json
{
  "project": "HomeGuardian AI",
  "version": "1.0.0",
  "last_updated": "2026-04-11",
  "chunks": [
    {
      "id": "00",
      "name": "Manifest and Diagnostics",
      "status": "not_started",
      "depends_on": [],
      "parallel_ok": false,
      "completed_at": null,
      "completed_by": null
    },
    {
      "id": "01",
      "name": "Project Setup",
      "status": "not_started",
      "depends_on": ["00"],
      "parallel_ok": false,
      "completed_at": null,
      "completed_by": null
    },
    {
      "id": "02",
      "name": "Backend Core",
      "status": "not_started",
      "depends_on": ["01"],
      "parallel_ok": false,
      "completed_at": null,
      "completed_by": null
    },
    {
      "id": "03",
      "name": "Sensor Data Pipeline",
      "status": "not_started",
      "depends_on": ["02"],
      "parallel_ok": true,
      "completed_at": null,
      "completed_by": null
    },
    {
      "id": "04",
      "name": "ML and Anomaly Detection",
      "status": "not_started",
      "depends_on": ["03"],
      "parallel_ok": false,
      "completed_at": null,
      "completed_by": null
    },
    {
      "id": "05",
      "name": "Intelligence Response Layer",
      "status": "not_started",
      "depends_on": ["04"],
      "parallel_ok": false,
      "completed_at": null,
      "completed_by": null
    },
    {
      "id": "06",
      "name": "Frontend Shell and Design System",
      "status": "not_started",
      "depends_on": ["02"],
      "parallel_ok": true,
      "completed_at": null,
      "completed_by": null
    },
    {
      "id": "07",
      "name": "Old Device Portal",
      "status": "not_started",
      "depends_on": ["06"],
      "parallel_ok": true,
      "completed_at": null,
      "completed_by": null
    },
    {
      "id": "08",
      "name": "New Device Dashboard",
      "status": "not_started",
      "depends_on": ["06"],
      "parallel_ok": true,
      "completed_at": null,
      "completed_by": null
    },
    {
      "id": "09",
      "name": "Secret Weapon, Security, Deploy",
      "status": "not_started",
      "depends_on": ["05", "08"],
      "parallel_ok": false,
      "completed_at": null,
      "completed_by": null
    }
  ]
}
```

---

## 00.2 — Diagnostics Script (diagnostics.py)

Place this file at the project root: `diagnostics.py`

```python
#!/usr/bin/env python3
"""
HomeGuardian AI — System Diagnostics
Runs all environment and dependency checks.
Each test outputs [PASS] or [FAIL] with an exact fix command.
"""

import sys
import os
import subprocess
import importlib
import json
from pathlib import Path


# ============================================================
# Configuration
# ============================================================
PROJECT_ROOT = Path(__file__).parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
ENV_FILE = PROJECT_ROOT / ".env"
DB_PATH = PROJECT_ROOT / "backend" / "data" / "homeguardian.db"
YOLO_MODEL_PATH = PROJECT_ROOT / "backend" / "models" / "yolov8n.pt"

REQUIRED_ENV_VARS = [
    "CLAUDE_API_KEY", "FCM_SERVER_KEY", "MQTT_BROKER_URL", "MQTT_PORT",
    "DB_PATH", "YOLO_MODEL_PATH", "BASELINE_DAYS", "ANOMALY_THRESHOLD",
    "CLIP_PRE_SECONDS", "CLIP_POST_SECONDS", "JWT_SECRET", "CORS_ORIGINS", "DEMO_MODE"
]

REQUIRED_PIP_PACKAGES = [
    "fastapi", "uvicorn", "pydantic", "python-jose", "passlib",
    "paho.mqtt.client", "cv2", "ultralytics", "sklearn",
    "anthropic", "firebase_admin", "slowapi", "python_multipart",
    "sqlalchemy", "aiofiles", "websockets"
]

REQUIRED_NPM_PACKAGES = [
    "react", "react-dom", "react-router-dom", "zustand",
    "@tanstack/react-query", "framer-motion", "socket.io-client",
    "tailwindcss", "vite"
]


# ============================================================
# Test Runner
# ============================================================
class DiagnosticRunner:
    def __init__(self):
        self.results = []
        self.pass_count = 0
        self.fail_count = 0

    def test(self, name, passed, fix_hint=""):
        status = "[PASS]" if passed else "[FAIL]"
        self.results.append((status, name, fix_hint))
        if passed:
            self.pass_count += 1
        else:
            self.fail_count += 1
        icon = "\033[92m[PASS]\033[0m" if passed else "\033[91m[FAIL]\033[0m"
        print(f"  {icon} {name}")
        if not passed and fix_hint:
            print(f"         Fix: {fix_hint}")

    def summary(self):
        total = self.pass_count + self.fail_count
        print(f"\n{'='*60}")
        print(f"  Results: {self.pass_count}/{total} passed, {self.fail_count} failed")
        if self.fail_count == 0:
            print("  \033[92mAll diagnostics passed. System is ready.\033[0m")
        else:
            print("  \033[91mSome diagnostics failed. See fix hints above.\033[0m")
        print(f"{'='*60}\n")
        return self.fail_count == 0


def run_diagnostics():
    print("\n" + "=" * 60)
    print("  HomeGuardian AI — System Diagnostics")
    print("=" * 60 + "\n")

    runner = DiagnosticRunner()

    # ---- 1. Python Version ----
    print("[1/12] Python Version")
    py_version = sys.version_info
    runner.test(
        f"Python {py_version.major}.{py_version.minor}.{py_version.micro}",
        py_version >= (3, 11),
        "Install Python 3.11+: brew install python@3.11"
    )

    # ---- 2. Node Version ----
    print("\n[2/12] Node Version")
    try:
        node_output = subprocess.check_output(
            ["node", "--version"], stderr=subprocess.DEVNULL
        ).decode().strip()
        node_major = int(node_output.lstrip("v").split(".")[0])
        runner.test(
            f"Node.js {node_output}",
            node_major >= 18,
            "Install Node 18+: brew install node"
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        runner.test("Node.js not found", False, "Install Node.js 18+: brew install node")

    # ---- 3. pip Packages ----
    print("\n[3/12] Python Packages")
    for pkg in REQUIRED_PIP_PACKAGES:
        import_name = pkg.replace("-", "_").replace(".", ".")
        try:
            importlib.import_module(import_name.split(".")[0])
            runner.test(f"  {pkg}", True)
        except ImportError:
            pip_name = pkg.replace(".", "-").replace("_", "-")
            if pkg == "cv2":
                pip_name = "opencv-python"
            elif pkg == "sklearn":
                pip_name = "scikit-learn"
            elif pkg == "paho.mqtt.client":
                pip_name = "paho-mqtt"
            runner.test(f"  {pkg}", False, f"pip install {pip_name}")

    # ---- 4. npm Packages ----
    print("\n[4/12] NPM Packages")
    package_json = FRONTEND_DIR / "package.json"
    if package_json.exists():
        with open(package_json) as f:
            pkg_data = json.load(f)
        all_deps = {
            **pkg_data.get("dependencies", {}),
            **pkg_data.get("devDependencies", {})
        }
        for pkg in REQUIRED_NPM_PACKAGES:
            runner.test(
                f"  {pkg}",
                pkg in all_deps,
                f"cd frontend && npm install {pkg}"
            )
    else:
        runner.test(
            "package.json exists",
            False,
            "Run Chunk 06 to create the frontend project"
        )

    # ---- 5. .env File ----
    print("\n[5/12] Environment Configuration")
    if ENV_FILE.exists():
        with open(ENV_FILE) as f:
            env_content = f.read()
        runner.test(".env file exists", True)
        for var in REQUIRED_ENV_VARS:
            present = var + "=" in env_content
            runner.test(
                f"  {var}",
                present,
                f'Add {var}=<value> to .env file'
            )
    else:
        runner.test(
            ".env file exists",
            False,
            "Run Chunk 01 to create the .env template"
        )

    # ---- 6. SQLite Writable ----
    print("\n[6/12] SQLite Database")
    try:
        db_dir = DB_PATH.parent
        db_dir.mkdir(parents=True, exist_ok=True)
        import sqlite3
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute("CREATE TABLE IF NOT EXISTS _diag_test (id INTEGER)")
        conn.execute("DROP TABLE IF EXISTS _diag_test")
        conn.close()
        runner.test("SQLite writable", True)
    except Exception as e:
        runner.test(
            "SQLite writable",
            False,
            f"Check permissions on {DB_PATH.parent}: chmod 755 {DB_PATH.parent}"
        )

    # ---- 7. MQTT Broker ----
    print("\n[7/12] MQTT Broker")
    try:
        import socket
        mqtt_host = os.getenv("MQTT_BROKER_URL", "localhost")
        mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
        sock = socket.create_connection((mqtt_host, mqtt_port), timeout=3)
        sock.close()
        runner.test(f"MQTT broker reachable at {mqtt_host}:{mqtt_port}", True)
    except Exception:
        runner.test(
            "MQTT broker reachable",
            False,
            "Start Mosquitto: docker run -d -p 1883:1883 eclipse-mosquitto OR brew services start mosquitto"
        )

    # ---- 8. OpenCV ----
    print("\n[8/12] OpenCV")
    try:
        import cv2
        runner.test(f"OpenCV {cv2.__version__}", True)
    except ImportError:
        runner.test("OpenCV", False, "pip install opencv-python")

    # ---- 9. YOLO Weights ----
    print("\n[9/12] YOLO Weights")
    runner.test(
        f"YOLO model at {YOLO_MODEL_PATH}",
        YOLO_MODEL_PATH.exists(),
        "Download: python -c \"from ultralytics import YOLO; YOLO('yolov8n.pt')\" && mv yolov8n.pt backend/models/"
    )

    # ---- 10. Claude API Key ----
    print("\n[10/12] Claude API Key")
    demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
    claude_key = os.getenv("CLAUDE_API_KEY", "")
    if demo_mode:
        runner.test("Claude API key (DEMO_MODE=true, skipped)", True)
    elif claude_key and claude_key.startswith("sk-ant-"):
        runner.test("Claude API key present and formatted correctly", True)
    else:
        runner.test(
            "Claude API key",
            False,
            "Set CLAUDE_API_KEY=sk-ant-... in .env OR set DEMO_MODE=true"
        )

    # ---- 11. FCM Credentials ----
    print("\n[11/12] Firebase Credentials")
    fcm_creds = PROJECT_ROOT / "backend" / "firebase-credentials.json"
    if demo_mode:
        runner.test("FCM credentials (DEMO_MODE=true, skipped)", True)
    elif fcm_creds.exists():
        runner.test("Firebase credentials file exists", True)
    else:
        runner.test(
            "Firebase credentials file",
            False,
            "Download from Firebase Console > Project Settings > Service Accounts OR set DEMO_MODE=true"
        )

    # ---- 12. WebSocket Server ----
    print("\n[12/12] WebSocket Server")
    try:
        import socket
        sock = socket.create_connection(("localhost", 8000), timeout=2)
        sock.close()
        runner.test("Backend server reachable on port 8000", True)
    except Exception:
        runner.test(
            "Backend server reachable on port 8000",
            False,
            "Start backend: cd backend && uvicorn main:app --reload --port 8000"
        )

    # ---- Summary ----
    runner.summary()
    return 0 if runner.fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(run_diagnostics())
```

---

## Verification

After creating both files, run:

```bash
# Verify manifest file is valid JSON
python -c "import json; json.load(open('build_manifest.json'))" && echo "Manifest OK"

# Run diagnostics (some will fail since nothing is set up yet — this is expected)
python diagnostics.py
```

Expected: Manifest parses successfully. Diagnostics runs and reports FAIL for most tests (Python version and SQLite should PASS). All failures should show clear fix commands.
