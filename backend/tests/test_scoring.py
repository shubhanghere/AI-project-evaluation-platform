import pytest
from backend.app.evaluator import DEFAULT_CRITERIA, aggregate

def test_weighted_score_is_deterministic():
    values={c['key']:{'score':80,'evidence':['line 1'],'confidence':0.8} for c in DEFAULT_CRITERIA}
    assert aggregate(DEFAULT_CRITERIA,values)['overall_score']==80

def test_reject_weight_or_score_errors():
    with pytest.raises(ValueError): aggregate([{'key':'x','weight':90}],{'x':{'score':50}})
    values={c['key']:{'score':101} for c in DEFAULT_CRITERIA}
    with pytest.raises(ValueError): aggregate(DEFAULT_CRITERIA,values)
