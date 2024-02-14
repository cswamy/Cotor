import os
import ast
import pandas as pd
from typing import List

def extract_code (repo: str, repo_folders: List[str]) -> pd.DataFrame:

    df = pd.DataFrame(columns=['repo', 'folder', 'file', 'code'])
    # Start going through the repo folders
    for folder in repo_folders:
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith('.py'):
                    # Add row to dataframe
                    new_row = pd.DataFrame({'repo': [repo], 'folder': [root], 'file': [file]})
                    # Use ast to parse the file
                    # if file == 'dataframe.py':
                    with open(f"{root}/{file}", 'r') as f:
                        source_code = f.read()
                        f.seek(0)
                        all_lines = f.readlines()
                        tree = ast.parse(source_code)
                        # Get the last line number before first function or class
                        setupCodeStartLineno = setupCodeEndLineno = 0
                        for node in ast.iter_child_nodes(tree):
                            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                                break
                            setupCodeEndLineno = node.end_lineno
                        # Extract setup code
                        setupCode = ''.join(all_lines[:setupCodeEndLineno])
                        # Get main code blocks and metadata
                        codeBlocks = []
                        codeBlocks.append({
                            'codeType': 'setup',
                            'name': 'n/a',
                            'startLineno': 0,
                            'endLineno': setupCodeEndLineno,
                            'code': setupCode
                        })
                        for node in ast.iter_child_nodes(tree):
                            if node.lineno > setupCodeEndLineno:
                                startLineno = node.lineno
                                endLineno = node.end_lineno
                                codeBlock = ''.join(all_lines[startLineno-1:endLineno])
                                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                    codeBlockType = 'function'
                                    codeBlockName = node.name
                                elif isinstance(node, (ast.ClassDef)):
                                    codeBlockType = 'class'
                                    codeBlockName = node.name
                                else: 
                                    codeBlockType = 'other'
                                    codeBlockName = 'n/a'
                                #print(f"CodeBlock: {codeBlockType}, Name: {codeBlockName}, Start: {startLineno}, End: {endLineno}")
                                codeBlocks.append({
                                    'codeType': codeBlockType,
                                    'name': codeBlockName,
                                    'startLineno': startLineno,
                                    'endLineno': endLineno,
                                    'code': codeBlock
                                })
                            # Add codeBlocks to new_row
                            new_row['code'] = [codeBlocks]
                    df = pd.concat([df, new_row], ignore_index=True)
    return df