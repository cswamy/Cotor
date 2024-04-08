import os
import pprint
import requests
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential

# function to call github api used across all functions
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def call_github_api(url: str):
    load_dotenv()
    token = os.getenv('GITHUB_TOKEN')
    header = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'cotor.dev',
    }
    try:
        response = requests.get(url, headers=header)
    except: 
        print(f"Request failed for {url}")
    return response

# helper function to call llm
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def call_llm(payload: dict):
    url = "https://api.openai.com/v1/chat/completions"
    load_dotenv()
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
    }
    response = None
    try:
        response = requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(e)
        print(f"LLM request failed for {url}")
    return response

# Get issue from GitHub
def get_issue(owner: str, repo: str, issue_number: int) -> dict:

    url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}'
    response = call_github_api(url)

    if 'pull_request' in response.json():
        print(f'[INFO] {issue_number} is a pull request. Please search for an issue.')
        return None

    return response.json()

repo: str = "gradio"
owner: str = "gradio-app"
issue_number: int = 5180

issue = get_issue(owner, repo, issue_number)
issue_title = issue['title']
issue_body = issue['body']
if issue['comments'] > 0: 
    comments_url = issue['comments_url']
    comments = call_github_api(comments_url).json()
    issue_comments = ''
    for comment in comments:
        if comment['author_association'] in ("OWNER", "MEMBER", "COLLABORATOR"):
            issue_comments += comment['body'] + '\n'

with open('./llm_prompts/gh_system.txt', 'r') as f:
    sys_prompt = f.read()

payload = {
    "model": "gpt-4-1106-preview",
    "messages": [
        {
            "role": "system",
            "content": sys_prompt
        },
        {
            "role": "user",
            "content": f'Issue title: {issue_title}\n\nIssue body: {issue_body}\n\nIssue comments: {issue_comments}'
        }
    ],
    "temperature": 0
}

llm_response = call_llm(payload)
with open('gh_llm_response.txt', 'w') as f:
    f.write(llm_response.json()['choices'][0]['message']['content'])