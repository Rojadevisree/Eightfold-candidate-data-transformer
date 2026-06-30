import os
import sys
import json
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from models import CandidateProfile
from normalize import normalize_phone, normalize_email, normalize_whitespace, normalize_skill
from merge import records_match, pick_value, build_candidate, merge_all
from confidence import score_field, tier_for_score
from parsers.csv_parser import parse_csv
from project import project

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "sample_inputs")


# 1. Normalizers
def test_normalize_phone_to_e164():
    assert normalize_phone("415-555-0110") == "+14155550110"

def test_normalize_email_lowercases_and_strips():
    assert normalize_email("  Jane@ACME.com ") == "jane@acme.com"

def test_normalize_email_rejects_garbage():
    assert normalize_email("not-an-email") is None

def test_normalize_skill_maps_alias_to_canonical():
    assert normalize_skill("ML") == "Machine Learning"
    assert normalize_skill("javascript") == "JavaScript"


# 2. records_match / identity resolution
def test_records_match_by_email_case_insensitive():
    a = {"email": "jane@acme.com", "full_name": "Jane Doe"}
    b = {"email": "JANE@ACME.com", "full_name": "J. Doe"}
    assert records_match(a, b) is True

def test_records_no_match_different_people():
    a = {"email": "jane@acme.com", "full_name": "Jane Doe"}
    b = {"email": "bob@other.com", "full_name": "Bob Smith"}
    assert records_match(a, b) is False


# 3. pick_value — source priority
def test_pick_value_prefers_csv_over_notes():
    group = [
        {"phone": "415-555-9999", "_source": "notes"},
        {"phone": "415-555-0110", "_source": "csv"},
    ]
    value, source = pick_value(group, "phone")
    assert value == "415-555-0110"
    assert source == "csv"

def test_pick_value_ignores_empty_strings():
    group = [{"phone": "", "_source": "csv"}, {"phone": "415-555-0110", "_source": "notes"}]
    value, source = pick_value(group, "phone")
    assert value == "415-555-0110"
    assert source == "notes"


# 4. build_candidate / merge_all
def test_build_candidate_populates_email_phone_and_provenance():
    group = [
        {"full_name": "Jane Doe", "email": "jane@acme.com", "phone": "415-555-0110", "_source": "csv"},
    ]
    profile = build_candidate(group, "c_00000")
    assert isinstance(profile, CandidateProfile)
    assert profile.emails == ["jane@acme.com"]
    assert profile.phones == ["+14155550110"]
    assert any(p.field == "emails" and p.source == "csv" for p in profile.provenance)
    assert profile.overall_confidence is not None
    assert 0.0 <= profile.overall_confidence <= 1.0
    assert profile.validation_status is not None

def test_build_candidate_defaults_name_to_unknown_when_missing():
    group = [{"email": "x@y.com", "_source": "csv"}]
    profile = build_candidate(group, "c_00001")
    assert profile.full_name == "Unknown"

def test_merge_all_on_real_recruiter_csv():
    records = parse_csv(os.path.join(SAMPLE_DIR, "recruiter_export.csv"))
    profiles = merge_all(records)
    assert len(profiles) == 2
    names = {p.full_name for p in profiles}
    assert "Jane Doe" in names


# 5. EDGE CASE (required) — missing/malformed source must not crash
def test_parse_csv_missing_file_returns_empty_not_crash():
    records = parse_csv(os.path.join(SAMPLE_DIR, "does_not_exist.csv"))
    assert records == []

def test_parse_csv_skips_row_with_no_name_and_no_email(tmp_path):
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text(
        "name,email,phone,current_company,title\n"
        ",,415-555-0110,Acme,SWE\n"
        "Jane Doe,jane@acme.com,,,\n"
    )
    records = parse_csv(str(bad_csv))
    assert len(records) == 1
    assert records[0]["full_name"] == "Jane Doe"

def test_normalize_phone_handles_malformed_number_gracefully():
    result = normalize_phone("9876543210")
    assert result is None or result.startswith("+")


# 6. Projector — both real configs
def test_project_default_config_includes_confidence():
    group = [{"full_name": "Jane Doe", "email": "jane@acme.com", "phone": "415-555-0110", "_source": "csv"}]
    profile = build_candidate(group, "c_00000")
    with open(os.path.join(SAMPLE_DIR, "config_default.json")) as f:
        config = json.load(f)
    output = project(profile, config)
    assert output["full_name"] == "Jane Doe"
    assert output["primary_email"] == "jane@acme.com"
    assert "overall_confidence" in output

def test_project_minimal_config_omits_missing_and_renames():
    group = [{"email": "jane@acme.com", "_source": "csv"}]
    profile = build_candidate(group, "c_00000")
    with open(os.path.join(SAMPLE_DIR, "config_minimal.json")) as f:
        config = json.load(f)
    output = project(profile, config)
    assert output == {"name": "Unknown"}
    assert "confidence" not in output