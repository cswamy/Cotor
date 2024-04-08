import os
import pprint
import requests
from dotenv import load_dotenv
from supabase import create_client, Client
from tenacity import retry, stop_after_attempt, wait_random_exponential

# helper function to call llm
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def call_llm(payload: dict):
    url = "https://api.openai.com/v1/chat/completions"
    load_dotenv()
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
    }
    response = None
    try:
        response = requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(e)
        print(f"LLM request failed for {url}")
    return response

load_dotenv()
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

response = (
    supabase.table("Issues")
    .select("*")
    .eq('repo', 'gradio')
    .eq('issue_id', '6973')
    .execute()
    )

with open('./llm_prompts/supa_system.txt', 'r') as f:
    sys_prompt: str = f.read() + '\n\n' + f'Issue title: {response.data[0]["issue_title"]}\n\n' + f'Issue_body: {response.data[0]["issue_body"]}'
files_prompt: str = ''
for file in response.data[0]['commit_details']['file_details']:
    files_prompt += f'\n\nFile: {file["filename"]}\n\nPatch:\n{file["raw_patch"]}\n\nExplanation:\n{file["patch_explains"]}'

payload: dict = {
    "model": "gpt-4-1106-preview",
    "messages": [
        {
            "role": "system",
            "content": sys_prompt
        },
        {
            "role": "user",
            "content": files_prompt
        }
    ],
    "temperature": 0
}

response = call_llm(payload)
with open('llm_response.txt', 'w') as f:
    f.write(response.json()['choices'][0]['message']['content'])