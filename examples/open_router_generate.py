from human_edit_bench.evaluation import generate_files, test_heb
from openai import OpenAI
from os import getenv
import time
import re


def parse_code_snippet(response):    
    # Remove opening ```[language]\n pattern (includes special chars like /)
    result = re.sub(r'^```[\w/\-+.]*\n', '', response)
    # Remove closing \n``` pattern  
    result = result.replace('\n```', '')
    return result


def generate_openrouter(prompt):
    """
    Query the OpenRouter API with retry logic.
    Retries up to 3 times on any failure with exponential backoff.
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=getenv("VAL_OPENROUTER"),
    )
    
    max_retries = 5
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model="qwen/qwen-2.5-72b-instruct:free",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return completion.choices[0].message.content
            
        except Exception as e:
            last_exception = e
            
            # Don't sleep on the last attempt
            if attempt < max_retries - 1:
                delay = 2 ** attempt
                time.sleep(delay)
    
    # If we get here, all retries failed
    raise last_exception


# 1: define a function to generate code snippets given the prompt specified in file
#    (in this case: prompts/python_whole_file.txt)
def generate_from_prompt(prompt):
    response = generate_openrouter(prompt)
    # Returned code should be a valid Python code snippet
    return parse_code_snippet(response)


# 2: generate the code snippets for the EVAL_MODEL, store in generations folder
generate_files(generate_from_prompt, "prompts/whole_file.txt")
test_heb("results/whole_file/qwen-2.5-72b-instruct:free.json")