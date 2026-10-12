# Deployment architecture

See `diagrams/deployment.mmd` and the production deployment section of the main report. AWS deployment is proposed only; no cloud resources exist. Run API and worker as separate ECS services in private subnets. Keep RDS and S3 private, use an ALB for ingress, SQS for work, task roles for identity, and CloudWatch/OpenTelemetry for operations.
