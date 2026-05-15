# 002: Redis Caching

**Date**: 2026-05-15

## Context
Queries requiring LLM planning are latency-intensive. Many questions are repeatedly asked. Caching is essential, but simply caching API responses is dangerous in finance, as datasets update and cached values become instantly stale.

## Decision
Implement a Redis-based cache accompanied by a dataset-version-aware invalidation strategy.

## Consequences
- **Positive**: Frequent queries are answered in milliseconds. If the underlying dataset changes (e.g., a corporate action is applied retroactively), we can increment the dataset version and intelligently purge or ignore stale cache lines.
- **Negative**: Requires maintaining a `CacheLineage` mapping in the database to track which cache keys belong to which dataset versions.

## Alternatives Considered
- In-memory LRU Cache: Does not scale horizontally across multiple API instances.
- TTL-based invalidation only: Rejected as it allows serving incorrect financial data for up to the TTL duration after an update.
