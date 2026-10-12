# Data model

The production relational model is represented in `diagrams/database-er.mmd`; `schema.sql` gives PostgreSQL DDL for core entities. All tenant-bound reads must include tenant/course authorization predicates. Rubric versions, model/prompt versions, source asset checksums, evaluator version, and policy version are snapshotted per job/result so historical scores remain interpretable. Assets live in object storage; SQL stores metadata and immutable object keys. Retention is assignment-configured with legal hold and auditable deletion.

PoC schema is intentionally narrower: submissions, rubrics, evaluations, reviews. It is not a production migration.
