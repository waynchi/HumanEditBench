from human_edit_bench.evaluation import test_heb
from os import getenv

# since generations already exists, we can directly test it
test_heb(f"results/{getenv("EVAL_MODEL")}.json")
