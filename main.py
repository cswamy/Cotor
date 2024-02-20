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

run_llm = False
if run_llm:
    df = utils.explain_code(df)
    with open('./outputs/line_plot.txt', 'w') as f:
        for index, row in df.iterrows():
            if row['file'] == 'line_plot.py':
                for codeBlock in row['codeData']:
                    f.write(str(codeBlock['code']) + '\n')
                    f.write('-'*50 + '\n')
                    f.write(str(codeBlock['explanation']) + '\n')
                    f.write('*'*50 + '\n')
else: 
    print(f"Set run_llm to True to call LLM. Current value: {run_llm}")