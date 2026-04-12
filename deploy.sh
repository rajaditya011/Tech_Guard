#!/bin/bash
# ============================================================
# HomeGuardian AI — Production Deployment Script
# Usage:
#   bash deploy.sh local        — docker-compose up (all services)
#   bash deploy.sh build        — build Docker images only
#   bash deploy.sh cloud        — deploy to Google Cloud Run
#   bash deploy.sh backend      — run FastAPI dev server only
#   bash deploy.sh frontend     — run Vite dev server only
#   bash deploy.sh mqtt         — start Mosquitto locally
# ============================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
MODE=${1:-local}
GCP_PROJECT=${GCP_PROJECT:-"homeguardian-ai"}
GCP_REGION=${GCP_REGION:-"us-central1"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

banner() {
    echo ""
    echo -e "${CYAN}=========================================${NC}"
    echo -e "${CYAN}  HomeGuardian AI — $1${NC}"
    echo -e "${CYAN}=========================================${NC}"
    echo ""
}

step() {
    echo -e "${GREEN}[$1]${NC} $2"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    exit 1
}

# ============================================================
# Command: build — Build All Docker Images
# ============================================================
cmd_build() {
    banner "Building Docker Images"

    step "1/3" "Building backend image..."
    docker build -t homeguardian-api:latest "$PROJECT_ROOT/backend"

    step "2/3" "Building frontend image..."
    docker build -t homeguardian-frontend:latest "$PROJECT_ROOT/frontend"

    step "3/3" "Verifying images..."
    docker images | grep homeguardian

    echo ""
    echo -e "${GREEN}All Docker images built successfully.${NC}"
}

# ============================================================
# Command: local — Start All Services with docker-compose
# ============================================================
cmd_local() {
    banner "Starting Local Environment"

    step "1/5" "Building Docker images..."
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" build

    step "2/5" "Starting all services..."
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" up -d

    step "3/5" "Waiting for services to initialize..."
    sleep 6

    step "4/5" "Running health check..."
    bash "$PROJECT_ROOT/health_check.sh" || true

    step "5/5" "Service endpoints:"
    echo ""
    echo -e "  ${CYAN}Frontend${NC}:   http://localhost:5173"
    echo -e "  ${CYAN}API${NC}:        http://localhost:8000"
    echo -e "  ${CYAN}API Docs${NC}:   http://localhost:8000/docs"
    echo -e "  ${CYAN}MQTT${NC}:       localhost:1883"
    echo -e "  ${CYAN}Nginx${NC}:      http://localhost:80"
    echo ""
    echo -e "${GREEN}All services running.${NC} Use 'docker-compose logs -f' to tail logs."
}

# ============================================================
# Command: cloud — Deploy to Google Cloud Run
# ============================================================
cmd_cloud() {
    banner "Deploying to Google Cloud Run"

    # Pre-flight checks
    if ! command -v gcloud &> /dev/null; then
        fail "gcloud CLI not found. Install: https://cloud.google.com/sdk/docs/install"
    fi

    step "1/7" "Authenticating with Google Cloud..."
    gcloud auth configure-docker "${GCP_REGION}-docker.pkg.dev" --quiet 2>/dev/null || true

    REGISTRY="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/homeguardian"

    step "2/7" "Creating Artifact Registry repository (if needed)..."
    gcloud artifacts repositories create homeguardian \
        --repository-format=docker \
        --location="${GCP_REGION}" \
        --project="${GCP_PROJECT}" 2>/dev/null || true

    step "3/7" "Building backend image for Cloud Run..."
    docker build --platform linux/amd64 \
        -t "${REGISTRY}/api:latest" \
        "$PROJECT_ROOT/backend"

    step "4/7" "Building frontend image for Cloud Run..."
    docker build --platform linux/amd64 \
        -t "${REGISTRY}/frontend:latest" \
        "$PROJECT_ROOT/frontend"

    step "5/7" "Pushing images to Artifact Registry..."
    docker push "${REGISTRY}/api:latest"
    docker push "${REGISTRY}/frontend:latest"

    step "6/7" "Deploying backend to Cloud Run..."
    gcloud run deploy homeguardian-api \
        --image="${REGISTRY}/api:latest" \
        --region="${GCP_REGION}" \
        --project="${GCP_PROJECT}" \
        --platform=managed \
        --port=8000 \
        --memory=1Gi \
        --cpu=1 \
        --min-instances=0 \
        --max-instances=3 \
        --allow-unauthenticated \
        --set-env-vars="DEMO_MODE=true" \
        --quiet

    step "7/7" "Deploying frontend to Cloud Run..."
    gcloud run deploy homeguardian-frontend \
        --image="${REGISTRY}/frontend:latest" \
        --region="${GCP_REGION}" \
        --project="${GCP_PROJECT}" \
        --platform=managed \
        --port=80 \
        --memory=256Mi \
        --cpu=1 \
        --min-instances=0 \
        --max-instances=3 \
        --allow-unauthenticated \
        --quiet

    echo ""
    step "DONE" "Retrieving service URLs..."
    API_URL=$(gcloud run services describe homeguardian-api \
        --region="${GCP_REGION}" --project="${GCP_PROJECT}" \
        --format='value(status.url)' 2>/dev/null)
    FE_URL=$(gcloud run services describe homeguardian-frontend \
        --region="${GCP_REGION}" --project="${GCP_PROJECT}" \
        --format='value(status.url)' 2>/dev/null)

    echo ""
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}  Cloud Run Deployment Complete!${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo -e "  ${CYAN}API${NC}:       ${API_URL:-"(retrieving...)"}"
    echo -e "  ${CYAN}Frontend${NC}:  ${FE_URL:-"(retrieving...)"}"
    echo ""
    echo -e "  ${YELLOW}NOTE${NC}: Set VITE_API_URL=${API_URL} in frontend build for cross-origin API calls."
    echo ""
}

# ============================================================
# Command: backend — Run FastAPI Dev Server Only
# ============================================================
cmd_backend() {
    banner "FastAPI Dev Server"

    if [ ! -d "$PROJECT_ROOT/backend/venv" ]; then
        warn "No virtualenv found. Creating one..."
        python3 -m venv "$PROJECT_ROOT/backend/venv"
        source "$PROJECT_ROOT/backend/venv/bin/activate"
        pip install -r "$PROJECT_ROOT/backend/requirements.txt"
    else
        source "$PROJECT_ROOT/backend/venv/bin/activate"
    fi

    step "RUN" "Starting uvicorn on http://localhost:8000 ..."
    cd "$PROJECT_ROOT/backend"
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
}

# ============================================================
# Command: frontend — Run Vite Dev Server Only
# ============================================================
cmd_frontend() {
    banner "Vite Dev Server"

    if [ ! -d "$PROJECT_ROOT/frontend/node_modules" ]; then
        warn "node_modules not found. Installing dependencies..."
        cd "$PROJECT_ROOT/frontend"
        npm install
    fi

    step "RUN" "Starting Vite on http://localhost:5173 ..."
    cd "$PROJECT_ROOT/frontend"
    npm run dev -- --host 0.0.0.0
}

# ============================================================
# Command: mqtt — Start Eclipse Mosquitto Locally
# ============================================================
cmd_mqtt() {
    banner "Eclipse Mosquitto MQTT Broker"

    # Try Docker first, fall back to local install
    if command -v docker &> /dev/null; then
        step "RUN" "Starting Mosquitto via Docker on port 1883..."
        docker run -d --rm \
            --name homeguardian-mqtt \
            -p 1883:1883 \
            -p 9001:9001 \
            -v "$PROJECT_ROOT/mosquitto/config:/mosquitto/config" \
            -v "$PROJECT_ROOT/mosquitto/data:/mosquitto/data" \
            -v "$PROJECT_ROOT/mosquitto/log:/mosquitto/log" \
            eclipse-mosquitto:2

        echo ""
        echo -e "  ${CYAN}MQTT Broker${NC}:  localhost:1883"
        echo -e "  ${CYAN}WebSocket${NC}:    localhost:9001"
        echo -e "  ${CYAN}Container${NC}:    homeguardian-mqtt"
        echo ""
        echo -e "  Stop with: ${YELLOW}docker stop homeguardian-mqtt${NC}"
    elif command -v mosquitto &> /dev/null; then
        step "RUN" "Starting local Mosquitto on port 1883..."
        mosquitto -c "$PROJECT_ROOT/mosquitto/config/mosquitto.conf" -v
    else
        fail "Neither Docker nor Mosquitto found. Install one:\n  brew install mosquitto\n  OR\n  brew install --cask docker"
    fi
}

# ============================================================
# Command: stop — Stop All Services
# ============================================================
cmd_stop() {
    banner "Stopping All Services"

    step "1/2" "Stopping docker-compose services..."
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" down 2>/dev/null || true

    step "2/2" "Stopping standalone MQTT container..."
    docker stop homeguardian-mqtt 2>/dev/null || true

    echo -e "${GREEN}All services stopped.${NC}"
}

# ============================================================
# Router
# ============================================================
case "$MODE" in
    build)    cmd_build ;;
    local)    cmd_local ;;
    cloud)    cmd_cloud ;;
    backend)  cmd_backend ;;
    frontend) cmd_frontend ;;
    mqtt)     cmd_mqtt ;;
    stop)     cmd_stop ;;
    *)
        echo "Usage: bash deploy.sh <command>"
        echo ""
        echo "Commands:"
        echo "  build       Build all Docker images for production"
        echo "  local       Start all services locally with docker-compose"
        echo "  cloud       Deploy to Google Cloud Run"
        echo "  backend     Run FastAPI dev server only"
        echo "  frontend    Run Vite dev server only"
        echo "  mqtt        Start Eclipse Mosquitto locally"
        echo "  stop        Stop all running services"
        echo ""
        echo "Environment Variables:"
        echo "  GCP_PROJECT  Google Cloud project ID (default: homeguardian-ai)"
        echo "  GCP_REGION   Google Cloud region (default: us-central1)"
        exit 1
        ;;
esac
