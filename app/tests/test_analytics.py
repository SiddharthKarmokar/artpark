from app.services.analytics_engine import AnalyticsEngine
import datetime
from decimal import Decimal
from unittest.mock import MagicMock
from app.models.domain import NormalizedRecord

def test_moving_average_calculation():
    # Setup mock DB session
    mock_db = MagicMock()
    engine = AnalyticsEngine(db=mock_db)
    
    # Mock return values for DB query
    records = [
        NormalizedRecord(ticker="INFY", date=datetime.date(2026, 4, 15), close_price=Decimal("1700.00")),
        NormalizedRecord(ticker="INFY", date=datetime.date(2026, 4, 16), close_price=Decimal("1720.00")),
    ]
    
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_order = mock_filter.order_by.return_value
    mock_limit = mock_order.limit.return_value
    mock_limit.all.return_value = records
    
    # Plan
    plan = {
        "action": "moving_average",
        "params": {
            "ticker": "INFY",
            "end_date": "2026-04-16",
            "days": 2
        }
    }
    
    # Execute
    value, citations, disagreements = engine.execute_plan(plan)
    
    assert value == Decimal("1710.00")
    assert len(citations) == 2
