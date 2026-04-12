#!/bin/bash
# ============================================================
# HomeGuardian AI — Emergency: Full Project Reset
# Wipes all generated data and rebuilds from Chunk 00.
# Usage: bash scripts/emergency_reset.sh
# ============================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${RED}=========================================${NC}"
echo -e "${RED}  EMERGENCY: Full Project Reset${NC}"
echo -e "${RED}=========================================${NC}"
echo ""

# ---- Step 1: Stop everything ----
echo -e "${YELLOW}[1/7]${NC} Stopping all running services..."
cd "$PROJECT_ROOT"
docker-compose down 2>/dev/null || true
docker stop homeguardian-mqtt 2>/dev/null || true
pkill -f "uvicorn main:app" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

# ---- Step 2: Wipe generated data ----
echo -e "${YELLOW}[2/7]${NC} Wiping generated data..."
rm -rf "$PROJECT_ROOT/backend/data/"*.db
rm -rf "$PROJECT_ROOT/backend/clips/"*
rm -rf "$PROJECT_ROOT/frontend/dist"
rm -rf "$PROJECT_ROOT/mosquitto/data/"*
rm -rf "$PROJECT_ROOT/mosquitto/log/"*
echo "  Cleared database, clips, build artifacts, and MQTT data."

# ---- Step 3: Verify .env exists ----
echo -e "${YELLOW}[3/7]${NC} Verifying environment configuration..."
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${RED}  .env file missing! Creating default...${NC}"
    cat > "$PROJECT_ROOT/.env" << 'ENVEOF'
DEMO_MODE=true
CLAUDE_API_KEY=
FCM_SERVER_KEY=
MQTT_BROKER_URL=localhost
MQTT_PORT=1883
DB_PATH=data/homeguardian.db
YOLO_MODEL_PATH=models/yolov8n.pt
BASELINE_DAYS=14
ANOMALY_THRESHOLD=0.65
CLIP_PRE_SECONDS=5
CLIP_POST_SECONDS=10
JWT_SECRET=homeguardian-dev-secret-change-in-production
JWT_ACCESS_EXPIRY_MINUTES=15
JWT_REFRESH_EXPIRY_DAYS=7
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
BACKEND_PORT=8000
FRONTEND_PORT=5173
ENVEOF
    echo "  Default .env created with DEMO_MODE=true."
else
    echo "  .env found."
fi

# ---- Step 4: Backend dependencies ----
echo -e "${YELLOW}[4/7]${NC} Setting up backend virtual environment..."
cd "$PROJECT_ROOT/backend"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt --quiet 2>/dev/null
echo "  Backend dependencies installed."

# ---- Step 5: Frontend dependencies ----
echo -e "${YELLOW}[5/7]${NC} Installing frontend dependencies..."
cd "$PROJECT_ROOT/frontend"
npm install --silent 2>/dev/null
echo "  Frontend dependencies installed."

# ---- Step 6: Ensure data directories exist ----
echo -e "${YELLOW}[6/7]${NC} Ensuring data directories..."
mkdir -p "$PROJECT_ROOT/backend/data"
mkdir -p "$PROJECT_ROOT/backend/clips"
mkdir -p "$PROJECT_ROOT/backend/models"
mkdir -p "$PROJECT_ROOT/mosquitto/config"
mkdir -p "$PROJECT_ROOT/mosquitto/data"
mkdir -p "$PROJECT_ROOT/mosquitto/log"

# ---- Step 7: Initialize database ----
echo -e "${YELLOW}[7/7]${NC} Initializing fresh database..."
cd "$PROJECT_ROOT/backend"
python3 -c "from database import init_database; init_database()" 2>/dev/null || echo "  Database init will happen on first boot."

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Reset Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "  Next steps:"
echo -e "  ${CYAN}1.${NC} bash deploy.sh backend    # Start API"
echo -e "  ${CYAN}2.${NC} bash deploy.sh frontend   # Start UI"
echo -e "  ${CYAN}3.${NC} Visit http://localhost:5173"
echo ""
