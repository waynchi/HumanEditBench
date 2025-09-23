from human_edit_bench.evaluation import generate_files, test_heb
from openai import OpenAI
from os import getenv
import re
import time

def parse_code_snippet(response):
    # Remove opening ```[language]\n pattern (includes special chars like /)
    result = re.sub(r'^```[\w/\-+.]*\n', '', response)
    # Remove closing \n``` pattern  
    result = result.replace('\n```', '')
    return result


def generate_openai(prompt):
    """
    Query the OpenRouter API with retry logic.
    Retries up to 3 times on any failure with exponential backoff.
    """
    client = OpenAI(
        api_key=getenv("VAL_OPENAI"),
    )
    
    max_retries = 5
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            
            # use this to mess with reasoning effort
            # response = client.responses.create(
            #     # model="o3-mini-2025-01-31",
            #     model="o4-mini-2025-04-16",
            #     reasoning={"effort": "high"},
            #     input=[
            #         {
            #             "role": "user", 
            #             "content": prompt
            #         }
            #     ]
            # )
            # return response.output_text

            # use this for most models
            completion = client.chat.completions.create(
                # model="o4-mini-2025-04-16",
                # model="o3-mini-2025-01-31",
                model="gpt-4o-2024-08-06",
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
                # Exponential backoff: 1s, 2s, 4s
                delay = 2 ** attempt
                time.sleep(delay)
    
    # If we get here, all retries failed
    print(last_exception)
    raise last_exception

# 1: define a function to generate code snippets given the prompt specified in file
#    (in this case: prompts/python_whole_file.txt)
def generate_from_prompt(prompt):
    response = generate_openai(prompt)
    return parse_code_snippet(response)


# 2: generate the code snippets for the EVAL_MODEL, store in generations folder
generate_files(generate_from_prompt, "prompts/whole_file.txt")
test_heb("results/whole_file/gpt-o4-mini-high.json")