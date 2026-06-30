from typing import Dict, Any
from models import CandidateProfile

def get_from_path(profile: CandidateProfile, path: str):
    """
    Resolves simple paths like 'emails[0]', 'full_name', 'confidence.phones' against a CandidateProfile.
    """
    data = profile.model_dump()
    if "[" in path:
        base, idx = path[:-1].split("[")
        idx = int(idx)
        values = data.get(base) or []
        return values[idx] if idx < len(values) else None
    if "." in path:
        parts = path.split(".")
        current = data
        for p in parts:
            if current is None:
                return None
            current = current.get(p)
        return current
    return data.get(path)

def project(profile: CandidateProfile, config: Dict[str, Any]) -> Dict:
    """
    Reshapes a canonical CandidateProfile into the view requested by config. Never mutates the canonical record. Validates required fields.
    """
    output = {}
    on_missing = config.get("on_missing", "null")

    for field_spec in config["fields"]:
        out_path = field_spec["path"]
        source_path = field_spec.get("from", out_path)
        required = field_spec.get("required", False)

        value = get_from_path(profile, source_path)

        if value is None:
            if required and on_missing == "error":
                raise ValueError(f"Required field '{out_path}' is missing for candidate {profile.candidate_id}")
            if on_missing == "omit":
                continue
            output[out_path] = None
        else:
            output[out_path] = value

    if config.get("include_confidence", False):
        output["confidence"] = profile.confidence
        output["overall_confidence"] = profile.overall_confidence

    return output