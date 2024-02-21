import utils

repo_link = "https://github.com/pydantic/FastUI"
owner = repo_link.split('/')[3]
repo = repo_link.split('/')[4]
issue_number = 148

# print(f"\n[INFO] Fetching issues from repo: {repo} under owner: {owner}\n")
if issue_number is None: 
    issues = utils.get_all_closed_issues(owner, repo)
else:
    print("Here")