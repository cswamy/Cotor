import os
import utils
import pandas as pd
import pprint

repo_link = 'https://github.com/gradio-app/gradio'
repo = '../../../gradio'
folders = ['gradio', 'test']
repo_folders = [f"{repo}/{folder}" for folder in folders]

# Get dataframe with repo, folder, file, raw_code
df = utils.extract_repo_files(repo, repo_folders)

# Get summaries for each file
df = utils.add_code_summary(df)

# Get embeddings for code summaries
df = utils.add_embeddings(df)

# Upload dataframe to supabase
utils.upload_to_supabase(df)

# Write dataframe to csv
#with open('embedding.csv', 'w') as f:
#    df.to_csv(f, index=False)

# Read dataframe from csv
#df = pd.read_csv('embedding.csv')

# Get embedding for GitHub issue title, body and comments
#issue_embed = utils.get_issue_embed(repo_link, issue)

# Get candidate files based on cosine similarity
#if len(issue_embed) > 0: 
#    files = utils.get_candidate_files(df, issue_embed)
#    pprint.pprint(files)