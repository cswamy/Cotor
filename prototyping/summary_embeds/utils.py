import os
import pandas as pd
import requests
import supabase
import torch
import ast
import time

from typing import List
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed, wait_random_exponential, retry_if_exception_type
from tqdm.auto import tqdm
from torch import cosine_similarity

class StatusCodeError(Exception):
    pass

# helper function to call llm
@retry(retry=retry_if_exception_type(StatusCodeError), wait=wait_fixed(60), stop=stop_after_attempt(6))
def call_llm(service: str, url: str, payload: dict):
    
    load_dotenv()
    if service == 'anthropic':
        headers = {
            "content-type": "application/json",
            "x-api-key": os.getenv('ANTHROPIC_API_KEY'),
            "anthropic-version": "2023-06-01",
        }
        payload["model"] = "claude-3-haiku-20240307"
        payload["max_tokens"] = 2032
        payload["temperature"] = 0
    elif service == 'openai':
        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        }
    elif service == 'groq':
        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        }
        #payload["model"] = "llama3-8b-8192"
        payload["model"] = "mixtral-8x7b-32768"
        payload["max_tokens"] = 2032
        payload["temperature"] = 0
    
    response = None
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise StatusCodeError(f"{service} request failure {response.text}. Retrying...")
    except StatusCodeError as e:
        print(e)
        raise
    
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
    df = pd.DataFrame(columns=['repo', 'folder', 'file', 'raw_code', 'llm_summary', 'summary_embed'])
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

def add_code_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds llm generated summaries for each file in repo 
    Args:
    - df: pd.DataFrame, pandas dataframe with ['repo', 'folder', 'file', 'raw_code', 'llm_summary', 'summary_embed']
    Returns:
    - df: pd.DataFrame, pandas dataframe with ['repo', 'folder', 'file', 'raw_code', 'llm_summary', 'summary_embed']
    """
    ### Anthropic test code below ###
    #service = "anthropic"
    #url = "https://api.anthropic.com/v1/messages"
    #for index, row in tqdm(df.iterrows()):
    #    print(f"Adding summary for row {index+1} of {len(df)}")
    #    payload = {
    #        "system": "Be precise and concise. Generate an explanation for code below.",
    #        "messages": [
    #            {
    #                "role": "user",
    #                "content": row['raw_code']
    #            }
    #        ]
    #    }
    #    response = call_llm(service, url, payload)
    #    if response is not None and "content" in response.json():
    #        df['llm_summary'][index] = response.json()['content'][0]['text']
    #    else:
    #        print(f"[ERROR] Adding summary failed for file: {row['file']}")
    #    # Pause execution for 60 seconds to avoid rate limiting
    #    time.sleep(60)
    #return df

    ### Groq test code below ###
    #service = "groq"
    #url = "https://api.groq.com/openai/v1/chat/completions"
    #for index, row in tqdm(df.iterrows()):
    #    print(f"Adding summary for row {index+1} of {len(df)}")
    #    payload = {
    #        "messages": [
    #            {
    #                "role": "system",
    #                "content": "Be precise and concise. Generate an explanation for code below."
    #            },
    #            {
    #                "role": "user",
    #                "content": row['raw_code']
    #            }
    #        ]
    #    }
    #    response = call_llm(service, url, payload)
    #    if response is not None and "choices" in response.json():
    #        df['llm_summary'][index] = response.json()['choices'][0]['message']['content']
    #    else:
    #        print(f"[ERROR] Adding summary failed for file: {row['file']}")
    #return df

    ### OpenAI test code below ###
    service = "openai"
    url = "https://api.openai.com/v1/chat/completions"
    for index, row in tqdm(df.iterrows()):
        print(f"Adding summary for row {index+1} of {len(df)}")
        payload = {
            "model": "gpt-3.5-turbo-0125",
            "messages": [
                {
                    "role": "system",
                    "content": "Be precise and concise. Generate an explanation for code below."
                },
                {
                    "role": "user",
                    "content": row['raw_code']
                }
            ],
            "temperature": 0,
            "max_tokens": 1024,
        }
        response = call_llm(service, url, payload)
        if response is not None and "choices" in response.json():
            df['llm_summary'][index] = response.json()['choices'][0]['message']['content']
        else:
            print(f"[ERROR] Adding summary failed for file: {row['file']}")
    return df

def add_embeddings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates embedddings for code summaries and adds them to the dataframe
    Args:
    - df: pd.DataFrame, pandas dataframe with ['repo', 'folder', 'file', 'raw_code', 'llm_summary', 'summary_embed']
    Returns:
    - df: pd.DataFrame, pandas dataframe with ['repo', 'folder', 'file', 'raw_code', 'llm_summary', 'summary_embed']
    """
    service = "openai"
    url = "https://api.openai.com/v1/embeddings"
    for index, row in tqdm(df.iterrows()):
        if not pd.isnull(df['llm_summary'][index]):
            print(f"Adding embedding for row {index+1} of {len(df)}")
            payload = {
                "model": "text-embedding-3-small",
                "input": row['llm_summary']
            }
            response = call_llm(service, url, payload)
            if response is not None and 'data' in response.json(): 
                df['summary_embed'][index] = response.json()['data'][0]['embedding']
            else:
                print(f"[ERROR] Adding embedding failed for file: {row['file']}")

    return df

def upload_to_supabase(df: pd.DataFrame) -> None:
    """
    Uploads dataframe to supabase
    Args:
    - df: pd.DataFrame, pandas dataframe with ['repo', 'folder', 'file', 'raw_code', 'llm_summary', 'summary_embed']
    """
    data_dict = df.to_dict(orient='records')
    load_dotenv()
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    supabase_table = os.getenv('SUPABASE_TABLE')
    supabase_client = supabase.create_client(supabase_url, supabase_key)

    try:
        response = supabase_client.table(supabase_table).upsert(data_dict).execute()
    except Exception as e:
        print(f"[ERROR] Uploading to Supabase: {e}")

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
            "model": "text-embedding-3-small",
            "input": issue_text,
        }
        llm_service = "openai"
        llm_url = "https://api.openai.com/v1/embeddings"
        llm_response = call_llm(llm_service, llm_url, payload)
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
        if row['summary_embed'] is not None:
            try:
                embedding = torch.tensor(ast.literal_eval(row['summary_embed'])).unsqueeze(0)
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
            'file': df['file'][idx],
            'similarity': round(similarities[idx].item(), 2),
            })
    return files