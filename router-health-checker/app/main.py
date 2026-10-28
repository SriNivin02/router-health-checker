"""FastAPI main application entry point."""
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.session import init_db
from app.security.headers import SecurityHeadersMiddleware
from app.security.firewall import FirewallMiddleware
from app.security.csrf import CSRFMiddleware

# Import API Routers
from app.api.auth_routes import router as auth_router
from app.api.scan_routes import router as scan_router
from app.api.stability_routes import router as stability_router
from app.speed.routes import router as speed_router
from app.api.agent_routes import router as agent_router
from app.api.settings_routes import router as settings_router

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs" if settings.APP_ENV == "development" else None,
    redoc_url=None
)

# 1. Custom Security Middlewares (order matters: Headers -> CSRF -> Firewall)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(FirewallMiddleware)

# 2. CORS locked to same-origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 3. Mount API Routers
app.include_router(auth_router)
app.include_router(scan_router)
app.include_router(stability_router)
app.include_router(speed_router)
app.include_router(agent_router)
app.include_router(settings_router)

# 4. Static Files and SPA Fallback
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
async def serve_index():
    return FileResponse(str(STATIC_DIR / "index.html"))

@app.get("/manifest.json")
async def serve_manifest():
    return FileResponse(str(STATIC_DIR / "manifest.json"))

@app.get("/sw.js")
async def serve_sw():
    return FileResponse(str(STATIC_DIR / "sw.js"), media_type="application/javascript")

# Global Safe Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred. Diagnostics logged."}
    )
