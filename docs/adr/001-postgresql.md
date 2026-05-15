# 001: PostgreSQL Migration

**Date**: 2026-05-15

## Context
The legacy application loaded CSV datasets entirely into memory during startup. As data volumes increased and the need for data provenance and complex disagreement tracking grew, in-memory processing became untenable.

## Decision
We migrated the data persistence layer to PostgreSQL and SQLAlchemy. 

## Consequences
- **Positive**: We can now store raw data, normalized data, and reconciliation rules persistently. The analytics engine can perform deterministic queries on a structured SQL database rather than manipulating memory objects. Data provenance is fully auditable.
- **Negative**: Adds operational overhead (managing a database instance, handling migrations).

## Alternatives Considered
- SQLite: Deemed insufficient for high-concurrency production workloads.
- NoSQL (MongoDB): Did not fit the strictly tabular and relational nature of financial time-series and citation mapping.
