import os
import utils

repo = '../../../gradio'
folders = ['gradio', 'test']
repo_folders = [f"{repo}/{folder}" for folder in folders]

# Get dataframe with repo, folder, file, raw_code
df = utils.extract_files(repo, repo_folders)

# Add embeddings to the dataframe
df = utils.add_embeddings(df)
print(df)