import json
from parsers.csv_parser import parse_csv
from merge import merge_all
from project import project

csv_records = parse_csv("../sample_inputs/recruiter_export.csv")
profiles = merge_all(csv_records)

with open("../sample_inputs/config_default.json") as f:
    config = json.load(f)

result = project(profiles[0], config)
print(json.dumps(result, indent=2))