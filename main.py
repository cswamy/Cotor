import os
import argparse
import pandas as pd

# Parse command line arguments repo folder
# parser = argparse.ArgumentParser()
# parser.add_argument('repo', type=str, help='Name of folder containing the cloned repo')
# args = parser.parse_args()
# repo = args.repo

repo = '../gradio-cotor/gradio'
folders = ['gradio', 'test']
repo_folders = [f"{repo}/{folder}" for folder in folders]

df = pd.DataFrame(columns=['repo', 'folder', 'filename'])
# Start going through the repo folders
for folder in repo_folders:
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith('.py'):
                new_row = pd.DataFrame({'repo': [repo], 'folder': [root], 'filename': [file]})
                df = pd.concat([df, new_row], ignore_index=True)
                # add to pandas dataframe

# Write dataframe to txt file
df.to_csv('files.csv', index=False)
