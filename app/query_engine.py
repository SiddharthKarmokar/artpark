"""Turn a natural-language question into a cited numeric answer + chart spec.

Current implementation hands the raw rows to the LLM (capped at MAX_ROWS_TO_LLM)
and asks for JSON back. This works but isn't ideal for precision.
"""
import json
import logging
from typing import Any

from app.config import MAX_ROWS_TO_LLM
from app.providers import LLMProvider

log = logging.getLogger("query")

SYSTEM = """You answer questions about tabular data. You will be given:
- The user's question.
- One or more tables (as JSON arrays of row objects).

Return a JSON object with these keys exactly:
  answer:     str   - short natural-language answer
  value:      number or null - the primary numeric answer if applicable
  chart:      object - { "type": "line|bar|table", "x": str, "y": str } or null
  citations:  array of strings - the table names and row identifiers used

Do not invent data. If the answer is not in the tables, set value to null and say so.
"""


def answer(question: str, tables: dict[str, list[dict[str, Any]]], provider: LLMProvider) -> dict[str, Any]:
    # send the first MAX_ROWS_TO_LLM rows of each table. obvious limitation, but works for small data.
    payload = {name: rows[:MAX_ROWS_TO_LLM] for name, rows in tables.items()}
    user = f"Question: {question}\n\nTables:\n{json.dumps(payload, default=str)}"
    raw = provider.complete(SYSTEM, user)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        log.warning("provider returned non-JSON; wrapping as plain answer")
        return {"answer": raw, "value": None, "chart": None, "citations": []}
