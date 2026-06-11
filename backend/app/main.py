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

__version__ = "0.10.0"

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
    # Startup
    print("Starting Economic Policy Simulator API...")
    yield
    # Shutdown
    service = get_wdi_service()
    await service.close()
    print("Shutdown complete")


app = FastAPI(
    title="Economic Policy Simulator API",
    description="""
    ## Overview

    This API powers an interactive tool for exploring the employment effects
    of economic policy choices in South Africa, Tunisia, Viet Nam, and Thailand.

    ## Features

    - **Policy Simulation**: Model tariff, subsidy, SME stimulus, and industrial policy effects
    - **Employment Multipliers**: Input-Output based direct, indirect, and induced job effects
    - **Demographic Disaggregation**: Results by gender, age (youth vs adult), and job quality
    - **Real Data**: Live World Bank WDI indicators
    - **AI Assistant**: Natural language policy interpretation

    ## Methodology

    The model uses Leontief Input-Output analysis to calculate employment effects:

    1. Policy changes translate to sector demand shocks
    2. Demand shocks propagate through inter-industry linkages
    3. Employment coefficients convert output changes to job effects
    4. Demographic shares disaggregate by gender, age, formality

    **Note**: This is a didactic tool designed for policy education.
    Results should be interpreted as illustrative, not precise forecasts.
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
