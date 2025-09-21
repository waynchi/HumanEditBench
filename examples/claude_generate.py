from human_edit_bench.evaluation import generate_files, test_heb
from os import getenv
import re
import anthropic
import os

def parse_code_snippet(response):
    # Remove opening ```[language]\n pattern (includes special chars like /)
    result = re.sub(r'^```[\w/\-+.]*\n', '', response)
    # Remove closing \n``` pattern  
    result = result.replace('\n```', '')
    return result


def generate_claude(prompt: str) -> str:
    api_key = os.getenv("WAYNE_CLAUDE")
    # Initialize the client
    client = anthropic.Anthropic(api_key=api_key)
    
    response = client.messages.create(
        model="claude-3-7-sonnet-20250219", 
        max_tokens=10000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
        
    return response.content[0].text
        


# 1: define a function to generate code snippets given the prompt specified in file
#    (in this case: prompts/python_whole_file.txt)
def generate_from_prompt(prompt):
    response = generate_claude(prompt)
    return parse_code_snippet(response)


# 2: generate the code snippets for the EVAL_MODEL, store in generations folder
generate_files(generate_from_prompt, "prompts/whole_file.txt")
test_heb("results/whole_file/claude-sonnet-3-7.json")