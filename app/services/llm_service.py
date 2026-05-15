import json
import requests
from typing import Protocol, Any, Dict
import structlog
from app.core.config import settings

log = structlog.get_logger("app.llm")

SYSTEM_PROMPT = """You are a financial query planner.
Your goal is to parse natural language questions into structured JSON query plans for an analytics engine.

Available actions:
- get_price: Get the closing price of a stock on a specific date.
  Requires: ticker (str), date (YYYY-MM-DD)
  
- moving_average: Get the moving average of a stock.
  Requires: ticker (str), end_date (YYYY-MM-DD), days (int)

- compare_price: Compare prices between two stocks on a date.
  Requires: ticker1 (str), ticker2 (str), date (YYYY-MM-DD)
  
Return EXACTLY a JSON object with this schema:
{
  "action": "action_name",
  "params": { ... }
}

If the query is unsupported, return {"action": "unsupported", "params": {}}.
Do not output markdown code blocks. Just raw JSON.
"""

class LLMProvider(Protocol):
    def plan_query(self, user_question: str) -> Dict[str, Any]: ...

class MockProvider:
    def plan_query(self, user_question: str) -> Dict[str, Any]:
        question = user_question.lower()
        if "infy" in question and "2026-04-10" in question:
            return {"action": "get_price", "params": {"ticker": "INFY", "date": "2026-04-10"}}
        if "moving average" in question:
            return {"action": "moving_average", "params": {"ticker": "INFY", "end_date": "2026-04-17", "days": 5}}
        return {"action": "get_price", "params": {"ticker": "UNKNOWN", "date": "2026-04-06"}}

class HostedProvider:
    def plan_query(self, user_question: str) -> Dict[str, Any]:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.hosted_api_key}", "Content-Type": "application/json"},
            json={
                "model": settings.hosted_model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_question},
                ],
                "temperature": 0,
                "response_format": {"type": "json_object"}
            },
            timeout=30,
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"]
        return json.loads(raw)

def get_llm_provider() -> LLMProvider:
    if settings.provider == "hosted":
        return HostedProvider()
    # Assume mock for default/fallback
    return MockProvider()
