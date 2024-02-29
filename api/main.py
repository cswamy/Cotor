import datetime
import json

import utils
import pprint

# repo_link = "https://github.com/gradio-app/gradio"
repo_link = "https://github.com/pydantic/FastUI"
# repo_link = "https://github.com/cswamy/edgar"
owner = repo_link.split('/')[3]
repo = repo_link.split('/')[4]

# issue_number = 6973
issue_number = 148
# issue_number = 8

issue_details = {}
issue_details["repo"] = repo
issue_details["repo_owner"] = owner
issue_details["issue_id"] = issue_number
issue_details["created_at"] = datetime.datetime.now().isoformat()
issue_details["updated_at"] = datetime.datetime.now().isoformat()

if issue_number:
    issue = utils.get_issue(owner, repo, issue_number)
    issue_details["issue_title"] = issue['title'] 
    issue_details["issue_body"] = issue['body']

if issue is not None:
    merged_commit = utils.get_merged_commit(owner, repo, issue)
    if merged_commit['pr_merge_sha'] is not None:
        issue_details["merged_pr_id"] = merged_commit['pr_number']
        commit_details = utils.get_commit_details(owner, repo, merged_commit['pr_merge_sha'])
        if len(commit_details['file_details']) == commit_details['files_changed']:
            utils.add_patch_explains(commit_details, issue)
            issue_details["commit_details"] = commit_details
            utils.upload_supabase(issue_details)