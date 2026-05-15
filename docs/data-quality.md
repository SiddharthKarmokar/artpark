# Data Quality(Same as Legacy, no changes made)

## Disagreement Handling
Financial data providers often disagree on historical prices due to differing policies on corporate actions (e.g., dividends, splits).

Our ingestion pipeline handles disagreements natively:
---
1. **Detection**: Prices from all sources (e.g., Source A, Source B) are compared per ticker and date.
2. **Reconciliation**: If prices differ, a `ReconciliationDecision` record is stored detailing the conflict and the rule applied (e.g., "prefer_source_a" or "average").
3. **Normalization**: The unified value is saved as a `NormalizedRecord`.
4. **Transparency**: All `DisagreementMetadata` relevant to a user's query is surfaced directly in the API response.

## Provenance Tracking
Every query response includes citations. Citations point to the specific dataset version and the database record IDs used to generate the answer.
