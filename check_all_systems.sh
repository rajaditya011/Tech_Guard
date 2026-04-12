#!/usr/bin/env bash
# ============================================================
# HomeGuardian AI — System Diagnostic Script
# Run: bash check_all_systems.sh
# ============================================================



GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

pass() { echo -e "  ${GREEN}✅ $1${NC}"; ((PASS++)); }
fail() { echo -e "  ${RED}❌ $1${NC}"; ((FAIL++)); }
warn() { echo -e "  ${YELLOW}⚠️  $1${NC}"; ((WARN++)); }

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$PROJECT_ROOT/backend"
FRONTEND="$PROJECT_ROOT/frontend"
UI="$PROJECT_ROOT/ui"

echo ""
echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║    HomeGuardian AI — System Diagnostics      ║${NC}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════╝${NC}"
echo ""

# ───────────────────────────────────────────────
echo -e "${BOLD}[1/8] Environment${NC}"
# ───────────────────────────────────────────────
if [ -f "$PROJECT_ROOT/.env" ]; then
  pass ".env file exists"
  if grep -q "DEMO_MODE=true" "$PROJECT_ROOT/.env"; then
    pass "DEMO_MODE=true (safe for demo)"
  else
    warn "DEMO_MODE is not true — external APIs required"
  fi
else
  fail ".env file missing"
fi

if command -v python3 &>/dev/null || [ -f "$BACKEND/venv/bin/python" ]; then
  PYTHON="$BACKEND/venv/bin/python"
  if [ -f "$PYTHON" ]; then
    PYVER=$("$PYTHON" --version 2>&1)
    pass "Python: $PYVER (venv)"
  else
    PYVER=$(python3 --version 2>&1)
    pass "Python: $PYVER (system)"
  fi
else
  fail "Python not found"
fi

# Check Node.js
export PATH="/usr/local/bin:$PATH"
if command -v node &>/dev/null; then
  NODEVER=$(node --version 2>&1)
  pass "Node.js: $NODEVER"
else
  fail "Node.js not found in PATH"
fi

# ───────────────────────────────────────────────
echo -e "\n${BOLD}[2/8] Backend Dependencies${NC}"
# ───────────────────────────────────────────────
if [ -d "$BACKEND/venv" ]; then
  pass "Python venv exists"
  PYTHON="$BACKEND/venv/bin/python"
  
  for pkg in fastapi uvicorn paho.mqtt jose passlib anthropic; do
    if "$PYTHON" -c "import ${pkg//./_}" 2>/dev/null; then
      pass "Package: $pkg"
    else
      fail "Package missing: $pkg"
    fi
  done
else
  fail "Backend venv missing — run: cd backend && python3 -m venv venv && pip install -r requirements.txt"
fi

# ───────────────────────────────────────────────
echo -e "\n${BOLD}[3/8] Frontend Dependencies${NC}"
# ───────────────────────────────────────────────
if [ -d "$FRONTEND/node_modules" ]; then
  pass "Frontend node_modules exists"
else
  fail "Frontend node_modules missing — run: cd frontend && npm install"
fi

if [ -d "$UI/node_modules" ]; then
  pass "UI (landing page) node_modules exists"
else
  warn "UI node_modules missing — run: cd ui && npm install"
fi

