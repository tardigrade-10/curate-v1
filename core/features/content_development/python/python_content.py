from openai import OpenAI
import json
import os
import time
import asyncio
from typing import List, Dict, Any, Tuple, Union

from core.features.content_development.python.prompts import SIMPLE_COURSE_GENERATION_PROMPT, JUPYTER_NOTEBOOK_TUTORIAL_PROMPT, JUPYTER_NOTEBOOK_TUTORIAL_PROMPT2
from core.features.topic_segregation.utils import add_dicts, calculate_cost_gpt4_turbo
from core.features.provider import async_creator, text_model_defaults

from dotenv import load_dotenv
load_dotenv()


class PythonContentGeneration:
    def __init__(self) -> None:
        pass

    async def generate_course_structure(self, title:str, scope:str, duration_in_hours:int, num_modules:int, path=None) -> Dict[str, Any]:

        conversation = [{"role": "system", "content": SIMPLE_COURSE_GENERATION_PROMPT}]

        user_input = f"""
        topic: {title}
        scope: {scope}
        duration_in_hours: {duration_in_hours}
        num_modules: {num_modules}
        """

        user_message = {'role': 'user', 'content': user_input}
        conversation.append(user_message)

        response = await async_creator(
            **text_model_defaults,
            messages=conversation
            )
        
        response = response.model_dump()
        output = json.loads(response["choices"][0]["message"]["content"])
        total_usage = response["usage"]
        gpt_cost = calculate_cost_gpt4_turbo(total_usage)

        curriculum_path = os.path.join(path, output['title'].replace(" ", "_"))

        os.makedirs(curriculum_path, exist_ok=True)
        with open(os.path.join(curriculum_path, 'curriculum.json'), 'w') as file:
            json.dump(output, file, indent=2)

        return output, gpt_cost


    async def generate_content_notebook(self, curriculum, previous_part, current_topic):

        conversation = [{"role": "system", "content": JUPYTER_NOTEBOOK_TUTORIAL_PROMPT}]

        user_input = f"""
        curriculum = {curriculum},

        previous_part = {previous_part},

        current_part = {current_topic}
        """

        user_message = {'role': 'user', 'content': user_input}
        conversation.append(user_message)

        response = await async_creator(
            **text_model_defaults,
            messages=conversation
            )
        
        output = response.choices[0].message.content
        total_usage = response.usage

        return {"output": output, "total_usage": total_usage}
    

    async def generate_content_notebook2(self, curriculum, module, current_topic):

        conversation = [{"role": "system", "content": JUPYTER_NOTEBOOK_TUTORIAL_PROMPT2}]

        user_input = f"""
        curriculum = {curriculum},

        module = {module},

        current_part = {current_topic}
        """

        user_message = {'role': 'user', 'content': user_input}
        conversation.append(user_message)

        response = await async_creator(
            **text_model_defaults,
            messages=conversation
            )
        
        output = response.choices[0].message.content
        total_usage = response.usage

        return {"output": output, "module": module, "topic": current_topic, "total_usage": total_usage}
    

    def convert_to_jupyter_notebook(self, input_json, file_name):

        # Template for a Jupyter Notebook

        """
        Rules to create the jupyter notebook:
        1. metadata tag must be present in code cell
        """
        notebook_template = {
            "cells": [],
            "metadata": {'kernelspec': {'display_name': 'Python 3',
                'language': 'python',
                'name': 'python3'},
                'language_info': {'codemirror_mode': {'name': 'ipython', 'version': 3},
                'file_extension': '.py',
                'mimetype': 'text/x-python',
                'name': 'python',
                'nbconvert_exporter': 'python',
                'pygments_lexer': 'ipython3',
                'version': '3.8.5'}},
            "nbformat": 4,
            "nbformat_minor": 4
        }

        # Adding the cells from the input JSON to the notebook template
        for cell in input_json['cells']:
            if cell['cell_type'] == "code":
                cell['metadata'] = {}

        notebook_template['cells'] = input_json['cells']

        with open(f'{file_name}.ipynb', 'w') as file:
            json.dump(notebook_template, file, indent=2)


    async def content_pipeline(self, curriculum, path):

        total_tokens = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
        previous_part = "NA"
        curriculum = json.loads(curriculum)
        for module, topics in curriculum['curriculum'].items():
            for i, topic in enumerate(topics):
                # Assuming generate_content_notebook and convert_to_jupyter_notebook are asynchronous
                result = await self.generate_content_notebook(curriculum=curriculum, previous_part=previous_part, current_topic=topic)
            
                output = result['output']
                print(output)
                usage = result['total_usage'].model_dump()

                total_tokens = add_dicts(total_tokens, usage)
                content_json = json.loads(output)

                os.makedirs(os.path.join(path, curriculum['title'].replace(" ", "_"), module), exist_ok=True)
                self.convert_to_jupyter_notebook(content_json, os.path.join(path, curriculum['title'].replace(" ", "_"), module, str(i+1) + "_" + topic.replace(" ", "_")))
                previous_part = content_json

        gpt_cost = calculate_cost_gpt4_turbo(total_tokens)
        return total_tokens, gpt_cost
    

    async def content_pipeline2(self, curriculum, path):

        total_tokens = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
        curriculum = json.loads(curriculum)
        tasks = []
        for module, topics in curriculum['curriculum'].items():
            for topic in topics:
                # Assuming generate_content_notebook and convert_to_jupyter_notebook are asynchronous
                topic = topic.replace(":", "-")
                task = self.generate_content_notebook2(curriculum=curriculum, module = module, current_topic=topic)
                tasks.append(task)

        results = await asyncio.gather(*tasks)

        for i, result in enumerate(results):

            output = result['output']
            module = result['module']
            topic = result['topic']
            print(output)
            usage = result['total_usage'].model_dump()
            total_tokens = add_dicts(total_tokens, usage)
            content_json = json.loads(output)

            os.makedirs(os.path.join(path, curriculum['title'].replace(" ", "_"), module), exist_ok=True)
            self.convert_to_jupyter_notebook(content_json, os.path.join(path, curriculum['title'].replace(" ", "_"), module, str(i+1) + "_" + topic.replace(" ", "_")))

        gpt_cost = calculate_cost_gpt4_turbo(total_tokens)
        return total_tokens, gpt_cost