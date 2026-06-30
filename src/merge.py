from typing import List, Dict
from rapidfuzz import fuzz
from models import CandidateProfile, ProvenanceEntry, Skill
from confidence import score_field, tier_for_score
from normalize import normalize_phone, normalize_email, normalize_whitespace, normalize_skill

def records_match(a: Dict, b: Dict) -> bool:
    """
    Decides if two raw records (possibly from different sources) belong to the same candidate.
    """
    email_a = normalize_email(a.get("email"))
    email_b = normalize_email(b.get("email"))
    if email_a and email_b and email_a == email_b:
        return True

    phone_a = normalize_phone(a.get("phone"))
    phone_b = normalize_phone(b.get("phone"))
    if phone_a and phone_b and phone_a == phone_b:
        return True

    name_a = a.get("full_name")
    name_b = b.get("full_name")
    if name_a and name_b:
        similarity = fuzz.ratio(name_a.lower(), name_b.lower())
        if similarity >= 90:
            return True

    return False

def group_records(records: List[Dict]) -> List[List[Dict]]:
    """
    Groups raw records into clusters belonging to the same candidate.
    """
    groups: List[List[Dict]] = []
    for record in records:
        placed = False
        for group in groups:
            if any(records_match(record, existing) for existing in group):
                group.append(record)
                placed = True
                break
        if not placed:
            groups.append([record])
    return groups

SOURCE_PRIORITY = {
    "csv": 3,
    "github": 2,
    "linkedin": 2,
    "resume": 1,
    "notes": 0,
}

def pick_value(group: List[Dict], field: str):
    """
    Picks the winning value for a field across a group of raw records, using source priority. Returns (value, source) or (None, None).
    """
    candidates = [(r.get(field), r.get("_source", "unknown")) for r in group if r.get(field)]
    if not candidates:
        return None, None
    candidates.sort(key=lambda c: SOURCE_PRIORITY.get(c[1], 0), reverse=True)
    return candidates[0]

def build_candidate(group: List[Dict], candidate_id: str) -> CandidateProfile:
    provenance = []

    name_val, name_src = pick_value(group, "full_name")
    email_val, email_src = pick_value(group, "email")
    phone_val, phone_src = pick_value(group, "phone")
    headline_val, headline_src = pick_value(group, "headline")

    norm_email = normalize_email(email_val)
    norm_phone = normalize_phone(phone_val)

    if name_val:
        provenance.append(ProvenanceEntry(field="full_name", source=name_src, method="source_priority"))
    if norm_email:
        provenance.append(ProvenanceEntry(field="emails", source=email_src, method="normalize_email"))
    if norm_phone:
        provenance.append(ProvenanceEntry(field="phones", source=phone_src, method="normalize_phone_e164"))
    if headline_val:
        provenance.append(ProvenanceEntry(field="headline", source=headline_src, method="source_priority"))
        
    confidence_scores = {}
    if norm_email:
        confidence_scores["emails"] = score_field(group, "email", email_src, norm_email)
    if norm_phone:
        confidence_scores["phones"] = score_field(group, "phone", phone_src, norm_phone)
    if headline_val:
        confidence_scores["headline"] = score_field(group, "headline", headline_src, headline_val)

    overall = round(sum(confidence_scores.values()) / len(confidence_scores), 3) if confidence_scores else None
    status = tier_for_score(overall) if overall is not None else None

    return CandidateProfile(
        candidate_id=candidate_id,
        full_name=normalize_whitespace(name_val) or "Unknown",
        emails=[norm_email] if norm_email else [],
        phones=[norm_phone] if norm_phone else [],
        headline=normalize_whitespace(headline_val),
        confidence=confidence_scores,
        overall_confidence=overall,
        validation_status=status,
        provenance=provenance,
    )

def merge_all(records: List[Dict]) -> List[CandidateProfile]:
    groups = group_records(records)
    profiles = []
    for i, group in enumerate(groups):
        candidate_id = f"c_{i:05d}"
        profiles.append(build_candidate(group, candidate_id))
    return profiles