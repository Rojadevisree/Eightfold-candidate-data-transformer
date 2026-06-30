import csv
from typing import List, Dict


def parse_csv(filepath: str) -> List[Dict]:
    """
    Reads a recruiter CSV export and returns a list of raw dicts,
    one per row. Does NOT normalize or validate yet — that happens later.
    Missing/garbage rows are skipped and logged, never crashed on.
    """
    records = []
    try:
        with open(filepath, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get("name") and not row.get("email"):
                    print(f"Skipping unusable row: {row}")
                    continue
                records.append({
                    "full_name": row.get("name", "").strip() or None,
                    "email": row.get("email", "").strip() or None,
                    "phone": row.get("phone", "").strip() or None,
                    "current_company": row.get("current_company", "").strip() or None,
                    "title": row.get("title", "").strip() or None,
                    "_source": "csv",
                })
    except FileNotFoundError:
        print(f"CSV file not found: {filepath}")
        return []
    return records