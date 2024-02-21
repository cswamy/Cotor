import os
import ast
import pandas as pd
import requests

from tenacity import retry, stop_after_attempt, wait_random_exponential
from dotenv import load_dotenv
from typing import List

def extract_code (repo: str, repo_folders: List[str]) -> pd.DataFrame:
    """
    Extracts code from a list of folders in a repo and returns a dataframe with the code and metadata
    Args:
    - repo: str, name of the repo
    - repo_folders: List[str], list of folders in the repo to extract code from
    Returns:
    - df: pd.DataFrame, pandas dataframe with the code and metadata
    """

    df = pd.DataFrame(columns=['repo', 'folder', 'file', 'codeData'])
    # Start going through the repo folders
    codeBlockID = 0
    for folder in repo_folders:
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith('.py'):
                    # Add row to dataframe
                    new_row = pd.DataFrame({'repo': [repo], 'folder': [root], 'file': [file]})
                    # Use ast to parse the file
                    with open(f"{root}/{file}", 'r') as f:
                        source_code = f.read()
                        # Handle empty files
                        if source_code == '':
                            continue
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
                        # Get setup code block and metadata
                        codeBlocks = []
                        codeBlockID += 1
                        codeBlocks.append({
                            'codeBlockID': codeBlockID,
                            'codeType': 'setup',
                            'name': 'n/a',
                            'startLineno': 0,
                            'endLineno': setupCodeEndLineno,
                            'code': setupCode
                        })
                        # Get all other code blocks
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
                                codeBlockID += 1
                                codeBlocks.append({
                                    'codeBlockID': codeBlockID,
                                    'codeType': codeBlockType,
                                    'name': codeBlockName,
                                    'startLineno': startLineno,
                                    'endLineno': endLineno,
                                    'code': codeBlock
                                })
                            # Add codeBlocks to new_row
                            new_row['codeData'] = [codeBlocks]
                    df = pd.concat([df, new_row], ignore_index=True)
    return df

def explain_code (df: pd.DataFrame) -> pd.DataFrame:
    """
    Uses an LLM to generate explanations for the code blocks
    Args:
    - df: pd.DataFrame, pandas dataframe with the code and metadata
    Returns:
    - df: pd.DataFrame, pandas dataframe with explains added to code and metadata
    """
    
    url = "https://api.perplexity.ai/chat/completions"

    load_dotenv()
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
    } 

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def call_llm(url: str, payload: dict, headers: dict):
        """
        Helper function to call LLMs with exponential backoff
        """
        response = requests.post(url, json=payload, headers=headers)
        return response

    for index, row in df.iterrows():
        if row['file'] == 'line_plot.py':
            for codeBlock in row['codeData']:
                payload = {
                    "model": "codellama-34b-instruct",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Be precise and concise. You are a teacher explaining code to a student."
                        },
                        {
                            "role": "user",
                            "content": codeBlock['code']
                        }
                    ],
                    "temperature": 0,
                }
                response = call_llm(url, payload, headers)

                # print(codeBlock['code'])
                # print("-"*80)
                # print(f"{response.json()['choices'][0]['message']['content']}\n\n")

                # add new field text to codeBlock
                codeBlock['explanation'] = response.json()['choices'][0]['message']['content']
    return df