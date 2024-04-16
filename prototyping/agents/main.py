import os
import utils
import pandas as pd

repo = '../../../gradio'
repo_link = 'https://github.com/gradio-app/gradio'
folders = ['gradio', 'test']
repo_folders = [f"{repo}/{folder}" for folder in folders]
issue = 6973

if not os.path.exists('embedding.csv'):
    # Get dataframe with repo, folder, file, raw_code
    df = utils.extract_repo_files(repo, repo_folders)

    # Add embeddings to the dataframe
    df = utils.add_repo_embeddings(df)

    # Write dataframe to csv
    with open('embedding.csv', 'w') as f:
        df.to_csv(f, index=False)

# Read dataframe from csv
df = pd.read_csv('embedding.csv')

# Get embedding for GitHub issue title, body and comments
issue_embed = utils.get_issue_embed(repo_link, issue)

# Get candidate files based on cosine similarity
if len(issue_embed) > 0: 
    files = utils.get_candidate_files(df, issue_embed)
    print(files)