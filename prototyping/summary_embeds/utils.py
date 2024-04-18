import os
import pandas as pd
import requests
import supabase

from typing import List
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential
from tqdm.auto import tqdm

# helper function to call llm
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
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
    
    response = None
    try:
        response = requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(e)
    
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
                if file in ['dataframe.py']:
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
    service = "anthropic"
    url = "https://api.anthropic.com/v1/messages"
    for index, row in tqdm(df.iterrows()):
        print(f"Adding summary for row {index+1} of {len(df)}")
        payload = {
            "system": "Be precise and concise. Generate an explanation for code below.",
            "messages": [
                {
                    "role": "user",
                    "content": row['raw_code']
                }
            ]
        }
        response = call_llm(service, url, payload)
        if response is not None and "content" in response.json():
            df['llm_summary'][index] = response.json()['content'][0]['text']
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