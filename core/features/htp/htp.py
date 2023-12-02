import base64
import requests
import os
import json
from typing import List, Any, Union
from tqdm import tqdm
import asyncio

from core.features.utils import calculate_cost_gpt4_turbo, add_dicts, encode_images, ServiceCost
from core.features.htp.prompt import SIMPLE_GPT_BASED_HTP_PROMPT, SIMPLE_GPT_BASED_HTP_FORMATTED_PROMPT
from core.features.provider import creator, async_creator, text_model_defaults, vision_model_defaults

from dotenv import load_dotenv
load_dotenv()

service_cost = ServiceCost()

def htp_gen(image: Any, intel = False):

    total_usage = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
    conversation = [{"role": "system", "content": SIMPLE_GPT_BASED_HTP_PROMPT}]
    user_message = {"role": "user", "content": [
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image}"
                }
            }
        ]
    }
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
        raise ValueError("Error in the response")
    total_usage = add_dicts(total_usage, dict(response["usage"]))

    return text, response["usage"]


async def async_htp_gen(image: Any, intel = False):
    total_usage = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
    conversation = [{"role": "system", "content": SIMPLE_GPT_BASED_HTP_PROMPT}]
    user_message = {"role": "user", "content": [
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image}"
            }
        }
    ]}
    conversation.append(user_message)

    try:
        response = await async_creator(
            **vision_model_defaults,
            messages = conversation
        )
        response = response.model_dump()
        text = response["choices"][0]["message"]["content"]
        text = "{" + text.split("{")[1].split("}")[0] + "}"

        text = json.loads(text)
    except:
        raise ValueError("Error in the response")
    total_usage = add_dicts(total_usage, dict(response["usage"]))

    return text, response["usage"]


def htp_process(image_paths):
    
    encoded_dict = encode_images(image_paths, verbose=True)
    images = list(encoded_dict.values())
    ser_cost = service_cost.htp_process(len(images))

    total_tokens = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
    result_dict = {}
    for name, image in encoded_dict.items():
        text, _tokens = htp_gen(image)
        result_dict[name] = text
        total_tokens = add_dicts(total_tokens, _tokens)

    gpt_cost = calculate_cost_gpt4_turbo(total_tokens)

    return result_dict, total_tokens, gpt_cost, ser_cost



async def async_htp_process(image_paths):
    encoded_dict = encode_images(image_paths, verbose=True)
    images = list(encoded_dict.values())
    ser_cost = service_cost.htp_process(len(images))

    total_tokens = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
    result_dict = {}

    # Run htp_gen for each image concurrently
    tasks = [async_htp_gen(image) for name, image in encoded_dict.items()]
    results = await asyncio.gather(*tasks)

    for (name, _), (text, _tokens) in zip(encoded_dict.items(), results):
        result_dict[name] = text
        total_tokens = add_dicts(total_tokens, _tokens)

    gpt_cost = calculate_cost_gpt4_turbo(total_tokens)

    return result_dict, total_tokens, gpt_cost, ser_cost


