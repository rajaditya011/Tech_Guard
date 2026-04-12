#!/bin/bash
# ============================================================
# HomeGuardian AI — Emergency: 10-Minute Synthetic Demo
# Absolute minimum: DEMO_MODE + synthetic data only.
# No external deps, no MQTT, no AI keys, no Docker.
# Usage: bash scripts/emergency_synthetic_only.sh
# ============================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${RED}=========================================${NC}"
echo -e "${RED}  10-MINUTE EMERGENCY — Synthetic Only${NC}"
echo -e "${RED}=========================================${NC}"
echo ""

# ---- Kill anything running on our ports ----
echo -e "${CYAN}[1/5]${NC} Clearing ports 8000 and 5173..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
sleep 1

# ---- Force DEMO_MODE ----
echo -e "${CYAN}[2/5]${NC} Forcing DEMO_MODE=true in .env..."
cd "$PROJECT_ROOT"
if [ -f .env ]; then
    sed -i.bak 's/DEMO_MODE=.*/DEMO_MODE=true/' .env
    rm -f .env.bak
else
    echo "DEMO_MODE=true" > .env
    echo "JWT_SECRET=demo-emergency-key" >> .env
    echo "DB_PATH=data/homeguardian.db" >> .env
    echo "MQTT_BROKER_URL=localhost" >> .env
    echo "MQTT_PORT=1883" >> .env
    echo "CORS_ORIGINS=http://localhost:5173,http://localhost:3000" >> .env
    echo "YOLO_MODEL_PATH=models/yolov8n.pt" >> .env
    echo "BASELINE_DAYS=14" >> .env
    echo "ANOMALY_THRESHOLD=0.65" >> .env
    echo "CLIP_PRE_SECONDS=5" >> .env
    echo "CLIP_POST_SECONDS=10" >> .env
fi

# ---- Backend: minimal boot ----
echo -e "${CYAN}[3/5]${NC} Booting backend (synthetic mode)..."
cd "$PROJECT_ROOT/backend"
mkdir -p data clips models
if [ -d "venv" ]; then
    source venv/bin/activate
fi
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/hg-api-emergency.log 2>&1 &
API_PID=$!
echo "  API PID: $API_PID (log: /tmp/hg-api-emergency.log)"

# ---- Wait for API ----
echo -e "${CYAN}[4/5]${NC} Waiting for API health..."
for i in $(seq 1 20); do
    if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "  ${GREEN}API ready in ${i}s${NC}"
        break
    fi
    if [ $i -eq 20 ]; then
        echo -e "  ${RED}API failed to start! Check /tmp/hg-api-emergency.log${NC}"
        echo "  Last 10 lines:"
        tail -10 /tmp/hg-api-emergency.log 2>/dev/null
        exit 1
    fi
    sleep 1
done

# ---- Frontend ----
echo -e "${CYAN}[5/5]${NC} Booting frontend..."
cd "$PROJECT_ROOT/frontend"
nohup npm run dev -- --host 0.0.0.0 > /tmp/hg-fe-emergency.log 2>&1 &
FE_PID=$!
echo "  Frontend PID: $FE_PID"
sleep 3

# ---- Inject synthetic demo data via API ----
echo ""
echo -e "${CYAN}Injecting synthetic demo scenarios...${NC}"
curl -sf http://localhost:8000/api/demo/scenarios | python3 -m json.tool 2>/dev/null || echo "(scenarios will load from UI)"

echo ""
echo -e "${GREEN}┌─────────────────────────────────────────┐${NC}"
echo -e "${GREEN}│  SYNTHETIC DEMO READY — GO PRESENT!     │${NC}"
echo -e "${GREEN}└─────────────────────────────────────────┘${NC}"
echo ""
echo -e "  ${BOLD}OPEN THIS NOW:${NC}  ${CYAN}http://localhost:5173/demo${NC}"
echo ""
echo -e "  Quick demo script:"
echo -e "    1. Click ${BOLD}Scenario D${NC} (Full Intrusion) → auto-opens dashboard"
echo -e "    2. Navigate to ${BOLD}AI Reasoning${NC} panel (sidebar: R)"
echo -e "    3. Show ${BOLD}Floor Plan${NC} → drag zones live"
echo -e "    4. Show ${BOLD}Alerts${NC} → click EXPORT PDF"
echo -e "    5. Toggle language: ${BOLD}EN → ES${NC} in header"
echo ""
echo -e "  ${YELLOW}Stop everything:${NC} kill $API_PID $FE_PID"
echo ""
