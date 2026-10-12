# Deployment guide

## Local

PowerShell: create and activate a Python venv, install `requirements.txt`, set `DATABASE_URL=sqlite:///./local.db`, then run `python -m uvicorn backend.app.main:app --reload`. The API starts its in-process polling worker. This mode is for demonstration only.

## Production design

Build and scan an immutable image in CI; deploy API and worker as distinct ECS services in private subnets behind an ALB. Configure RDS PostgreSQL, S3, SQS/DLQ, outbox relay, task roles, Secrets Manager, TLS, CloudWatch alarms, and backups via IaC. Run migrations as a controlled one-off task. Drain API requests and stop workers from taking new messages before deployment. Use rolling/canary health gates and rollback to a schema-compatible image. Validate backup restoration and queue redrive procedures. No production environment is provisioned by this repository.
