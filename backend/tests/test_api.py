import time
from fastapi.testclient import TestClient
from backend.app.main import app

def test_submission_evaluation_and_idempotency():
    with TestClient(app) as client:
        sub=client.post('/api/v1/submissions',json={'student_id':'test-student','course_id':'test-course','assignment_id':'test-assignment','title':'Test project','content':'A documented project with test coverage.'})
        assert sub.status_code==201, sub.text
        sid=sub.json()['id']
        assert client.get(f'/api/v1/submissions/{sid}').status_code==200
        body={'idempotency_key':'same-key-for-retry'}
        first=client.post(f'/api/v1/submissions/{sid}/evaluations',json=body)
        second=client.post(f'/api/v1/submissions/{sid}/evaluations',json=body)
        assert first.status_code==202 and first.json()['id']==second.json()['id']
        eid=first.json()['id']
        for _ in range(40):
            status=client.get(f'/api/v1/evaluations/{eid}').json()['status']
            if status=='COMPLETED': break
            time.sleep(.05)
        assert status=='COMPLETED'
        result=client.get(f'/api/v1/submissions/{sid}/result')
        assert result.status_code==200
        assert result.json()['result']['overall_score']>=0

def test_invalid_rubric_weights_and_missing_submission():
    with TestClient(app) as client:
        bad=client.post('/api/v1/rubrics',json={'name':'bad','criteria':[{'key':'x','name':'X','weight':40}]})
        assert bad.status_code==422
        missing=client.post('/api/v1/submissions/missing/evaluations',json={'idempotency_key':'key'})
        assert missing.status_code==404
        assert client.get('/health/live').json()['status']=='alive'
