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
        'Accept': 'application/vnd.github+json',
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

def get_merge_commit(owner: str, repo: str, issue: dict) -> str:

    html_url = issue['html_url']
    html = call_github_api(html_url).text
    
    soup = BeautifulSoup(html, 'html.parser')

    search_phrase = "Successfully merging a pull request may close this issue."
    search_element = soup.find(text=search_phrase)

    pr_merge_sha = None
    if search_element:
        next_div = search_element.find_next('div')
        if next_div:
            first_link = next_div.find('a')
            if first_link and first_link.has_attr('href'):
                if 'pull' in first_link['href']:
                    pr_number = first_link['href'].split('/')[-1]
                    url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}'
                    pr_details = call_github_api(url)
                    if pr_details.json()['merged'] == True:
                        pr_merge_sha = pr_details.json()['merge_commit_sha']
                    else:
                        print(f'[INFO] Pull request {pr_number} for issue {issue["number"]} was not merged to base branch.')
            else:
                print("No link found")
        else:
            print("No next div found")
    else:
        print("Search phrase not found")

    return pr_merge_sha

def get_commit_details(owner: str, repo:str, ref: str) -> dict:

    # Helper function for files with many patches
    def process_patches(patch: str) -> List[dict]:
        # split patch into lines
        lines = patch.split('\n')
        processed_patches = []
        for line in lines:
            # if line starts with @@, it's a hunk header
            # Get line number and context for new file only
            if line.startswith('@@'):
                hunk_header = line.split(' ')
                code_edit_starts = int(hunk_header[2].split(',')[0].replace('+', ''))
                code_edit_context = int(hunk_header[2].split(',')[1])
                patch_dict = {}
                patch_dict['patch_start'] = code_edit_starts
                patch_dict['context'] = code_edit_context
                processed_patches.append(patch_dict)
        return processed_patches

    url = f'https://api.github.com/repos/{owner}/{repo}/commits/{ref}'
    response = call_github_api(url)

    commit_details = {}
    json_response = response.json()
    commit_details['files_changed'] = len(json_response['files'])
    file_details = []
    for file in json_response['files']:
        file_detail = {}
        file_detail['filename'] = file['filename']
        file_detail['status'] = file['status']
        file_detail['changes'] = file['changes']
        file_detail['raw_patch'] = file['patch']
        file_detail['raw_url'] = file['raw_url']
        if file['status'] == 'added':
            file_detail['processed_patch'] = [{
                'patch_start': 1,
                'context': len(file['patch'].split('\n'))-1
            }]
        else:
            file_detail['processed_patch'] = process_patches(file['patch'])
        file_details.append(file_detail)
    
    commit_details['file_details'] = file_details
    return commit_details