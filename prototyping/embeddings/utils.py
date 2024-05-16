import os
import pandas as pd
import requests
import torch
import ast

from typing import List
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential
from torch.nn.functional import cosine_similarity
from tqdm.auto import tqdm

# helper function to call llm
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def call_llm(url: str, payload: dict):
    load_dotenv()
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
    }
    payload["model"] = os.getenv("LLM_MODEL")
    response = None
    try:
        response = requests.post(url, json=payload, headers=headers)
    except:
        print(f"LLM request failed for {url}")
    return response

# helper function to call github api
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def call_github_api(url: str):
    load_dotenv()
    token = os.getenv('GITHUB_TOKEN')
    header = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'cotor.dev',
    }
    response = None
    try:
        response = requests.get(url, headers=header)
    except: 
        print(f"Request failed for {url}")
    return response

def extract_repo_files(repo: str, repo_folders: List[str]) -> pd.DataFrame: 
    """
    Builds a pandas dataframe with files and code from a repo
    Args:
    - repo: str, name of the repo
    - repo_folders: str, folders in the repo to extract files from
    Returns:
    - df: pd.DataFrame, pandas dataframe with ['repo', 'folder', 'file', 'raw_code']
    """
    df = pd.DataFrame(columns=['repo', 'folder', 'file', 'raw_code', 'embedding'])
    for folder in repo_folders:
        for root, dirs, files in os.walk(folder):
            for file in files:
                #if file in ['dataframe.py']:
                try: 
                    with open(f"{root}/{file}", 'r') as f:
                        source_code = f.read()
                        if source_code == '':
                            continue
                        new_row = pd.DataFrame({
                            'repo': [repo], 
                            'folder': [root], 
                            'file': [file],
                            'raw_code': [source_code]
                        })
                        df = pd.concat([df, new_row], ignore_index=True)
                except:
                    continue
    return df

def add_repo_embeddings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds embeddings to a pandas dataframe
    Args:
    - df: pd.DataFrame, pandas dataframe with ['repo', 'folder', 'file', 'raw_code']
    Returns:
    - df: pd.DataFrame, pandas dataframe with ['repo', 'folder', 'file', 'raw_code', 'embedding']
    """
    url = "https://api.openai.com/v1/embeddings"
    for index, row in tqdm(df.iterrows()):
        print(f"Processing row {index+1} of {len(df)}")
        payload = {
            #"input": row['file'] + '\n' + row['raw_code'],
            "input": row['folder'] + row['file'],
        }
        response = call_llm(url, payload)
        if response is not None and 'data' in response.json():
            embedding = response.json()['data'][0]['embedding']
            df['embedding'][index] = embedding

    return df

def get_issue_embed(repo_link: str, issue: int) -> List:
    """
    Get embeddings for an issue title, body and comments
    Args:
    - repo_link: str, link to the repo
    - issue: int, issue number
    Returns:
    - issue_embed: List, embeddings for issue title, body and comments
    """
    owner = repo_link.split('/')[3]
    repo = repo_link.split('/')[4]
    gh_url = url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue}'
    gh_response = call_github_api(gh_url)

    issue_embed = []
    if gh_response is not None:
        issue = gh_response.json()
        issue_text = issue['title'] + issue['body']
        if issue['comments'] > 0:
            comments = call_github_api(gh_url + '/comments')
            if comments is not None: 
                comments = comments.json()
                for comment in comments:
                    if comment['author_association'] in ['OWNER', 'MEMBER', 'CONTRIBUTOR']:
                        issue_text += comment['body']
        payload = {
            "input": issue_text,
        }
        llm_url = "https://api.openai.com/v1/embeddings"
        llm_response = call_llm(llm_url, payload)
        if llm_response is not None:
            issue_embed = llm_response.json()['data'][0]['embedding']

    return issue_embed

def get_candidate_files(df: pd.DataFrame, issue_embed: List) -> List:
    """
    Get candidate files based on cosine similarity
    Args:
    - df: pd.DataFrame, pandas dataframe with ['repo', 'folder', 'file', 'raw_code', 'embedding']
    - issue_embed: List, embeddings for issue title, body and comments
    Returns:
    - files: List, candidate files based on cosine similarity
    """
    repo_embeddings = []
    for index, row in df.iterrows():
        if row['embedding'] is not None:
            try:
                embedding = torch.tensor(ast.literal_eval(row['embedding'])).unsqueeze(0)
                repo_embeddings.append(embedding)
            except:
                continue
    
    issue_embed = torch.tensor(issue_embed).unsqueeze(0)
    similarities = [cosine_similarity(issue_embed, file_embed) for file_embed in repo_embeddings]
    files = []
    top_indices = torch.argsort(torch.cat(similarities, dim=0), descending=True)[:10].tolist()
    for idx in top_indices:
        files.append({
            'folder': df['folder'][idx],
            'file': df['file'][idx]
            })
    return files