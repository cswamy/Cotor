import requests
import os
import pprint
import json

from dotenv import load_dotenv
from typing import List
from tenacity import retry, stop_after_attempt, wait_random_exponential
from bs4 import BeautifulSoup

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def call_github_api(url: str):
    load_dotenv()
    token = os.getenv('GITHUB_TOKEN')
    header = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'cotor.ai',
    }
    try:
        response = requests.get(url, headers=header)
    except: 
        print(f"Request failed for {url}")
    return response

def get_all_closed_issues(owner: str, repo: str) -> List[dict]:
    issues = []
    url = f'https://api.github.com/repos/{owner}/{repo}/issues?state=closed'

    while True:
        if os.path.exists(f'issues/{repo}.json'):
            break
        else: 
            response = call_github_api(url)

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

def get_issue(owner: str, repo: str, issue_number: int) -> dict:

    url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}'
    response = call_github_api(url)

    if 'pull_request' in response.json():
        print(f'[INFO] {issue_number} is a pull request. Please search for a closed issue.')
        return None

    if response.json()['state'] == 'open':
        print(f'[INFO] {issue_number} is still open. Please search for a closed issue.')
        return None

    return response.json()

def get_pull_request(issue: dict):

    html_url = issue['html_url']
    html = call_github_api(html_url).text
    
    soup = BeautifulSoup(html, 'html.parser')

    search_phrase = "Successfully merging a pull request may close this issue."
    search_element = soup.find(text=search_phrase)

    pr_number = None
    if search_element:
        next_div = search_element.find_next('div')
        if next_div:
            first_link = next_div.find('a')
            if first_link and first_link.has_attr('href'):
                if 'pull' in first_link['href']:
                    pr_number = first_link['href'].split('/')[-1]
            else:
                print("No link found")
        else:
            print("No next div found")
    else:
        print("Search phrase not found")

    return pr_number
    