import json

DEFAULT_CRITERIA = [
    {"key":"functionality","name":"Functionality","weight":25},
    {"key":"code_quality","name":"Code Quality","weight":20},
    {"key":"architecture","name":"Architecture","weight":20},
    {"key":"problem_solving","name":"Problem Solving","weight":15},
    {"key":"documentation","name":"Documentation","weight":10},
    {"key":"innovation","name":"Innovation / AI Usage","weight":10},
]

def aggregate(criteria, scores):
    if not criteria or abs(sum(float(c["weight"]) for c in criteria) - 100) > 1e-6:
        raise ValueError("Rubric weights must sum to 100")
    result=[]
    for c in criteria:
        score=float(scores[c["key"]]["score"])
        if not 0 <= score <= 100: raise ValueError("Criterion score must be between 0 and 100")
        result.append({**c, **scores[c["key"]], "weighted_score": round(score*float(c["weight"])/100, 2)})
    return {"criteria": result, "overall_score": round(sum(x["weighted_score"] for x in result), 2)}

class MockEvaluator:
    """Offline deterministic adapter. Replace behind this interface; it is not an LLM."""
    def evaluate(self, content: str, criteria: list[dict]) -> dict:
        size=len(content.strip())
        values={c["key"]:{"score":min(90, max(35, 45 + min(size, 450)//10)),
                           "evidence": [f"Submitted text length: {size} characters"],
                           "confidence": 0.35} for c in criteria}
        return aggregate(criteria, values)

def dump(value): return json.dumps(value, ensure_ascii=False)
