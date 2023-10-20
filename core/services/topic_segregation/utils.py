

def add_dicts(a, b):
    return {k: a[k] + b[k] for k in a.keys() & b.keys()}

def calculate_cost_gpt4_8k(token_usage):
    prompt = token_usage['prompt_tokens']
    completion = token_usage['completion_tokens']

    cost =  (prompt * 0.03 + completion * 0.06) / 1000

    return cost


# import tiktoken

# encoding = tiktoken.get_encoding("cl100k_base")
# encoding = tiktoken.encoding_for_model("gpt-4")

# def num_tokens_from_string(string: str, encoding_name: str) -> int:
#     """Returns the number of tokens in a text string."""
#     encoding = tiktoken.get_encoding(encoding_name)
#     num_tokens = len(encoding.encode(string))
#     return num_tokens