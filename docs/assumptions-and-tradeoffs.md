# Assumptions and tradeoffs

- Average traffic is uniform only for arithmetic; real arrival peaks are assumed at 10× for illustrative sizing, not measured.
- 8.5-minute mean is the midpoint of the supplied 2–15 minute range; actual duration distribution must be measured.
- PoC SQLite/in-process polling worker favors zero-service startup; it is process-local, non-durable, and unsuitable for multi-instance use.
- PoC string IDs simplify demos; production uses UUIDs and tenant IDs.
- PoC has no auth and trusts supplied student IDs; never expose beyond local development.
- The deterministic mock score depends on text length and is intentionally not a quality model.
- PostgreSQL/SQS/S3/ECS are proposed production services; no cloud deployment has occurred.
- Provider choice requires legal/privacy, quality, cost, latency, and data-residency review.
- Upload size, course tenancy, retention, SLO, RPO/RTO, and review rules require product confirmation before production.
