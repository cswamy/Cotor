import requests
import os
import pprint
import json

from dotenv import load_dotenv
from typing import List

def get_all_closed_issues(owner: str, repo: str) -> List[dict]:
    issues = []
    url = f'https://api.github.com/repos/{owner}/{repo}/issues?state=closed'
    load_dotenv()
    token = os.getenv('GITHUB_TOKEN')
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'cotor.ai',
    }

    while True:
        if os.path.exists(f'issues/{repo}.json'):
            break
        else: 
            response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f'[ERROR] Failed to fetch issues: {response.status_code} {response.reason} {response.text}')
            break

        # Filter out pull requests and add current batch of issues to the list
        issues += [issue for issue in response.json() if 'pull_request' not in issue]

        # Check if there is a next page, if not, break loop
        if 'next' not in response.links:
            break

        # Update URL for next page
        url = response.links['next']['url']
    
    # Write issues to json file
    if os.path.exists(f'issues/{repo}.json'):
        print(f'[INFO] File already exists: issues/{repo}.json')
    else:
        print(f"[INFO] Writing {len(issues)} issues to file...")
        with open(f'issues/{repo}.json', 'w') as f:
            json.dump(issues, f, indent=4)

    return issues