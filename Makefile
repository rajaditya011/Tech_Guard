# ============================================================
# HomeGuardian AI — Makefile
# Quick aliases for all deployment and development commands.
#
# Usage:
#   make dev          — Start backend + frontend in parallel
#   make backend      — FastAPI only
#   make frontend     — Vite only
#   make mqtt         — Mosquitto only
#   make build        — Build all Docker images
#   make up           — docker-compose up -d
#   make down         — docker-compose down
#   make deploy       — Deploy to Google Cloud Run
#   make diagnostics  — Run system diagnostics
#   make health       — Run health check
#   make clean        — Remove containers, images, and build artifacts
# ============================================================

.PHONY: dev backend frontend mqtt build up down deploy diagnostics health clean stop logs

# ---- Development ----

dev:
	@echo "Starting backend + frontend in parallel..."
	@bash deploy.sh backend &
	@sleep 2
	@bash deploy.sh frontend

backend:
	@bash deploy.sh backend

frontend:
	@bash deploy.sh frontend

mqtt:
	@bash deploy.sh mqtt

# ---- Docker ----

build:
	@bash deploy.sh build

up:
	@bash deploy.sh local

down:
	@bash deploy.sh stop

stop:
	@bash deploy.sh stop

logs:
	@docker-compose logs -f

# ---- Cloud ----

deploy:
	@bash deploy.sh cloud

# ---- Diagnostics ----

diagnostics:
	@cd backend && python3 ../diagnostics.py

health:
	@bash health_check.sh

# ---- Cleanup ----

clean:
	@echo "Stopping all services..."
	@docker-compose down --rmi local -v 2>/dev/null || true
	@docker stop homeguardian-mqtt 2>/dev/null || true
	@echo "Removing build artifacts..."
	@rm -rf frontend/dist
	@echo "Done."

# ---- Emergency ----

reset:
	@bash scripts/emergency_reset.sh

demo-30:
	@bash scripts/emergency_demo_critical.sh

demo-10:
	@bash scripts/emergency_synthetic_only.sh

recover:
	@bash scripts/emergency_recover.sh
