from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.observability import setup_observability
from app.core.database import engine, Base
from app.api.router import router

# Create DB tables (In production, use Alembic migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="Natural-language tabular analytics service"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Observability
log = setup_observability(app, engine)

# Include Router
app.include_router(router)

@app.on_event("startup")
def startup_event():
    log.info("Application starting up...", version=settings.version, domain=settings.domain)
    # Trigger initial data ingestion here if needed, or rely on a script/cron
    # For this exercise, we could trigger it automatically if tables are empty.
    from app.core.database import SessionLocal
    from app.services.ingestion_service import ingest_domain_data
    from app.models.domain import NormalizedRecord
    db = SessionLocal()
    try:
        count = db.query(NormalizedRecord).count()
        if count == 0:
            log.info("No data found, starting initial ingestion...")
            ingest_domain_data(db)
    finally:
        db.close()

@app.on_event("shutdown")
def shutdown_event():
    log.info("Application shutting down...")
