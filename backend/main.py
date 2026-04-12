"""
HomeGuardian AI — Main Application
FastAPI entry point with all middleware and route configuration.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import settings
from database import init_database
from mqtt_client import mqtt_manager
from websocket_manager import connection_manager
from auth import decode_token

# ---- Logging Setup ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("homeguardian")

# ---- Rate Limiter ----
limiter = Limiter(key_func=get_remote_address)


# ---- Lifespan ----
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    logger.info("Starting HomeGuardian AI...")
    logger.info(f"Demo Mode: {settings.DEMO_MODE}")

    errors = settings.validate()
    for error in errors:
        logger.warning(f"Config Warning: {error}")

    init_database()

    try:
        mqtt_manager.connect()
    except Exception as e:
        logger.error(f"MQTT connection failed: {e}")

    # Register sensor pipeline MQTT handlers
    from services.pipeline_setup import setup_sensor_pipeline
    setup_sensor_pipeline()

    logger.info("HomeGuardian AI started successfully.")
    yield

    logger.info("Shutting down HomeGuardian AI...")
    mqtt_manager.disconnect()
    logger.info("Shutdown complete.")


# ---- App Instance ----
app = FastAPI(
    title="HomeGuardian AI",
    description="Adaptive Intelligence Security System API",
    version="1.0.0",
    lifespan=lifespan
)

# ---- Middleware ----
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# ---- Import and Include Routers ----
from routers.auth_routes import router as auth_router
from routers.sensor_routes import router as sensor_router
from routers.demo_routes import router as demo_router
from routers.stream_routes import router as stream_router
from routers.anomaly_routes import router as anomaly_router
from routers.communication_routes import router as communication_router
from routers.clip_routes import router as clip_router
from routers.narrative_routes import router as narrative_router
from routers.prediction_routes import router as prediction_router
from routers.dashboard_routes import router as dashboard_router
from routers.alert_routes import router as alert_router

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(sensor_router, prefix="/api/sensors", tags=["Sensors"])
app.include_router(demo_router, prefix="/api/demo", tags=["Demo"])
app.include_router(stream_router, prefix="/api/stream", tags=["Streaming"])
app.include_router(anomaly_router, prefix="/api/anomalies", tags=["Anomalies"])
app.include_router(communication_router, prefix="/api/communicate", tags=["Communication"])
app.include_router(clip_router, prefix="/api/clips", tags=["Clips"])
app.include_router(narrative_router, prefix="/api/narratives", tags=["Narratives"])
app.include_router(prediction_router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(alert_router, prefix="/api/alerts", tags=["Alerts"])



# ---- Health Check ----
@app.get("/api/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "demo_mode": settings.DEMO_MODE,
        "services": {
            "database": "connected",
            "mqtt": "connected" if mqtt_manager.connected else "disconnected",
            "websocket_old_devices": connection_manager.active_old_devices,
            "websocket_dashboards": connection_manager.active_dashboards
        }
    }


# ---- WebSocket Endpoints ----
@app.websocket("/ws/old-device/{device_id}")
async def websocket_old_device(websocket: WebSocket, device_id: str):
    """WebSocket endpoint for old device communication."""
    await connection_manager.connect_old_device(device_id, websocket)
    try:
        while True:
            text_data = await websocket.receive_text()
            import json
            try:
                data = json.loads(text_data)
            except json.JSONDecodeError:
                data = {}
            msg_type = data.get("type", "")
            if msg_type:
                logger.debug(f"Received from old device {device_id}: {msg_type}")
    except WebSocketDisconnect:
        connection_manager.disconnect_old_device(device_id)
    except Exception as e:
        logger.error(f"WebSocket error for {device_id}: {e}")
        connection_manager.disconnect_old_device(device_id)


@app.websocket("/ws/dashboard/{user_id}")
async def websocket_dashboard(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for dashboard real-time updates."""
    await connection_manager.connect_dashboard(user_id, websocket)
    try:
        while True:
            text_data = await websocket.receive_text()
            import json
            try:
                data = json.loads(text_data)
            except json.JSONDecodeError:
                data = {}
            msg_type = data.get("type", "")
            if msg_type == "send_message":
                target_device = data.get("target_device_id")
                if target_device:
                    await connection_manager.send_to_old_device(target_device, {
                        "type": "incoming_message",
                        "from": user_id,
                        "content": data.get("content", "")
                    })
            if msg_type:
                logger.debug(f"Received from dashboard {user_id}: {msg_type}")
    except WebSocketDisconnect:
        connection_manager.disconnect_dashboard(user_id)
    except Exception as e:
        logger.error(f"WebSocket error for dashboard {user_id}: {e}")
        connection_manager.disconnect_dashboard(user_id)


# ---- Error Handlers ----
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "An internal error occurred. Please try again later."})
