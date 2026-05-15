import time
import uuid
import hashlib
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from app.core.database import get_db
from app.core.security import get_api_key
from app.core.observability import QUERY_COUNT, QUERY_LATENCY
from app.models.schemas import QueryRequest, QueryResponse
from app.services.llm_service import get_llm_provider
from app.services.analytics_engine import AnalyticsEngine
from app.services.cache_service import cache_service
from app.services.ingestion_service import ingest_domain_data
import structlog
from opentelemetry import trace

log = structlog.get_logger("app.api")
router = APIRouter()
tracer = trace.get_tracer(__name__)

# Fake dataset version for this test. In reality, this would be updated on new ingestion.
CURRENT_DATASET_VERSION = 1

@router.get("/health")
def health(db: Session = Depends(get_db)):
    health_status = {
        "status": "ok",
        "db": "unknown",
        "redis": "unknown",
        "dataset_version": CURRENT_DATASET_VERSION,
    }
    #This prevents the entire endpoint from hanging/failing because one dependency is unavailable during tests. -siddharth
    try:
        db.execute(text("SELECT 1"))
        health_status["db"] = "healthy"
    except Exception as e:
        log.error("DB health check failed", error=str(e))
        health_status["status"] = "degraded"

    try:
        cache_service.redis.ping()
        health_status["redis"] = "healthy"
    except Exception as e:
        log.error("Redis health check failed", error=str(e))
        health_status["status"] = "degraded"

    return health_status

@router.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@router.get("/version")
def version():
    from app.core.config import settings
    return {"version": settings.version}

@router.post("/ingest")
def trigger_ingestion(background_tasks: BackgroundTasks, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    """Trigger data ingestion and cache invalidation manually."""
    background_tasks.add_task(run_ingestion_and_invalidate, db)
    return {"status": "Ingestion started"}

def run_ingestion_and_invalidate(db: Session):
    global CURRENT_DATASET_VERSION
    ingest_domain_data(db)
    CURRENT_DATASET_VERSION += 1
    cache_service.invalidate_all(db)

@router.post("/query", response_model=QueryResponse)
def query(req: QueryRequest, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    with tracer.start_as_current_span("process_query") as span:
        t0 = time.time()
        query_id = str(uuid.uuid4())
        span.set_attribute("query.id", query_id)
        
        try:
            # 1. Generate Cache Key based on question
            key_hash = hashlib.md5(req.question.encode()).hexdigest()
            cache_key = f"query:{key_hash}"
            
            # 2. Check Cache
            try:
                cached_resp = cache_service.get(
                    cache_key,
                    CURRENT_DATASET_VERSION,
                    db
                )
            except Exception as e:
                log.warning(
                    "Cache unavailable, continuing without cache",
                    error=str(e)
                )
                cached_resp = None
            if cached_resp:
                cached_resp["cache_hit"] = True
                cached_resp["query_id"] = query_id
                cached_resp["trace_id"] = hex(span.get_span_context().trace_id)
                QUERY_COUNT.labels(status="success_cached").inc()
                return cached_resp

            # 3. LLM Planning
            llm = get_llm_provider()
            plan = llm.plan_query(req.question)
            span.set_attribute("query.plan.action", plan.get("action", "unknown"))
            
            # 4. Analytics Execution
            engine = AnalyticsEngine(db)
            value, citations, disagreements = engine.execute_plan(plan)
            
            # 5. Format Response
            if plan.get("action") == "unsupported":
                answer = "I'm sorry, I don't know how to answer that."
            elif value is not None:
                answer = f"The calculated value is {value}."
            else:
                answer = "I could not find the required data to answer your question."
                
            execution_time_ms = (time.time() - t0) * 1000
            
            response = QueryResponse(
                query_id=query_id,
                answer=answer,
                value=float(value) if value is not None else None,
                chart=None, # Simplified for now
                citations=citations,
                disagreements=disagreements,
                dataset_version=CURRENT_DATASET_VERSION,
                trace_id=hex(span.get_span_context().trace_id),
                execution_time_ms=execution_time_ms,
                cache_hit=False
            )
            
            # 6. Save to Cache
            try:
                cache_service.set(cache_key, response.model_dump(), CURRENT_DATASET_VERSION, db)
            except Exception as e:
                log.warning("Cache write failed", error=str(e))
            
            QUERY_COUNT.labels(status="success_computed").inc()
            QUERY_LATENCY.observe(execution_time_ms / 1000.0)
            log.info("Query successful", query_id=query_id, latency_ms=execution_time_ms, action=plan.get("action"))
            return response
            
        except Exception as e:
            QUERY_COUNT.labels(status="error").inc()
            log.error("Query failed", query_id=query_id, error=str(e), exc_info=True)
            span.record_exception(e)
            raise HTTPException(status_code=500, detail="Internal Server Error")
