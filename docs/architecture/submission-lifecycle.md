# Submission lifecycle

See the sequence diagram and reliability notes in the primary report. Production request stages are metadata creation, presigned transfer, upload verification/scanning, transactional enqueue, isolated processing, evidence retrieval, validated evaluation, deterministic aggregation, review policy, and result retrieval. Keep HTTP calls short: evaluation is always asynchronous. Each state transition emits an audit event with actor/service, request ID, attempt, timestamp, and reason code.
