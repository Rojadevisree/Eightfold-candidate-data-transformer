from typing import List, Dict
from models import CandidateProfile

SOURCE_RELIABILITY = {
    "csv": 0.95,
    "github": 0.8,
    "linkedin": 0.85,
    "resume": 0.7,
    "notes": 0.5,
    "unknown": 0.4,
}

def extraction_score(source: str) -> float:
    return SOURCE_RELIABILITY.get(source, 0.4)

def agreement_score(group: List[Dict], field: str, winning_value, source_reliability: float = None) -> float:
    relevant = [r for r in group if r.get(field)]
    if not relevant:
        return 0.0
    if len(relevant) == 1:
        if source_reliability is not None and source_reliability >= 0.9:
            return 0.85
        return 0.6
    agreeing = sum(1 for r in relevant if r.get(field) == winning_value)
    return agreeing / len(relevant)

def validation_score(value, field: str) -> float:
    if value is None:
        return 0.0
    if field == "emails" and "@" not in str(value):
        return 0.0
    if field == "phones" and not str(value).startswith("+"):
        return 0.0
    return 1.0

def score_field(group: List[Dict], field: str, source: str, value, normalization_ok: bool = True) -> float:
    e = extraction_score(source)
    n = 1.0 if normalization_ok else 0.5
    a = agreement_score(group, field, value, source_reliability=e)
    v = validation_score(value, field)
    return round(e * n * a * v, 3)

def tier_for_score(score: float) -> str:
    if score >= 0.95:
        return "PRODUCTION_READY"
    if score >= 0.80:
        return "HIGH_CONFIDENCE"
    if score >= 0.60:
        return "NEEDS_REVIEW"
    return "REJECTED"