# ───────────────────────────────────────────────
echo -e "\n${BOLD}[4/8] Backend Module Imports${NC}"
# ───────────────────────────────────────────────
PYTHON="$BACKEND/venv/bin/python"
IMPORT_TEST=$("$PYTHON" -c "
import sys
sys.path.insert(0, '$BACKEND')
errors = []
modules = [
  'config', 'database', 'models', 'auth', 'mqtt_client', 'websocket_manager',
  'services.sensor_pipeline', 'services.pipeline_setup',
  'services.baseline_service', 'services.yolo_service',
  'services.anomaly_service', 'services.fusion_service',
  'services.risk_service', 'services.clip_service',
  'services.narrative_service', 'services.alert_service',
  'services.communication_service', 'services.prediction_service',
  'routers.auth_routes', 'routers.sensor_routes', 'routers.demo_routes',
  'routers.stream_routes', 'routers.anomaly_routes', 'routers.clip_routes',
  'routers.narrative_routes', 'routers.communication_routes',
  'routers.prediction_routes', 'routers.dashboard_routes', 'routers.alert_routes',
]
for m in modules:
    try:
        __import__(m)
    except Exception as e:
        errors.append(f'{m}: {e}')
if errors:
    for e in errors: print(f'FAIL:{e}')
else:
    print(f'OK:{len(modules)}')
" 2>&1 | grep -v "Warning\|warn\|google\|urllib3")

if echo "$IMPORT_TEST" | grep -q "^OK:"; then
  COUNT=$(echo "$IMPORT_TEST" | grep "^OK:" | cut -d: -f2)
  pass "All $COUNT backend modules import successfully"
else
  echo "$IMPORT_TEST" | grep "^FAIL:" | while read -r line; do
    fail "${line#FAIL:}"
  done
fi

# ───────────────────────────────────────────────
echo -e "\n${BOLD}[5/8] Database Schema${NC}"
# ───────────────────────────────────────────────
DB_CHECK=$("$PYTHON" -c "
import sys
sys.path.insert(0, '$BACKEND')
from database import init_database, get_db
init_database()
with get_db() as conn:
    tables = [r[0] for r in conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()]
    required = ['users','sensor_nodes','baseline_profiles','anomaly_events','alerts','scenario_library','prediction_events']
    for t in required:
        if t in tables:
            print(f'OK:{t}')
        else:
            print(f'FAIL:{t}')
    
    # Verify schema fixes
    alerts_sql = conn.execute(\"SELECT sql FROM sqlite_master WHERE name='alerts'\").fetchone()[0]
    if 'email' in alerts_sql:
        print('OK:alerts_email_channel')
    else:
        print('FAIL:alerts_missing_email')
    
    sensors_sql = conn.execute(\"SELECT sql FROM sqlite_master WHERE name='sensor_nodes'\").fetchone()[0]
    if 'iot_sensor' in sensors_sql:
        print('OK:sensor_iot_type')
    else:
        print('FAIL:sensor_missing_iot')
" 2>&1 | grep -v "DB\]\|Warning\|warn\|google\|urllib3")

echo "$DB_CHECK" | while read -r line; do
  name="${line#*:}"
  if echo "$line" | grep -q "^OK:"; then
    pass "Table/Schema: $name"
  else
    fail "Table/Schema: $name"
  fi
done

# ───────────────────────────────────────────────
echo -e "\n${BOLD}[6/8] Frontend Build Check${NC}"
# ───────────────────────────────────────────────
if [ -d "$FRONTEND/dist" ]; then
  pass "Frontend dist/ exists (production build available)"
else
  warn "Frontend dist/ missing (not critical — dev server works)"
fi

if [ -f "$FRONTEND/src/App.jsx" ]; then
  pass "Frontend App.jsx exists"
else
  fail "Frontend App.jsx missing"
fi

# Check critical components exist
COMPONENTS=(
  "contexts/AuthContext.jsx" "contexts/ThemeContext.jsx" "contexts/I18nContext.jsx"
  "pages/NewDeviceLogin.jsx" "pages/NewDeviceDashboard.jsx" "pages/DemoPage.jsx"
  "pages/OldDeviceLogin.jsx" "pages/OldDevicePortal.jsx"
  "components/layout/AppShell.jsx" "components/layout/Sidebar.jsx" "components/layout/ThemeToggle.jsx"
  "components/dashboard/LiveFeedGrid.jsx" "components/dashboard/FloorPlan.jsx"
  "components/dashboard/AlertFeed.jsx" "components/dashboard/RiskGauge.jsx"
  "components/dashboard/SensorHealth.jsx" "components/dashboard/CommPanel.jsx"
  "components/dashboard/ReasoningReplay.jsx"
  "components/old-device/CameraPreview.jsx" "components/old-device/BaselineProgress.jsx"
  "components/old-device/AudioWarning.jsx" "components/old-device/DeviceStatus.jsx"
)

MISSING=0
for comp in "${COMPONENTS[@]}"; do
  if [ ! -f "$FRONTEND/src/$comp" ]; then
    fail "Missing component: $comp"
    ((MISSING++))
  fi
done
if [ "$MISSING" -eq 0 ]; then
  pass "All ${#COMPONENTS[@]} frontend components present"
fi

# ───────────────────────────────────────────────
echo -e "\n${BOLD}[7/8] Port Availability${NC}"
# ───────────────────────────────────────────────
for port in 8000 5173; do
  if lsof -ti:$port >/dev/null 2>&1; then
    warn "Port $port is in use (may need to kill existing process)"
  else
    pass "Port $port is free"
  fi
done

# ───────────────────────────────────────────────
echo -e "\n${BOLD}[8/8] API Endpoint Test${NC}"
# ───────────────────────────────────────────────
if curl -s --connect-timeout 2 http://localhost:8000/api/health >/dev/null 2>&1; then
  HEALTH=$(curl -s http://localhost:8000/api/health)
  pass "Backend API responding: $HEALTH"
else
  warn "Backend not running on port 8000 (start with: cd backend && source venv/bin/activate && uvicorn main:app --port 8000)"
fi

if curl -s --connect-timeout 2 http://localhost:5173 >/dev/null 2>&1; then
  pass "Frontend dev server responding on port 5173"
else
  warn "Frontend not running on port 5173 (start with: cd frontend && npm run dev)"
fi

# ───────────────────────────────────────────────
echo ""
echo -e "${CYAN}${BOLD}══════════════════════════════════════════════${NC}"
echo -e "${BOLD}  Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}, ${YELLOW}$WARN warnings${NC}"
echo -e "${CYAN}${BOLD}══════════════════════════════════════════════${NC}"

if [ "$FAIL" -gt 0 ]; then
  echo -e "\n${RED}${BOLD}  ⛔ $FAIL critical issue(s) found. Fix before launch.${NC}"
  exit 1
else
  echo -e "\n${GREEN}${BOLD}  🚀 System is READY FOR LAUNCH!${NC}"
  echo -e "  Start backend:  cd backend && source venv/bin/activate && uvicorn main:app --port 8000 --reload"
  echo -e "  Start frontend: cd frontend && npm run dev"
  echo ""
  exit 0
fi
