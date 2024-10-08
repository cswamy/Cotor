import requests
import os
import json

from dotenv import load_dotenv
from typing import List, Tuple
from tenacity import retry, stop_after_attempt, wait_random_exponential
from bs4 import BeautifulSoup

# function to call github api used across all functions
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def call_github_api(url: str, token: str):
    header = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'cotor.dev',
    }
    response = None
    try:
        response = requests.get(url, headers=header)
    except: 
        print(f"Github request failed for {url}")
    return response

# helper function to call llm
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def call_llm(payload: dict):
    url = "https://api.openai.com/v1/chat/completions"
    load_dotenv()
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        # "authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
    }
    response = None
    try:
        response = requests.post(url, json=payload, headers=headers)
    except:
        print(f"LLM request failed for {url}")
    return response

def get_merged_commit(
    owner: str, 
    repo: str, 
    issue: int,
    issue_url: str,
    is_pull_request: bool, 
    token: str) -> dict:

    merged_commit = {
        'pr_number': None,
        'pr_merge_sha': None,
    }

    # Logic if issue is a PR
    if is_pull_request:
        url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{issue}'
        pr_details = call_github_api(url, token)
        pr_json = pr_details.json()
        if pr_json['merged'] == True:
            merged_commit['pr_number'] = issue
            merged_commit['pr_merge_sha'] = pr_json['merge_commit_sha']
        # PR status is closed instead of merged. Label Merged added instead
        elif any(label.get('name') == 'Merged' for label in pr_json.get('labels', [])):
            merged_commit['pr_number'] = issue
            merged_commit['pr_merge_sha'] = pr_json['merge_commit_sha']
    # Logic if issue is not a PR
    else:
        html = call_github_api(issue_url, token).text
        soup = BeautifulSoup(html, 'html.parser')
        pr_link = None

        # Side bar strategy (primary approach)
        search_phrase = "Successfully merging a pull request may close this issue."
        search_element = soup.find(text=search_phrase)
        if search_element:
            next_div = search_element.find_next('div')
            if next_div:
                pr_link = next_div.find('a')
        else:
            # Comments strategy
            span = soup.find('span', title='Status: Merged')
            if span:
                parent_div = span.find_parent('div')
                previous_div = parent_div.find_previous_sibling('div')
                if previous_div:
                    pr_link = previous_div.find('a')

        if pr_link is not None:
            if pr_link.has_attr('href'):
                if 'pull' in pr_link['href']:
                    pr_number = pr_link['href'].split('/')[-1]
                    url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}'
                    pr_details = call_github_api(url, token)
                    pr_json = pr_details.json()
                    if pr_json['merged'] == True:
                        merged_commit['pr_number'] = pr_number
                        merged_commit['pr_merge_sha'] = pr_json['merge_commit_sha']
                    # PR status is closed instead of merged. Label Merged added instead
                    elif any(label.get('name') == 'Merged' for label in pr_json.get('labels', [])):
                        merged_commit['pr_number'] = pr_number
                        merged_commit['pr_merge_sha'] = pr_json['merge_commit_sha']

    return merged_commit

def get_commit_details(owner: str, repo:str, ref: str, token: str) -> dict:

    # Helper function for files with many patches
    def process_patches(patch: str) -> List:
        # split patch into lines
        lines = patch.split('\n')
        processed_patches = []
        for line in lines:
            # if line starts with @@, it's a hunk header
            # Get line number and context for new file only
            try:
                if line.startswith('@@'):
                    hunk_header = line.split(' ')
                    code_edit_starts = int(hunk_header[2].split(',')[0].replace('+', ''))
                    code_edit_context = int(hunk_header[2].split(',')[1])
                    patch_list = range(code_edit_starts, code_edit_starts + code_edit_context)
                    processed_patches.extend(patch_list)
            except:
                return list(range(1, len(patch.split('\n'))))
        return processed_patches

    url = f'https://api.github.com/repos/{owner}/{repo}/commits/{ref}'
    response = call_github_api(url, token)

    commit_details = {}
    json_response = response.json()
    commit_details['files_changed'] = len(json_response['files'])
    file_details = []
    for file in json_response['files']:
        file_detail = {}
        file_detail['filename'] = file['filename']
        file_detail['status'] = file['status']
        file_detail['changes'] = file['changes']
        file_detail['raw_url'] = file['raw_url']
        # Some changes might not come with a patch
        if 'patch' in file:
            file_detail['raw_patch'] = file['patch']
            # Get raw code
            html = call_github_api(file['raw_url'], token).text
            if html:
                file_detail['raw_code'] = html
            else: 
                file_detail['raw_code'] = f"Couldn't fetch code from {file['raw_url']}"
            if file['status'] == 'added':
                file_detail['processed_patch'] = list(range(
                    1, len(file['patch'].split('\n'))
                ))
            else:
                file_detail['processed_patch'] = process_patches(file['patch'])
        else:
            file_detail['raw_patch'] = f"No code changes were made in {file['filename']}."
            file_detail['raw_code'] = f"No code changes were made in {file['filename']}."
        file_details.append(file_detail)
    
    commit_details['file_details'] = file_details
    return commit_details

def add_patch_explains(commit_details: dict, issue_title: str, issue_body: str) -> None:

    with open('./llm_prompts/patch_explain.txt', 'r') as f:
        patch_prompt_str = f.read()
        patch_prompt_str = patch_prompt_str + issue_title + "\n" + issue_body

    for file in commit_details['file_details']:
        payload = {
            "model": "gpt-4-1106-preview",
            "messages": [
                {
                    "role": "system",
                    "content": patch_prompt_str
                },
                {
                    "role": "user",
                    "content": file['raw_patch']
                }],
                "temperature": 0,
        }
        response = call_llm(payload)
        file['patch_explains'] = "Please try again"
        if response is not None:
            json_response = response.json()
            if 'choices' in json_response:
                file['patch_explains'] = json_response['choices'][0]['message']['content']
            