import requests
import os
import pprint
import json
import supabase

from dotenv import load_dotenv
from typing import List, Tuple
from tenacity import retry, stop_after_attempt, wait_random_exponential
from bs4 import BeautifulSoup

# function to call github api used across all functions
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def call_github_api(url: str):
    load_dotenv()
    token = os.getenv('GITHUB_TOKEN')
    header = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'cotorai.com',
    }
    try:
        response = requests.get(url, headers=header)
    except: 
        print(f"Request failed for {url}")
    return response

# helper function to call llm
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def call_llm(payload: dict):
    # url = "https://api.perplexity.ai/chat/completions"
    url = "https://api.openai.com/v1/chat/completions"
    load_dotenv()
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
    }
    response = requests.post(url, json=payload, headers=headers)
    return response

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

def get_merged_commit(owner: str, repo: str, issue: dict) -> Tuple[str, str]:

    html_url = issue['html_url']
    html = call_github_api(html_url).text
    
    soup = BeautifulSoup(html, 'html.parser')

    search_phrase = "Successfully merging a pull request may close this issue."
    search_element = soup.find(text=search_phrase)

    merged_commit = {
        'pr_number': None,
        'pr_merge_sha': None,
    }
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
                        merged_commit['pr_number'] = pr_number
                        merged_commit['pr_merge_sha'] = pr_details.json()['merge_commit_sha']
                    else:
                        print(f'[INFO] Pull request {pr_number} for issue {issue["number"]} was not merged to base branch.')
            else:
                print("No link found")
        else:
            print("No next div found")
    else:
        print("Search phrase not found")

    return merged_commit

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

def add_patch_explains(commit_details: dict, issue: dict) -> None:

    with open('./llm_prompts/patch_explain.txt', 'r') as f:
        patch_prompt_str = f.read()
        patch_prompt_str = patch_prompt_str + issue['title'] + "\n" + issue['body']

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
        file['patch_explains'] = response.json()['choices'][0]['message']['content']

def upload_supabase(data_dict: dict) -> None:
    
    load_dotenv()
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    supabase_table = os.getenv('SUPABASE_TABLE')
    supabase_client = supabase.create_client(supabase_url, supabase_key)

    try:
        response = supabase_client.table(supabase_table).upsert(data_dict).execute()
    except Exception as e:
        print(f"[ERROR] Uploading to Supabase: {e}")