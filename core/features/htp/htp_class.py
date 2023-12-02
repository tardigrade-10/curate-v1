import base64
import os
import json
import asyncio
from typing import Any, List, Tuple, Dict

from core.features.utils import calculate_cost_gpt4_turbo, add_dicts, ServiceCost, encode_images, process_for_json
from core.features.htp.prompt import SIMPLE_GPT_BASED_HTP_PROMPT
from core.features.provider import creator, async_creator, vision_model_defaults

service_cost = ServiceCost()

class HTPService:
    def __init__(self):
        self.max_tries = 3

    def htp_gen(self, image: Any, creator_args={}) -> Tuple[Dict[str, Any], Dict[str, int]]:
        
        conversation = [{"role": "system", "content": SIMPLE_GPT_BASED_HTP_PROMPT}]
        user_message = {
            "role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}"}}
            ]
        }
        conversation.append(user_message)
        
        for attempt in range(self.max_tries):
            try:
                response = creator(
                    **vision_model_defaults,
                    messages = conversation,
                    **creator_args
                )
                response = response.model_dump()
                text = response["choices"][0]["message"]["content"]
                text = process_for_json(text)
                text = json.loads(text)

                return text, response["usage"]

            except Exception as e:
                if attempt + 1 == 3:
                    raise ValueError(f"Error in the response after {self.max_tries}: {e}")
                continue


    async def async_htp_gen(self, image: Any, creator_args={}) -> Tuple[Dict[str, Any], Dict[str, int]]:

        conversation = [{"role": "system", "content": SIMPLE_GPT_BASED_HTP_PROMPT}]
        user_message = {
            "role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}"}}
            ]
        }
        conversation.append(user_message)

        for attempt in range(self.max_tries):
            try:
                response = await async_creator(
                    **vision_model_defaults,
                    messages = conversation,
                    **creator_args
                )
                response = response.model_dump()
                text = response["choices"][0]["message"]["content"]
                text = process_for_json(text)
                text = json.loads(text)

                return text, response["usage"]

            except Exception as e:
                if attempt + 1 == 3:
                    raise ValueError(f"Error in the response after {self.max_tries}: {e}")
                continue
    
        
    def htp_process(self, image_paths: List[str], creator_args={}) -> Tuple[Dict[str, Any], Dict[str, int], float]:
        encoded_dict = encode_images(image_paths, verbose=True)
        total_tokens = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
        result_dict = {}
        serv_cost = service_cost.htp_service(len(image_paths))

        for name, image in encoded_dict.items():
            text, _tokens = self.htp_gen(image = image, creator_args = creator_args)
            result_dict[name] = text
            total_tokens = add_dicts(total_tokens, _tokens)

        gpt_cost = calculate_cost_gpt4_turbo(total_tokens)

        return result_dict, total_tokens, gpt_cost, serv_cost


    async def async_htp_process(self, image_paths: List[str], creator_args={}) -> Tuple[Dict[str, Any], Dict[str, int], float]:
        encoded_dict = encode_images(image_paths, verbose=True)
        total_tokens = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
        result_dict = {}
        serv_cost = service_cost.htp_service(len(image_paths))

        tasks = [self.async_htp_gen(image=image, creator_args=creator_args) for name, image in encoded_dict.items()]
        results = await asyncio.gather(*tasks)

        for (name, _), (text, _tokens) in zip(encoded_dict.items(), results):
            result_dict[name] = text
            total_tokens = add_dicts(total_tokens, _tokens)

        gpt_cost = calculate_cost_gpt4_turbo(total_tokens)

        return result_dict, total_tokens, gpt_cost, serv_cost
