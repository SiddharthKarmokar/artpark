import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from prometheus_client import Counter, Histogram
from fastapi import FastAPI
import structlog

from app.core.config import settings

# Prometheus Metrics
QUERY_COUNT = Counter('analytics_queries_total', 'Total number of queries', ['status'])
DISAGREEMENT_COUNT = Counter('analytics_disagreements_total', 'Total number of data disagreements encountered')
CACHE_HITS = Counter('analytics_cache_hits_total', 'Total number of cache hits')
QUERY_LATENCY = Histogram('analytics_query_latency_seconds', 'Query latency in seconds')

def setup_observability(app: FastAPI, engine):
    # Setup Structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Setup OpenTelemetry
    resource = Resource.create({"service.name": "tabular-analytics"})
    provider = TracerProvider(resource=resource)
    
    if settings.otel_exporter_otlp_endpoint:
        processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint))
        provider.add_span_processor(processor)
        
    trace.set_tracer_provider(provider)
    
    # Instrumentations
    FastAPIInstrumentor.instrument_app(app)
    if engine:
        SQLAlchemyInstrumentor().instrument(engine=engine)
    RedisInstrumentor().instrument()
    
    return structlog.get_logger("app")
