import requests
from typing import Dict, Optional


def parse_github(username: str) -> Optional[Dict]:
    """
    Fetches a public GitHub profile and returns raw extracted fields.
    Returns None (never raises) if the user doesn't exist, the API fails,
    or we get rate-limited — so one bad source never crashes the pipeline.
    """
    url = f"https://api.github.com/users/{username}"
    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as e:
        print(f"GitHub request failed for '{username}': {e}")
        return None

    if response.status_code == 404:
        print(f"GitHub user not found: {username}")
        return None

    if response.status_code != 200:
        print(f"GitHub API returned {response.status_code} for '{username}'")
        return None

    data = response.json()

    return {
        "full_name": data.get("name") or None,
        "headline": data.get("bio") or None,
        "github_url": data.get("html_url") or None,
        "location": data.get("location") or None,
        "public_repos": data.get("public_repos"),
        "_source": "github",
    }