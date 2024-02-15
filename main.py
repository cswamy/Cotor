import argparse
import utils

from typing import List

# Parse command line arguments repo folder
# parser = argparse.ArgumentParser()
# parser.add_argument('repo', type=str, help='Name of folder containing the cloned repo')
# args = parser.parse_args()
# repo = args.repo

repo = '../gradio-cotor/gradio'
folders = ['gradio', 'test']
repo_folders = [f"{repo}/{folder}" for folder in folders]

df = utils.extract_code(repo, repo_folders)

df = utils.explain_code(df)

# print(df)
# print(df[df['file'] == 'dropdown.py']['codeData'].tolist())
for index, row in df.iterrows():
        if row['file'] == 'dataframe.py':
            for codeBlock in row['codeData']:
                print(codeBlock['code'])
                print('-'*50)
                print(codeBlock['explanation'])
                print('*'*50)