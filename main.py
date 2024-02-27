import utils
import pprint

repo_link = "https://github.com/gradio-app/gradio"
# repo_link = "https://github.com/pydantic/FastUI"
# repo_link = "https://github.com/cswamy/edgar"
owner = repo_link.split('/')[3]
repo = repo_link.split('/')[4]

issue_number = 6973
# issue_number = 148
# issue_number = 8

if issue_number:
    issue = utils.get_issue(owner, repo, issue_number)

if issue is not None:
    pr_merge_sha = utils.get_merge_commit(owner, repo, issue)
    if pr_merge_sha is not None:
        commit_details = utils.get_commit_details(owner, repo, pr_merge_sha)
        if len(commit_details['file_details']) == commit_details['files_changed']:
            utils.add_patch_explains(commit_details, issue)
            pprint.pprint(commit_details)