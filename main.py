import os
import ast
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

df = pd.DataFrame(columns=['repo', 'folder', 'file'])
# Start going through the repo folders
for folder in repo_folders:
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith('.py'):
                # Add row to dataframe
                new_row = pd.DataFrame({'repo': [repo], 'folder': [root], 'file': [file]})
                df = pd.concat([df, new_row], ignore_index=True)
                # Use ast to parse the file
                if file == 'dataframe.py':
                    with open(f"{root}/{file}", 'r') as f:
                        source_code = f.read()
                        tree = ast.parse(source_code)
                        # Get the last line number before first function or class
                        end_lineno = 0
                        for node in ast.iter_child_nodes(tree):
                            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                                break
                            end_lineno = node.end_lineno
                        # Go back to beginning of file and extract lines up to end_lineno
                        f.seek(0)
                        top_lines = f.readlines()[:end_lineno]
                        print(''.join(top_lines))
