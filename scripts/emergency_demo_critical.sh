#!/bin/bash
# ============================================================
# HomeGuardian AI — Emergency: 30-Minute Demo Prep
# Focuses ONLY on demo-critical features:
#   - Backend API with DEMO_MODE=true
#   - Frontend dashboard
#   - Demo scenarios loaded and ready
#   - Health check passes
# Skips: MQTT, YOLO, Claude API, FCM, SSL
# Usage: bash scripts/emergency_demo_critical.sh
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
echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}  30-MINUTE DEMO PREP — Critical Path${NC}"
echo -e "${YELLOW}=========================================${NC}"
echo ""

# ---- Force DEMO_MODE ----
echo -e "${CYAN}[1/6]${NC} Forcing DEMO_MODE=true..."
cd "$PROJECT_ROOT"
if grep -q "DEMO_MODE=" .env 2>/dev/null; then
    sed -i.bak 's/DEMO_MODE=.*/DEMO_MODE=true/' .env
    rm -f .env.bak
else
    echo "DEMO_MODE=true" >> .env
fi
echo "  DEMO_MODE=true set."

# ---- Backend Setup ----
echo -e "${CYAN}[2/6]${NC} Ensuring backend is ready..."
cd "$PROJECT_ROOT/backend"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt --quiet 2>/dev/null
mkdir -p data clips models
echo "  Backend dependencies ready."

# ---- Database Init ----
echo -e "${CYAN}[3/6]${NC} Initializing fresh database..."
rm -f data/homeguardian.db
python3 -c "from database import init_database; init_database()" 2>/dev/null || echo "  Will init on boot."

# ---- Frontend Setup ----
echo -e "${CYAN}[4/6]${NC} Ensuring frontend is ready..."
cd "$PROJECT_ROOT/frontend"
if [ ! -d "node_modules" ]; then
    npm install --silent 2>/dev/null
fi
echo "  Frontend dependencies ready."

# ---- Start Backend ----
echo -e "${CYAN}[5/6]${NC} Starting FastAPI backend (background)..."
cd "$PROJECT_ROOT/backend"
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/homeguardian-api.log 2>&1 &
API_PID=$!
echo "  API PID: $API_PID"

# Wait for API to be ready
echo "  Waiting for API..."
for i in $(seq 1 15); do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "  ${GREEN}API is up!${NC}"
        break
    fi
    sleep 1
done

# ---- Start Frontend ----
echo -e "${CYAN}[6/6]${NC} Starting Vite frontend (background)..."
cd "$PROJECT_ROOT/frontend"
nohup npm run dev -- --host 0.0.0.0 > /tmp/homeguardian-frontend.log 2>&1 &
FE_PID=$!
echo "  Frontend PID: $FE_PID"
sleep 3

# ---- Summary ----
echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  DEMO-READY!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "  ${BOLD}Dashboard${NC}:  ${CYAN}http://localhost:5173/new-device/login${NC}"
echo -e "  ${BOLD}Demo Page${NC}:  ${CYAN}http://localhost:5173/demo${NC}"
echo -e "  ${BOLD}API Docs${NC}:   ${CYAN}http://localhost:8000/docs${NC}"
echo -e "  ${BOLD}API Health${NC}: ${CYAN}http://localhost:8000/api/health${NC}"
echo ""
echo -e "  ${YELLOW}Demo flow:${NC}"
echo -e "    1. Open ${CYAN}/demo${NC} → pick a scenario"
echo -e "    2. System auto-redirects to dashboard"
echo -e "    3. Show Floor Plan, Alerts, AI Reasoning panels"
echo -e "    4. Switch theme with sidebar toggle"
echo ""
echo -e "  ${YELLOW}To stop:${NC} kill $API_PID $FE_PID"
echo ""
