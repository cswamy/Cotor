import os
import utils
import pandas as pd
import argparse
import pprint

repo = '../../../gradio'
repo_link = 'https://github.com/gradio-app/gradio'
folders = ['gradio', 'test']
repo_folders = [f"{repo}/{folder}" for folder in folders]
issue = 6973

parser = argparse.ArgumentParser()
parser.add_argument('--embeds', type=str, default=None)
parser.add_argument('--get_embeds', type=bool, default=False)
args = parser.parse_args()
args.get_embeds = bool(args.get_embeds)

if args.embeds is not None and os.path.exists(args.embeds):
    df = pd.read_csv(args.embeds)
    args.get_embeds = False

else:
    if args.get_embeds == False:
        print(f'[INFO] No embedding file. Please confirm running embeddings with "--get_embeds True"')
        exit()

    else:
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
    pprint.pprint(files)