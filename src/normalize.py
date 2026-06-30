import re
import phonenumbers
from typing import Optional

def normalize_phone(raw: Optional[str], default_region: str = "US") -> Optional[str]:
    """
    Converts a raw phone string to E.164 format.Returns None if it can't be parsed 
    """
    if not raw:
        return None
    try:
        parsed = phonenumbers.parse(raw, default_region)
        if not phonenumbers.is_valid_number(parsed):
            return None
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        return None

def normalize_email(raw: Optional[str]) -> Optional[str]:
    """
    Lowercases and strips whitespace. Returns None if it doesn't look like an email.
    """
    if not raw:
        return None
    cleaned = raw.strip().lower()
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", cleaned):
        return None
    return cleaned

def normalize_whitespace(raw: Optional[str]) -> Optional[str]:
    """Collapses multiple spaces/control characters into single spaces."""
    if not raw:
        return None
    cleaned = re.sub(r"\s+", " ", raw).strip()
    return cleaned or None

SKILL_ALIASES = {
    "ml": "Machine Learning",
    "machine-learning": "Machine Learning",
    "machine learning": "Machine Learning",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "py": "Python",
    "python": "Python",
}

def normalize_skill(raw: Optional[str]) -> Optional[str]:
    """Maps a raw skill string to its canonical name via the alias table."""
    if not raw:
        return None
    key = raw.strip().lower()
    return SKILL_ALIASES.get(key, raw.strip().title())