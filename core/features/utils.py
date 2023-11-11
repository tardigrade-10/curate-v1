def calculate_cost_gpt4_8k(token_usage):
    prompt = token_usage['prompt_tokens']
    completion = token_usage['completion_tokens']

    cost =  (prompt * 0.03 + completion * 0.06) / 1000

    return cost

def calculate_cost_gpt4_turbo(token_usage):
    prompt = token_usage['prompt_tokens']
    completion = token_usage['completion_tokens']

    cost =  (prompt * 0.01 + completion * 0.03) / 1000

    return cost



def add_dicts(a, b):
    return {k: a[k] + b[k] for k in a.keys() & b.keys()}