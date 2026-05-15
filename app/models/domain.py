from sqlalchemy import Column, Integer, String, DateTime, JSON, Numeric
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class RecordStatus(enum.Enum):
    RAW = "RAW"
    NORMALIZED = "NORMALIZED"

class DisagreementStatus(enum.Enum):
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"

class RawRecord(Base):
    __tablename__ = "raw_records"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, index=True)
    source = Column(String, index=True)
    ticker = Column(String, index=True)
    date = Column(DateTime, index=True)
    raw_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class NormalizedRecord(Base):
    __tablename__ = "normalized_records"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, index=True)
    ticker = Column(String, index=True)
    date = Column(DateTime, index=True)
    close_price = Column(Numeric(10, 2))
    dataset_version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ReconciliationDecision(Base):
    __tablename__ = "reconciliation_decisions"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    date = Column(DateTime, index=True)
    conflict_type = Column(String)
    decision_rule = Column(String)
    resolved_value = Column(Numeric(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CacheLineage(Base):
    __tablename__ = "cache_lineage"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String, unique=True, index=True)
    dataset_version = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
