import argparse
from extractor import extract_code

# Parse command line arguments repo folder
# parser = argparse.ArgumentParser()
# parser.add_argument('repo', type=str, help='Name of folder containing the cloned repo')
# args = parser.parse_args()
# repo = args.repo

repo = '../gradio-cotor/gradio'
folders = ['gradio', 'test']
repo_folders = [f"{repo}/{folder}" for folder in folders]

df = extract_code(repo, repo_folders)

# print(df)
# print(df[df['file'] == 'dataframe.py']['code'].tolist()[0][0]['code'])