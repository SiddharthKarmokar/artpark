import json
from sqlalchemy.orm import Session
from app.core.redis import get_redis
from app.models.domain import CacheLineage
from app.core.config import settings
from app.core.observability import CACHE_HITS
import structlog

log = structlog.get_logger("app.cache")

class CacheService:
    def __init__(self):
        self.redis = get_redis()
        
    def get(self, key: str, current_version: int, db: Session):
        # 1. Check Redis
        data_str = self.redis.get(key)
        if not data_str:
            return None
            
        # 2. Verify dataset version in lineage tracking
        lineage = db.query(CacheLineage).filter_by(cache_key=key).first()
        if not lineage:
            # Ghost cache entry
            self.redis.delete(key)
            return None
            
        if lineage.dataset_version != current_version:
            log.info("Cache invalidated due to dataset version mismatch", key=key, old_ver=lineage.dataset_version, new_ver=current_version)
            self.redis.delete(key)
            db.delete(lineage)
            db.commit()
            return None
            
        CACHE_HITS.inc()
        log.debug("Cache hit", key=key)
        return json.loads(data_str)
        
    def set(self, key: str, value: dict, current_version: int, db: Session):
        # Store in Redis
        self.redis.setex(key, settings.cache_ttl, json.dumps(value))
        
        # Store lineage
        lineage = db.query(CacheLineage).filter_by(cache_key=key).first()
        if lineage:
            lineage.dataset_version = current_version
        else:
            lineage = CacheLineage(cache_key=key, dataset_version=current_version)
            db.add(lineage)
        db.commit()
        
    def invalidate_all(self, db: Session):
        """Simulate dataset update -> invalidate related cache entries."""
        # Get all keys from lineage
        lineages = db.query(CacheLineage).all()
        for lin in lineages:
            self.redis.delete(lin.cache_key)
            db.delete(lin)
        db.commit()
        log.info("All cache entries invalidated.")

cache_service = CacheService()
