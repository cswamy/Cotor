import utils
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
)

@app.get("/validateinputs/{owner}/{repo}")
def validate_inputs(owner: str, repo: str, issue: int) -> dict:
    response = {
        "repo_exists": False,
        "issue_exists": False,
        "issue_status": None,  
    }
    
    repo_url = f'https://api.github.com/repos/{owner}/{repo}'
    repo_response = utils.call_github_api(repo_url)

    issue_url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue}'
    issue_response = utils.call_github_api(issue_url)
    
    if repo_response.status_code == 200:
        response['repo_exists'] = True
    if issue_response.status_code == 200:
        if issue_response.json()['state'] == 'closed':
            response['issue_exists'] = True
            response['issue_status'] = 'closed'
        else:
            response['issue_exists'] = True
            response['issue_status'] = 'open'
    
    return response

    