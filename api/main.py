import utils
import json
import datetime

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_headers=["*"],
)

@app.get("/validateinputs/{owner}/{repo}")
def validate_inputs(
    owner: str, 
    repo: str, 
    issue: int,
    authorization: str = Header(None)) -> dict:
    response = {
        "repo_exists": False,
        "issue_exists": False,
        "issue_status": None,
        "issue_url": None,
        "issue_title": None,
        "issue_body": None,
        "is_pull_request": False,
    }

    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = authorization.split(" ")[1]
    
    repo_url = f'https://api.github.com/repos/{owner}/{repo}'
    repo_response = utils.call_github_api(repo_url, token)

    issue_url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue}'
    issue_response = utils.call_github_api(issue_url, token)
    
    if repo_response.status_code == 200:
        response['repo_exists'] = True
    if issue_response.status_code == 200:
        if issue_response.json()['state'] == 'closed':
            response['issue_exists'] = True
            response['issue_status'] = 'closed'
            response['issue_url'] = issue_response.json()['html_url']
            response['issue_title'] = issue_response.json()['title']
            # response['issue_body'] = issue_response.json()['body']
            response['issue_body'] = None
            # Check if issue is actually a PR
            if 'pull_request' in issue_response.json():
                response['is_pull_request'] = True
                response['issue_body'] = None
            # Check if issue was closed without PR
            merged_commit = utils.get_merged_commit(owner, repo, issue, response['issue_url'], response['is_pull_request'], token)
            if merged_commit['pr_number'] is None or merged_commit['pr_merge_sha'] is None:
                if response['is_pull_request']:
                    response['issue_status'] = 'pr_closed_without_merge'
                else:
                    response['issue_status'] = 'issue_closed_without_pr'
        else:
            if 'pull_request' in issue_response.json():
                response['is_pull_request'] = True
                response['issue_body'] = None
            response['issue_exists'] = True
            response['issue_status'] = 'open'
    
    return response

    
@app.get("/researchissue")
def research_issue(
    owner: str, 
    repo: str, 
    issue: int, 
    issue_url: str,
    issue_title: str,
    is_pull_request: bool,
    issue_body: str = '',
    authorization: str = Header(None)) -> dict:

    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = authorization.split(" ")[1]
    
    response = {}
    response['repo'] = repo
    response['repo_owner'] = owner
    response['issue_id'] = issue
    response['issue_title'] = issue_title
    response['issue_body'] = issue_body
    response['issue_url'] = issue_url
    response['is_pull_request'] = is_pull_request
    response['created_at'] = datetime.datetime.now().isoformat()
    response['updated_at'] = datetime.datetime.now().isoformat()

    merged_commit = utils.get_merged_commit(owner, repo, issue, issue_url, is_pull_request, token)
    if merged_commit['pr_merge_sha'] is not None:
        response['merged_pr_id'] = merged_commit['pr_number']
        commit_details = utils.get_commit_details(owner, repo, merged_commit['pr_merge_sha'], token)
        if len(commit_details['file_details']) == commit_details['files_changed']:
            utils.add_patch_explains(commit_details, issue_title, issue_body)
            response['commit_details'] = commit_details

    return response
