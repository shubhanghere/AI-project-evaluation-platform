# API specification

The running FastAPI app publishes the exact PoC OpenAPI document at `/openapi.json`. This PoC omits authentication and upload endpoints; those contracts below describe the production API boundary. All endpoints are under `/api/v1`; bearer identity and role checks are mandatory in production.

| Method and path | Purpose | Success |
|---|---|---|
| POST `/submissions` | Create metadata, distinct from evaluating | 201 |
| GET `/submissions/{id}` | Authorized metadata | 200 |
| GET `/submissions?student_id=&limit=&offset=` | Paginated list | 200 |
| POST `/submissions/{id}/uploads` | Request short-lived scoped upload intent | 201 |
| POST `/submissions/{id}/uploads/{asset}/complete` | Verify checksum/size/object then finalize | 200 |
| POST `/submissions/{id}/evaluations` | Idempotently enqueue evaluation | 202 |
| GET `/evaluations/{id}` | Job status | 200 |
| GET `/submissions/{id}/result` | Result; 409 until terminal result ready | 200 |
| GET/POST `/rubrics` | List/create immutable rubric versions | 200/201 |
| POST `/evaluations/{id}/reviews` | Reviewer approve/reject | 201 |
| GET `/health/live`, `/health/ready` | Liveness/readiness | 200/503 |

PoC create example: `{"student_id":"s-1","course_id":"c-1","assignment_id":"a-1","title":"Demo","content":"..."}`. Evaluation: `{"idempotency_key":"client-generated-key","rubric_id":null}`. Success returns `{"id":"…","submission_id":"…","status":"QUEUED","attempt":0,"score":null}`. Errors use `{error:{code,message,request_id}}`. Production requires `Idempotency-Key`, stable error codes, authorization scoping, bounded pagination, per-user/course rate limits, and correlation IDs. Large payloads never pass through API request bodies.
