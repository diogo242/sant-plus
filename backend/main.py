import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from backend.app.core.config import settings
from backend.app.database import init_db, check_db_connection
from backend.app.core.logging import configure_logging
import logging

logger = logging.getLogger("santeplus")
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Démarrage de %s", settings.APP_NAME)
    ok = await check_db_connection()
    if ok:
        logger.info("Connexion PostgreSQL établie ✔")
    else:
        logger.warning("PostgreSQL indisponible — mode dégradé")
    yield
    logger.info("Arrêt de %s", settings.APP_NAME)


app = FastAPI(
    title="Santé+ API",
    description="API professionnelle — Module orientation, dossier médical, paiement",
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

limiter = Limiter(key_func=lambda r: r.client.host)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.APP_NAME}


@app.get("/health/db")
async def db_health():
    ok = await check_db_connection()
    return {"status": "ok" if ok else "unavailable", "database": settings.POSTGRES_DB}


# Routes
from backend.app.routes import auth, hospitals, doctors, appointments, medical_records, invoices, blockchain, access_requests, search
app.include_router(auth.router)
app.include_router(hospitals.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(medical_records.router)
app.include_router(invoices.router)
app.include_router(blockchain.router)
app.include_router(access_requests.router)
app.include_router(search.router)

