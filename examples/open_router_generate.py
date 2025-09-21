from human_edit_bench.evaluation import generate_files, test_heb
from openai import OpenAI
from os import getenv

def generate_openrouter(prompt):
    # query the model with the prompt ....
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=getenv("VAL_OPENROUTER"),
    )
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b:free",
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
    # Returned code should be a valid Python code snippet
    return response.replace("```python\n", "").replace("\n```", "")


# 2: generate the code snippets for the EVAL_MODEL, store in generations folder
generate_files(generate_from_prompt, "prompts/whole_file.txt")
test_heb("results/whole_file/gpt-oss-20b.json")