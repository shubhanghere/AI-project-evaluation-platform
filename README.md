# AlmaBetter Project Evaluation Platform

Architecture assignment deliverable and small offline proof of concept (PoC) for asynchronous, rubric-driven evaluation of student projects.

## What is here

- `output/submission-report.md`: self-contained architecture submission.
- `docs/architecture/diagrams/`: Mermaid system, sequence, ER, evaluation, deployment, and recovery diagrams.
- `docs/`: focused API, schema, security, reliability, AI, deployment, research, roadmap, and assumptions notes.
- `backend/app/`: FastAPI API, SQLAlchemy/SQLite persistence, rubric scoring, mock evaluator, and a local background worker.
- `backend/tests/`: API and scoring tests.

The PoC uses SQLite and an in-process worker for easy offline startup. They are explicitly development adapters, not durable production services. The production reference uses PostgreSQL, transactional outbox, SQS/DLQ, S3, isolated workers, and a provider interface.

## Requirements and setup (PowerShell)

Python 3.11+ (tested here with Python 3.13) is required. Docker is optional and is not installed in the inspected environment.

```powershell
cd .\almabetter-project-evaluation-platform
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

## Run the API and worker

The local worker runs as a FastAPI lifespan background task. It is convenient for a single-process demo; run a separate durable worker service in production.

```powershell
$env:DATABASE_URL = "sqlite:///./local.db"
python -m uvicorn backend.app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`. Readiness: `GET /health/ready`.

## Example requests

```powershell
$body = @{ student_id = "student-1"; course_id = "course-1"; assignment_id = "assignment-1"; title = "Demo project"; content = "A small Python service with tests and documentation." } | ConvertTo-Json
$created = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/submissions -ContentType 'application/json' -Body $body
$created | ConvertTo-Json -Depth 8
$jobBody = @{ idempotency_key = "demo-eval-001" } | ConvertTo-Json
$job = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/submissions/$($created.id)/evaluations" -ContentType 'application/json' -Body $jobBody
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/evaluations/$($job.id)"
```

The default rubric is seeded as editable data on startup. `GET /api/v1/rubrics` lists it; `POST /api/v1/rubrics` creates a versioned rubric. `GET /api/v1/submissions/{id}/result` returns the result when complete.

## Tests

```powershell
python -m pip install pytest
python -m pytest backend/tests -q
```

## Generate report

The Markdown report is the source of truth. PDF generation is not configured in this environment; use a reviewed Markdown-to-PDF renderer if a PDF is required. Mermaid diagrams are source `.mmd` files and can be rendered with Mermaid CLI or GitHub's Mermaid support.

## Production direction

See the submission report. The report distinguishes initial 30/day architecture, the 10,000/day target, PoC implementation, and production-only components. No AWS deployment or live LLM calls are claimed.

## Limitations

The PoC has no authentication, upload pipeline, real source-provider integration, durable cross-process queue, or sandboxed code execution. Never expose the development API as a production service.

Latest verification in this environment: python -m compileall backend/app backend/tests succeeded; python -m pytest backend/tests -q reported 4 passed; the OpenAPI snapshot parsed as 3.1.0 with 9 paths. Docker/PDF rendering tools were not available.
