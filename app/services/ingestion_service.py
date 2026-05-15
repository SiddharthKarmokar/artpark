import csv
import os
import datetime
from decimal import Decimal, InvalidOperation
from sqlalchemy.orm import Session
from app.models.domain import RawRecord, NormalizedRecord, ReconciliationDecision
from app.core.config import settings
from app.core.observability import DISAGREEMENT_COUNT
import structlog

log = structlog.get_logger("app.ingestion")

def load_csv(path: str) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows

def parse_date(date_str: str) -> datetime.date:
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

def parse_decimal(val_str: str) -> Decimal:
    try:
        return Decimal(val_str).quantize(Decimal('0.01'))
    except InvalidOperation:
        return Decimal('0.00')

def ingest_domain_data(db: Session, domain: str = settings.domain):
    domain_dir = os.path.join(settings.data_root, domain)
    if not os.path.isdir(domain_dir):
        log.error("Domain directory not found", domain_dir=domain_dir)
        return

    # Clear existing data for idempotency during dev
    db.query(RawRecord).delete()
    db.query(NormalizedRecord).delete()
    db.query(ReconciliationDecision).delete()
    db.commit()

    # Phase 1: Load raw data
    records_by_key = {}
    for fname in os.listdir(domain_dir):
        if not fname.endswith(".csv"):
            continue
        source = fname[:-4]
        rows = load_csv(os.path.join(domain_dir, fname))
        
        for row in rows:
            # Map columns to standard names
            ticker = row.get("ticker") or row.get("symbol")
            date_str = row.get("date") or row.get("trade_date")
            close_price_str = row.get("close") or row.get("close_price")
            
            if not ticker or not date_str or close_price_str is None:
                continue

            date_val = parse_date(date_str)
            
            raw = RawRecord(
                domain=domain,
                source=source,
                ticker=ticker,
                date=date_val,
                raw_data=row
            )
            db.add(raw)
            
            # Group for reconciliation
            key = (ticker, date_val)
            if key not in records_by_key:
                records_by_key[key] = {}
            
            records_by_key[key][source] = parse_decimal(close_price_str)
            
    db.commit()
    log.info("Raw records ingested successfully")

    # Phase 2: Reconcile and Normalize
    for (ticker, date_val), sources_data in records_by_key.items():
        prices = list(sources_data.values())
        if not prices:
            continue
            
        final_price = prices[0]
        
        # Detect disagreement
        if len(set(prices)) > 1:
            DISAGREEMENT_COUNT.inc()
            log.warning("Disagreement detected", ticker=ticker, date=str(date_val), sources=list(sources_data.keys()))
            
            # Simple reconciliation rule: Average them or prefer a specific source
            # For this test, let's prefer 'prices_source_a' if it exists, otherwise average
            if 'prices_source_a' in sources_data:
                final_price = sources_data['prices_source_a']
                rule = "prefer_source_a"
            else:
                final_price = sum(prices) / len(prices)
                final_price = final_price.quantize(Decimal('0.01'))
                rule = "average"
                
            decision = ReconciliationDecision(
                ticker=ticker,
                date=date_val,
                conflict_type="price_discrepancy",
                decision_rule=rule,
                resolved_value=final_price
            )
            db.add(decision)

        normalized = NormalizedRecord(
            domain=domain,
            ticker=ticker,
            date=date_val,
            close_price=final_price,
            dataset_version=1
        )
        db.add(normalized)
        
    db.commit()
    log.info("Data normalization complete")
