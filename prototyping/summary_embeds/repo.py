import os
import utils
import pandas as pd
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--embeds', type=str, required=True, help='Name of the file to save the embeddings')
args = parser.parse_args()

repo_link = 'https://github.com/gradio-app/gradio'
repo = '../../../gradio'
folders = ['gradio/components']
repo_folders = [f"{repo}/{folder}" for folder in folders]

# Prevent OS from sleeping
caffeinate_process = subprocess.Popen(['caffeinate', "-i"])

# Get dataframe with repo, folder, file, raw_code
df = utils.extract_repo_files(repo, repo_folders)

# Get summaries for each file
df = utils.add_code_summary(df)

# Get embeddings for code summaries
df = utils.add_embeddings(df)

# Upload dataframe to supabase
# utils.upload_to_supabase(df)

# Write dataframe to csv
with open(f'{args.embeds}', 'w') as f:
    df.to_csv(f, index=False)

# Kill caffeinate process
if caffeinate_process.poll() is None:
    caffeinate_process.terminate()