from human_edit_bench.evaluation import generate_files, test_heb
from openai import OpenAI
from os import getenv
import re

def parse_code_snippet(response):
    # Remove opening ```[language]\n pattern (includes special chars like /)
    result = re.sub(r'^```[\w/\-+.]*\n', '', response)
    # Remove closing \n``` pattern  
    result = result.replace('\n```', '')
    return result

def generate_openrouter(prompt):
    # query the model with the prompt ....
    client = OpenAI(
        api_key=getenv("VAL_OPENAI"),
    )
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
            "role": "user",
            "content": prompt
            }
        ]
    )

    return completion.choices[0].message.content


# 1: define a function to generate code snippets given the prompt specified in file
#    (in this case: prompts/python_whole_file.txt)
def generate_from_prompt(prompt):
    response = generate_openrouter(prompt)
    return parse_code_snippet(response)


# 2: generate the code snippets for the EVAL_MODEL, store in generations folder
generate_files(generate_from_prompt, "prompts/whole_file.txt")
test_heb("results/whole_file/gpt-4o-mini.json")