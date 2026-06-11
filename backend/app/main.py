"""
Economic Policy Simulator - FastAPI Backend
============================================
A didactic tool for policymakers to explore employment effects
of economic policy choices.

Data Sources:
- World Bank WDI API (real-time economic indicators)
- OECD ICIO Input-Output tables (employment multipliers)

Models:
- Leontief Input-Output analysis for multiplier effects
- Employment elasticities by sector
- Demographic employment shares (gender, age)
"""

import os
import secrets
from pathlib import Path

__version__ = "1.0.0"

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
from .api import router
from .services import get_wdi_service


# --------------- HTTP Basic Auth Middleware ---------------

AUTH_USERNAME = os.getenv("AUTH_USERNAME", "")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "")


class BasicAuthMiddleware(BaseHTTPMiddleware):
    """Require HTTP Basic Auth on all routes when credentials are configured."""

    async def dispatch(self, request: Request, call_next):
        # Skip auth if no credentials configured (local development)
        if not AUTH_USERNAME or not AUTH_PASSWORD:
            return await call_next(request)

        # Allow health check without auth (for Render health checks)
        if request.url.path == "/health":
            return await call_next(request)

        auth = request.headers.get("Authorization")
        if auth and auth.startswith("Basic "):
            import base64
            try:
                decoded = base64.b64decode(auth[6:]).decode("utf-8")
                username, password = decoded.split(":", 1)
                if (secrets.compare_digest(username, AUTH_USERNAME)
                        and secrets.compare_digest(password, AUTH_PASSWORD)):
                    return await call_next(request)
            except Exception:
                pass

        return Response(
            content="Unauthorized",
            status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="Policy Simulator"'},
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup: load all verified country data and engine parameters once,
    # so data problems surface at boot and the first request is fast.
    # Runtime work per simulation is matrix-vector products only.
    from .models import engine
    countries = engine.available_countries()
    for iso3 in countries:
        engine.load_country(iso3)
    engine.load_params("central")
    print(f"Economic Policy Simulator API: loaded {countries}")
    yield
    # Shutdown
    service = get_wdi_service()
    await service.close()
    print("Shutdown complete")


app = FastAPI(
    title="Economic Policy Simulator API",
    description="""
    ## Overview

    Didactic simulator of the employment effects of policy choices in
    South Africa, Tunisia, Viet Nam, Thailand and Senegal. NOT a
    forecasting or decision-support tool.

    ## Model

    Demand-driven Leontief input-output model computed from the OECD ICIO
    2025 edition (reference year 2022), with employment from OECD Trade in
    Employment (TiM) 2025 and ILOSTAT. Tariffs are decomposed into four
    transmission channels; sector support carries a financing-drag toggle;
    induced (Type II) effects are an optional, upper-bound-labelled toggle.
    Every behavioural parameter carries a citation in the assumptions
    registry and results are reported with parameter ranges.

    Under default parameters a unilateral tariff increase is never net
    employment-positive (automated acceptance test, per Flaaen & Pierce
    2019 and Amiti, Redding & Weinstein 2019).
    """,
    version=__version__,
    lifespan=lifespan
)

# Basic Auth middleware (must be added before CORS)
app.add_middleware(BasicAuthMiddleware)

# CORS middleware for frontend
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": __version__}


# --------------- Serve Frontend Static Files ---------------

# Check multiple possible locations for the built frontend
_candidates = [
    Path(__file__).resolve().parent.parent.parent / "frontend" / "dist",  # Local dev
    Path("/app/frontend/dist"),  # Docker container
]
FRONTEND_DIST = next((p for p in _candidates if p.is_dir()), None)

if FRONTEND_DIST is not None:
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="static-assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the React SPA - return index.html for all non-API routes."""
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
else:
    @app.get("/")
    async def root():
        """API root - no frontend build found"""
        return {
            "name": "Economic Policy Simulator API",
            "version": __version__,
            "status": "running",
            "docs": "/docs",
            "note": "Frontend not built. Run 'npm run build' in frontend/ directory.",
        }
