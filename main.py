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

df = pd.DataFrame(columns=['repo', 'folder', 'file', 'top_lines'])
# Start going through the repo folders
for folder in repo_folders:
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith('.py'):
                # Add row to dataframe
                new_row = pd.DataFrame({'repo': [repo], 'folder': [root], 'file': [file]})
                # Use ast to parse the file
                if file == 'dataframe.py':
                    with open(f"{root}/{file}", 'r') as f:
                        source_code = f.read()
                        f.seek(0)
                        all_lines = f.readlines()
                        tree = ast.parse(source_code)
                        # Get the last line number before first function or class
                        top_content_end_lineno = 0
                        for node in ast.iter_child_nodes(tree):
                            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                                break
                            top_content_end_lineno = node.end_lineno
                        # Go back to beginning of file and extract lines up to end_lineno
                        top_lines = all_lines[:top_content_end_lineno]
                        top_lines_str = ''.join(top_lines)
                        new_row.loc[0, 'top_lines'] = top_lines_str
                        # Get rest of contents of file
                        for node in ast.iter_child_nodes(tree):
                            if node.lineno > top_content_end_lineno:
                                print(f"Node: {type(node).__name__}, Lineno: {node.lineno}, endLineno: {node.end_lineno}")
                                # start_lineno = node.lineno
                                # end_lineno = node.end_lineno
                                # snippet = all_lines[start_lineno-1:end_lineno]
                # df = pd.concat([df, new_row], ignore_index=True)

# write df to file
# with open('files.csv', 'w') as f:
#    df.to_csv(f, index=False)
