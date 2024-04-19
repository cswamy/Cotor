import os
import argparse
import pandas as pd
import utils
import pprint

parser = argparse.ArgumentParser()
parser.add_argument('--embeds', type=str, required=True, help='Name of the file with stored embeddings')
args = parser.parse_args()

repo_link = 'https://github.com/gradio-app/gradio'
issue = 6973

if not os.path.exists(args.embeds):
    print("File does not exist")
else:
    df = pd.read_csv(args.embeds)

    # Get embedding for issue title, body and comments
    issue_embed = utils.get_issue_embed(repo_link, issue)
    
    # Get candidate files based on cosine similarity
    if len(issue_embed) > 0: 
        files = utils.get_candidate_files(df, issue_embed)
        pprint.pprint(files)
