#!/bin/bash
# ============================================================
# HomeGuardian AI — Emergency: Crash Recovery
# The demo crashed mid-presentation. Get back online NOW.
# Usage: bash scripts/emergency_recover.sh
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
echo -e "${RED}  CRASH RECOVERY — Restarting NOW${NC}"
echo -e "${RED}=========================================${NC}"
echo ""

RECOVER_START=$(date +%s)

# ---- Step 1: Kill zombie processes ----
echo -e "${CYAN}[1/5]${NC} Killing stale processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
docker stop homeguardian-mqtt 2>/dev/null || true
sleep 1
echo "  Ports 8000 and 5173 cleared."

# ---- Step 2: Verify .env is sane ----
echo -e "${CYAN}[2/5]${NC} Checking .env..."
cd "$PROJECT_ROOT"
if [ ! -f .env ]; then
    echo -e "  ${RED}.env missing! Creating minimal config...${NC}"
    cat > .env << 'EOF'
DEMO_MODE=true
JWT_SECRET=homeguardian-dev-secret-change-in-production
DB_PATH=data/homeguardian.db
MQTT_BROKER_URL=localhost
MQTT_PORT=1883
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
YOLO_MODEL_PATH=models/yolov8n.pt
BASELINE_DAYS=14
ANOMALY_THRESHOLD=0.65
CLIP_PRE_SECONDS=5
CLIP_POST_SECONDS=10
EOF
fi
# Ensure DEMO_MODE is true for recovery
sed -i.bak 's/DEMO_MODE=.*/DEMO_MODE=true/' .env
rm -f .env.bak
echo "  .env verified, DEMO_MODE=true."

# ---- Step 3: Restart backend ----
echo -e "${CYAN}[3/5]${NC} Restarting backend..."
cd "$PROJECT_ROOT/backend"
mkdir -p data clips models
if [ -d "venv" ]; then
    source venv/bin/activate
fi
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/hg-recover-api.log 2>&1 &
API_PID=$!

# Wait for health
for i in $(seq 1 15); do
    if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "  ${GREEN}API recovered in ${i}s (PID: $API_PID)${NC}"
        break
    fi
    if [ $i -eq 15 ]; then
        echo -e "  ${RED}API failed! Dumping last log lines:${NC}"
        tail -5 /tmp/hg-recover-api.log 2>/dev/null
        echo ""
        echo -e "  ${YELLOW}Try: cd backend && source venv/bin/activate && uvicorn main:app --port 8000${NC}"
        exit 1
    fi
    sleep 1
done

# ---- Step 4: Restart frontend ----
echo -e "${CYAN}[4/5]${NC} Restarting frontend..."
cd "$PROJECT_ROOT/frontend"
nohup npm run dev -- --host 0.0.0.0 > /tmp/hg-recover-fe.log 2>&1 &
FE_PID=$!
sleep 3
echo "  Frontend started (PID: $FE_PID)"

# ---- Step 5: Resume demo scenario ----
echo -e "${CYAN}[5/5]${NC} Resuming last demo scenario..."
# Try to start Scenario D (Full Intrusion) — the most impressive demo
RESUME_RESULT=$(curl -sf -X POST http://localhost:8000/api/demo/start/4 2>/dev/null || echo "")
if [ -n "$RESUME_RESULT" ]; then
    echo -e "  ${GREEN}Scenario D (Full Intrusion) re-triggered.${NC}"
else
    echo -e "  ${YELLOW}Auto-resume failed. Manually pick a scenario at /demo${NC}"
fi

RECOVER_END=$(date +%s)
RECOVER_TIME=$((RECOVER_END - RECOVER_START))

echo ""
echo -e "${GREEN}┌─────────────────────────────────────────┐${NC}"
echo -e "${GREEN}│  RECOVERED in ${RECOVER_TIME}s — Go back to demo!     │${NC}"
echo -e "${GREEN}└─────────────────────────────────────────┘${NC}"
echo ""
echo -e "  ${BOLD}Dashboard${NC}: ${CYAN}http://localhost:5173/new-device/dashboard${NC}"
echo -e "  ${BOLD}Demo Page${NC}: ${CYAN}http://localhost:5173/demo${NC}"
echo ""
echo -e "  ${YELLOW}Stop:${NC} kill $API_PID $FE_PID"
echo ""
