#!/bin/bash
# HomeGuardian AI — Quick health check for all services

echo "========================================="
echo "  HomeGuardian AI — Health Check"
echo "========================================="

# API
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health 2>/dev/null)
if [ "$API_STATUS" = "200" ]; then
    echo "[PASS] API:      http://localhost:8000 (HTTP $API_STATUS)"
else
    echo "[FAIL] API:      http://localhost:8000 (HTTP $API_STATUS)"
fi

# Frontend
FE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173 2>/dev/null)
if [ "$FE_STATUS" = "200" ]; then
    echo "[PASS] Frontend: http://localhost:5173 (HTTP $FE_STATUS)"
else
    echo "[FAIL] Frontend: http://localhost:5173 (HTTP $FE_STATUS)"
fi

# MQTT
if nc -z localhost 1883 2>/dev/null; then
    echo "[PASS] MQTT:     localhost:1883 (UP)"
else
    echo "[WARN] MQTT:     localhost:1883 (DOWN — expected in DEMO_MODE)"
fi

# API Health Details
echo ""
echo "--- API Health Response ---"
curl -s http://localhost:8000/api/health 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "(API not reachable)"

echo ""
echo "========================================="
echo "  Health check complete."
echo "========================================="
