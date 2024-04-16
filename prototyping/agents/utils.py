import os
import pandas as pd
import requests

from typing import List
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential

# helper function to call llm
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def call_llm(url: str, payload: dict):
    load_dotenv()
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
    }
    response = None
    try:
        response = requests.post(url, json=payload, headers=headers)
    except:
        print(f"LLM request failed for {url}")
    return response

def extract_files(repo: str, repo_folders: List[str]) -> pd.DataFrame: 
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

def add_embeddings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds embeddings to a pandas dataframe
    Args:
    - df: pd.DataFrame, pandas dataframe with ['repo', 'folder', 'file', 'raw_code']
    Returns:
    - df: pd.DataFrame, pandas dataframe with ['repo', 'folder', 'file', 'raw_code', 'embedding']
    """
    url = "https://api.openai.com/v1/embeddings"
    for index, row in df.iterrows():
        payload = {
            "input": row['raw_code'],
            "model": "text-embedding-3-large"
        }
        response = call_llm(url, payload)
        if response is not None:
            embedding = response.json()['data'][0]['embedding']
            df['embedding'][index] = embedding

    return df