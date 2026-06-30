import argparse
import json
import os
from parsers.csv_parser import parse_csv
from merge import merge_all
from project import project

def run_pipeline(inputs_dir: str, config_path: str, output_path: str):
    all_records = []

    csv_path = os.path.join(inputs_dir, "recruiter_export.csv")
    if os.path.exists(csv_path):
        all_records.extend(parse_csv(csv_path))

    github_list_path = os.path.join(inputs_dir, "github_usernames.txt")
    if os.path.exists(github_list_path):
        from parsers.github_parser import parse_github
        with open(github_list_path) as f:
            for line in f:
                username = line.strip()
                if username:
                    result = parse_github(username)
                    if result:
                        all_records.append(result)

    profiles = merge_all(all_records)

    with open(config_path) as f:
        config = json.load(f)

    output = [project(p, config) for p in profiles]

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Processed {len(profiles)} candidates -> {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Source Candidate Data Transformer")
    parser.add_argument("--inputs", required=True, help="Directory containing input source files")
    parser.add_argument("--config", required=True, help="Path to runtime output config JSON")
    parser.add_argument("--out", required=True, help="Path to write output JSON")
    args = parser.parse_args()

    run_pipeline(args.inputs, args.config, args.out)