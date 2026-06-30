from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from enum import Enum


class Location(BaseModel):
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None


class Links(BaseModel):
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    other: List[str] = []


class Skill(BaseModel):
    name: str
    confidence: float
    sources: List[str] = []


class Experience(BaseModel):
    company: str
    title: str
    start: Optional[str] = None
    end: Optional[str] = None
    summary: Optional[str] = None


class Education(BaseModel):
    institution: str
    degree: Optional[str] = None
    field: Optional[str] = None
    end_year: Optional[int] = None


class ProvenanceEntry(BaseModel):
    field: str
    source: str
    method: str
    timestamp: Optional[str] = None


class ValidationStatus(str, Enum):
    PRODUCTION_READY = "PRODUCTION_READY"
    HIGH_CONFIDENCE = "HIGH_CONFIDENCE"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    REJECTED = "REJECTED"


class CandidateProfile(BaseModel):
    candidate_id: str
    full_name: str
    emails: List[str] = []
    phones: List[str] = []
    location: Optional[Location] = None
    links: Optional[Links] = None
    headline: Optional[str] = None
    years_experience: Optional[float] = None
    skills: List[Skill] = []
    experience: List[Experience] = []
    education: List[Education] = []
    provenance: List[ProvenanceEntry] = []
    confidence: Dict[str, float] = {}
    overall_confidence: Optional[float] = None
    validation_status: Optional[ValidationStatus] = None