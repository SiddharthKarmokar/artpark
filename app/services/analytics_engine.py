import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.domain import NormalizedRecord, ReconciliationDecision
from app.models.schemas import DisagreementMetadata, Citation
import structlog

log = structlog.get_logger("app.analytics")

class AnalyticsEngine:
    def __init__(self, db: Session):
        self.db = db

    def _get_disagreements(self, ticker: str, date_val: datetime.date):
        decisions = self.db.query(ReconciliationDecision).filter(
            ReconciliationDecision.ticker == ticker,
            ReconciliationDecision.date == date_val
        ).all()
        
        disagreements = []
        for d in decisions:
            disagreements.append(DisagreementMetadata(
                ticker=d.ticker,
                date=str(d.date),
                conflict_type=d.conflict_type,
                decision_rule=d.decision_rule,
                sources_involved=["source_a", "source_b"] # Simplification for now
            ))
        return disagreements

    def execute_plan(self, plan: dict) -> tuple[Decimal | None, list[Citation], list[DisagreementMetadata]]:
        action = plan.get("action")
        params = plan.get("params", {})
        
        citations = []
        disagreements = []
        
        if action == "get_price":
            ticker = params.get("ticker")
            date_str = params.get("date")
            if not ticker or not date_str:
                return None, [], []
                
            date_val = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            record = self.db.query(NormalizedRecord).filter(
                NormalizedRecord.ticker == ticker,
                NormalizedRecord.date == date_val
            ).first()
            
            if record:
                citations.append(Citation(source="NormalizedRecord", record_id=record.id))
                disagreements.extend(self._get_disagreements(ticker, date_val))
                return record.close_price, citations, disagreements
                
        elif action == "moving_average":
            ticker = params.get("ticker")
            end_date_str = params.get("end_date")
            days = params.get("days", 5)
            
            if not ticker or not end_date_str:
                return None, [], []
                
            end_date_val = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
            # Fetch last N days
            records = self.db.query(NormalizedRecord).filter(
                NormalizedRecord.ticker == ticker,
                NormalizedRecord.date <= end_date_val
            ).order_by(NormalizedRecord.date.desc()).limit(days).all()
            
            if not records:
                return None, [], []
                
            total = Decimal('0.00')
            for r in records:
                total += r.close_price
                citations.append(Citation(source="NormalizedRecord", record_id=r.id))
                disagreements.extend(self._get_disagreements(ticker, r.date))
                
            avg = total / Decimal(len(records))
            avg = avg.quantize(Decimal('0.01'))
            return avg, citations, disagreements
            
        return None, [], []
