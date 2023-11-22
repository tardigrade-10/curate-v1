import base64
import requests
import os
import json
from typing import List, Any, Union
from tqdm import tqdm

from core.features.utils import calculate_cost_gpt4_turbo, add_dicts
from prompt import SIMPLE_GPT_BASED_HTR_PROMPT, SIMPLE_GPT_BASED_HTR_FORMATTED_PROMPT
from core.features.provider import creator, text_model_defaults, vision_model_defaults

from dotenv import load_dotenv
load_dotenv()


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def encode_and_batch(image_paths, batch_size=4, verbose = False):

    encoded = []
    encoded_name = []
    enc = []
    enc_name = []
    for image_path in image_paths:
        enc_name.append(image_path.split("/")[-1])
        enc.append(encode_image(image_path))
        if len(enc) >= batch_size:
            encoded.append(enc)
            encoded_name.append(enc_name)
            enc = []
            enc_name = []
    
    if len(enc) > 0:
        encoded.append(enc)
        encoded_name.append(enc_name)

    if verbose:
        print("Total images:", len(image_paths))
        print("Total batches:", len(encoded))

    return encoded, encoded_name


def htr_gen(images: List[Any], intel = False):

    # logging.info("encoded the images")
    total_usage = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}

    conversation = [{"role": "system", "content": SIMPLE_GPT_BASED_HTR_PROMPT}]
    # if intel:
    #     conversation = [{"role": "system", "content": SIMPLE_GPT_BASED_HTR_FORMATTED_PROMPT}]
        
    user_message = {"role": "user", "content": [*map(lambda x :{
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{x}"
          }
        }, images)]}
    conversation.append(user_message)

    try:
        response = creator(
                **vision_model_defaults,
                messages = conversation
                )
        
        response = response.model_dump()
        text = response["choices"][0]["message"]["content"]
        text = "{" + text.split("{")[1].split("}")[0] + "}"

        text = json.loads(text)
    except:
        # print(response.json())
        raise ValueError("Error in the response")

    total_usage = add_dicts(total_usage, dict(response["usage"]))

    return text, response["usage"]


def htr_batch_process(image_paths, batch_size: int):
    
    batches, batch_names = encode_and_batch(image_paths[:10], batch_size=batch_size, verbose=True)

    final_text = []
    total_tokens = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
    for batch in tqdm(batches):
        text, _tokens = htr_gen(batch)
        final_text.append(text["text"])
        total_tokens = add_dicts(total_tokens, _tokens)

    return batch_names, final_text, total_tokens
