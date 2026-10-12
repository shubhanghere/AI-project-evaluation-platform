import json, logging, time
from datetime import datetime, timezone
from sqlalchemy import select
from .database import SessionLocal
from .models import Evaluation, Submission, Rubric
from .evaluator import MockEvaluator, aggregate

log=logging.getLogger(__name__)

def process_one(evaluation_id: str, evaluator=None):
    evaluator=evaluator or MockEvaluator()
    with SessionLocal() as db:
        job=db.get(Evaluation, evaluation_id)
        if not job or job.status in {"COMPLETED","FAILED","CANCELLED"}: return
        job.status="PROCESSING"; job.attempt += 1; db.commit()
        submission=db.get(Submission, job.submission_id); rubric=db.get(Rubric, job.rubric_id)
        try:
            if submission is None or rubric is None: raise ValueError("Missing submission or rubric")
            criteria=json.loads(rubric.criteria_json)
            result=evaluator.evaluate(submission.content, criteria)
            # Validate and re-aggregate output instead of trusting provider-produced totals.
            by_key={c["key"]: {"score": c["score"], "evidence": c.get("evidence", []), "confidence": c.get("confidence", 0)} for c in result["criteria"]}
            result=aggregate(criteria, by_key)
            job.score=result["overall_score"]; job.result_json=json.dumps(result); job.status="COMPLETED"; job.error=None
        except Exception as exc:
            job.status="FAILED"; job.error=str(exc)[:1000]
            log.exception("evaluation_failed", extra={"evaluation_id": evaluation_id})
        job.updated_at=datetime.now(timezone.utc); db.commit()

def worker_loop(stop_event, poll_seconds=1.0):
    while not stop_event.is_set():
        with SessionLocal() as db:
            row=db.scalar(select(Evaluation.id).where(Evaluation.status=="QUEUED").order_by(Evaluation.created_at).limit(1))
        if row: process_one(row)
        else: stop_event.wait(poll_seconds)
