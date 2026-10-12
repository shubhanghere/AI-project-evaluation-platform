# Technology decisions

| Decision | Selected | Alternatives | Trade-off and revisit trigger | Primary evidence |
|---|---|---|---|---|
| API | FastAPI + Pydantic | Django REST, Node frameworks | Low ceremony and typed OpenAPI fit a Python AI stack; Django if integrated admin/auth dominates | https://fastapi.tiangolo.com/tutorial/first-steps/ |
| Primary DB | PostgreSQL | MongoDB | Relational constraints and transactions fit jobs/rubric/audit; MongoDB if document aggregates dominate and cross-entity integrity is less central | https://www.postgresql.org/docs/current/tutorial-transactions.html ; https://www.mongodb.com/docs/manual/core/transactions/ |
| Queue | SQS + DLQ | RabbitMQ, Kafka | Managed delivery minimizes broker operations; RabbitMQ for complex routing, Kafka for retained high-throughput event streams | https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/working-with-visibility-timeouts.html |
| Assets | S3 | Database blobs, self-managed object storage | Direct uploads and lifecycle suit large files; alternatives if portability/residency/cost dominates, at extra operations | https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html ; https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html |
| Vector | Lexical first, pgvector when needed | Pinecone, Weaviate | Co-locates vectors/metadata; dedicated service when measured vector load or operations warrant separate lifecycle and cost | https://github.com/pgvector/pgvector |
| Compute | ECS services | EC2-managed services, Lambda | ECS runs long-lived separate API/worker services; EC2 if host control justifies patching, Lambda for short bounded tasks | https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html |
| Model | Hosted API behind adapter | Self-hosted model | Lower model-serving operations initially; self-host if sustained utilization, policy, and quality justify GPU cost and staffing | https://platform.openai.com/docs/guides/your-data |

Cost and operational effort: SQS/S3/RDS incur usage charges and reduce broker/storage administration; PostgreSQL still needs capacity, backups, migrations, and connection controls; hosted model costs are token-dependent and require per-assignment budgets. Exact price and quotas are region/account/date-specific and intentionally not guessed. Benchmark real repositories, provider calls, retrieval quality, and reviewer agreement before production selection.
