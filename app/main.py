# /opt/iot-backend/app/main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.config import settings
from app.logger import get_logger
from app.routers import auth, farms, sheds, devices, telemetry

logger = get_logger()

app = FastAPI(
    title=settings.APP_NAME,  # viene del .env
    description="Backend para gestión IoT de granjas (temperatura, humedad, gases, etc.)",
    version=settings.VERSION,  # viene del .env
    contact={
        "name": "CerdIoT Dev Team",
        "email": "soporte@cerdiot.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# ========== CORS ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # cámbialo cuando tengas frontend fijo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== MIDDLEWARES ==========

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Mide el tiempo que tarda cada petición y lo mete en la cabecera.
    Útil para ver si algo se está volviendo lento.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.3f}s"
    return response


# ========== EVENTOS DE ARRANQUE/APAGADO ==========

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 CerdIoT API iniciada correctamente")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 CerdIoT API detenida")


# ========== HANDLERS DE ERRORES BONITOS ==========

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(
        f"HTTP {exc.status_code} on {request.method} {request.url.path}: {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "code": exc.status_code,
            "message": exc.detail,
            "path": request.url.path,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(
        f"Unhandled error on {request.method} {request.url.path}: {exc}"
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "code": 500,
            "message": "Internal server error",
            "path": request.url.path,
        },
    )


# ========== ENDPOINTS DE SISTEMA ==========

@app.get("/", tags=["system"])
def root():
    """
    Endpoint raíz de la API — útil para tests rápidos o uptime checks.
    """
    return {
        "status": "ok",
        "message": "CerdIoT API running",
        "routers": ["/auth", "/farms", "/sheds", "/devices", "/telemetry"],
        "version": settings.VERSION,
    }


@app.get("/healthz", tags=["system"])
def healthz():
    return {"status": "ok"}


@app.get("/version", tags=["system"])
def version():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "env": settings.ENVIRONMENT,
    }


# ========== ROUTERS ==========
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(farms.router, prefix="/farms", tags=["farms"])
app.include_router(sheds.router, prefix="/sheds", tags=["sheds"])
app.include_router(devices.router, prefix="/devices", tags=["devices"])
app.include_router(telemetry.router, prefix="/telemetry", tags=["telemetry"])
