import json, logging, threading, uuid
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .database import Base, engine, get_db, SessionLocal
from .models import Submission, Rubric, Evaluation, Review
from .evaluator import DEFAULT_CRITERIA, aggregate
from .worker import worker_loop

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
stop_event=threading.Event(); worker_thread=None

@asynccontextmanager
async def lifespan(app):
    global worker_thread
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.scalar(select(Rubric).where(Rubric.name=="AlmaBetter Default")) is None:
            db.add(Rubric(id=str(uuid.uuid4()),name="AlmaBetter Default",version=1,criteria_json=json.dumps(DEFAULT_CRITERIA),active=1)); db.commit()
    stop_event.clear(); worker_thread=threading.Thread(target=worker_loop,args=(stop_event,),daemon=True); worker_thread.start()
    yield
    stop_event.set()
    if worker_thread: worker_thread.join(timeout=3)

app=FastAPI(title="Project Evaluation Platform API",version="1.0.0",lifespan=lifespan)

@app.middleware("http")
async def request_id(request: Request, call_next):
    rid=request.headers.get("X-Request-ID") or str(uuid.uuid4()); request.state.request_id=rid
    response=await call_next(request); response.headers["X-Request-ID"]=rid; return response

@app.exception_handler(HTTPException)
async def http_error(request, exc):
    return JSONResponse(status_code=exc.status_code,content={"error":{"code":"http_error","message":str(exc.detail),"request_id":getattr(request.state,"request_id",None)}})

class SubmissionIn(BaseModel):
    student_id: str=Field(min_length=1,max_length=128); course_id: str=Field(min_length=1,max_length=128)
    assignment_id: str=Field(min_length=1,max_length=128); title: str=Field(min_length=1,max_length=240)
    content: str=Field(default="",max_length=500000)
class Criterion(BaseModel): key: str; name: str; weight: float=Field(gt=0,le=100)
class RubricIn(BaseModel):
    name: str
    criteria: list[Criterion]
    @model_validator(mode="after")
    def validate_weights(self):
        if not self.criteria or len({c.key for c in self.criteria}) != len(self.criteria): raise ValueError("criteria must be non-empty with unique keys")
        if abs(sum(c.weight for c in self.criteria)-100)>1e-6: raise ValueError("weights must sum to 100")
        return self
class EvalIn(BaseModel): idempotency_key: str=Field(min_length=1,max_length=200); rubric_id: str|None=None
class ReviewIn(BaseModel): reviewer_id: str; decision: str=Field(pattern="^(approve|reject)$"); comment: str=""

def submission_out(s): return {"id":s.id,"student_id":s.student_id,"course_id":s.course_id,"assignment_id":s.assignment_id,"title":s.title,"status":s.status,"created_at":s.created_at.isoformat()}
def evaluation_out(e): return {"id":e.id,"submission_id":e.submission_id,"status":e.status,"attempt":e.attempt,"score":e.score,"created_at":e.created_at.isoformat(),"error":e.error}

@app.get("/health/live")
def live(): return {"status":"alive"}
@app.get("/health/ready")
def ready(db: Session=Depends(get_db)):
    try: db.execute(select(1)); return {"status":"ready","database":"ok"}
    except Exception: raise HTTPException(503,"database unavailable")
@app.post("/api/v1/submissions",status_code=201)
def create_submission(body: SubmissionIn, db: Session=Depends(get_db)):
    row=Submission(id=str(uuid.uuid4()),**body.model_dump()); db.add(row); db.commit(); db.refresh(row); return submission_out(row)
@app.get("/api/v1/submissions")
def list_submissions(limit:int=Query(default=50,ge=1,le=100), offset:int=Query(default=0,ge=0), student_id:str|None=None, db:Session=Depends(get_db)):
    q=select(Submission).order_by(Submission.created_at.desc()).offset(offset).limit(limit)
    if student_id: q=q.where(Submission.student_id==student_id)
    return {"items":[submission_out(s) for s in db.scalars(q)],"limit":limit,"offset":offset}
@app.get("/api/v1/submissions/{sid}")
def get_submission(sid:str,db:Session=Depends(get_db)):
    row=db.get(Submission,sid)
    if not row: raise HTTPException(404,"submission not found")
    return submission_out(row)
@app.get("/api/v1/rubrics")
def list_rubrics(db:Session=Depends(get_db)):
    return [{"id":r.id,"name":r.name,"version":r.version,"criteria":json.loads(r.criteria_json)} for r in db.scalars(select(Rubric).where(Rubric.active==1))]
@app.post("/api/v1/rubrics",status_code=201)
def create_rubric(body:RubricIn,db:Session=Depends(get_db)):
    row=Rubric(id=str(uuid.uuid4()),name=body.name,version=1,criteria_json=json.dumps([c.model_dump() for c in body.criteria]),active=1); db.add(row); db.commit()
    return {"id":row.id,"name":row.name,"version":row.version,"criteria":json.loads(row.criteria_json)}
@app.post("/api/v1/submissions/{sid}/evaluations",status_code=202)
def start_evaluation(sid:str,body:EvalIn,db:Session=Depends(get_db)):
    sub=db.get(Submission,sid)
    if not sub: raise HTTPException(404,"submission not found")
    existing=db.scalar(select(Evaluation).where(Evaluation.submission_id==sid,Evaluation.idempotency_key==body.idempotency_key))
    if existing: return evaluation_out(existing)
    rubric=db.get(Rubric,body.rubric_id) if body.rubric_id else db.scalar(select(Rubric).where(Rubric.name=="AlmaBetter Default",Rubric.active==1))
    if not rubric: raise HTTPException(404,"rubric not found")
    job=Evaluation(id=str(uuid.uuid4()),submission_id=sid,rubric_id=rubric.id,idempotency_key=body.idempotency_key,status="QUEUED"); db.add(job)
    try: db.commit()
    except IntegrityError:
        db.rollback(); job=db.scalar(select(Evaluation).where(Evaluation.submission_id==sid,Evaluation.idempotency_key==body.idempotency_key)); return evaluation_out(job)
    db.refresh(job); return evaluation_out(job)
@app.get("/api/v1/evaluations/{eid}")
def get_evaluation(eid:str,db:Session=Depends(get_db)):
    row=db.get(Evaluation,eid)
    if not row: raise HTTPException(404,"evaluation not found")
    return evaluation_out(row)
@app.get("/api/v1/submissions/{sid}/result")
def get_result(sid:str,db:Session=Depends(get_db)):
    row=db.scalar(select(Evaluation).where(Evaluation.submission_id==sid).order_by(Evaluation.created_at.desc()))
    if not row: raise HTTPException(404,"evaluation not found")
    if row.status!="COMPLETED": raise HTTPException(409,f"result unavailable; status={row.status}")
    return {**evaluation_out(row),"result":json.loads(row.result_json)}
@app.post("/api/v1/evaluations/{eid}/reviews",status_code=201)
def review(eid:str,body:ReviewIn,db:Session=Depends(get_db)):
    row=db.get(Evaluation,eid)
    if not row: raise HTTPException(404,"evaluation not found")
    if row.status!="COMPLETED": raise HTTPException(409,"evaluation must be completed before review")
    rev=Review(id=str(uuid.uuid4()),evaluation_id=eid,**body.model_dump()); db.add(rev); row.status="COMPLETED" if body.decision=="approve" else "REVIEW_REQUIRED"; db.commit()
    return {"id":rev.id,"evaluation_id":eid,"decision":rev.decision}
