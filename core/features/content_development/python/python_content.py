from openai import OpenAI
import json
import os
import time
import asyncio
from typing import List, Dict, Any, Tuple, Union

from core.features.content_development.python.prompts import SIMPLE_COURSE_GENERATION_PROMPT, JUPYTER_NOTEBOOK_TUTORIAL_PROMPT, JUPYTER_NOTEBOOK_TUTORIAL_PROMPT2
from core.features.content_development.python import DEFAULT_IPYNB_TEMPLATE
from core.features.utils import add_dicts, calculate_cost_gpt4_omni
from core.features.provider import async_creator, text_model_defaults

from dotenv import load_dotenv
load_dotenv()


class PythonContentGeneration:
    def __init__(self, ipynb_template=DEFAULT_IPYNB_TEMPLATE) -> None:
        self.ipynb_template = ipynb_template


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
        gpt_cost = calculate_cost_gpt4_omni(total_usage)

        curriculum_path = os.path.join(path, output['title'].replace(" ", "_") + ".json")

        # os.makedirs(curriculum_path, exist_ok=True)
        with open(curriculum_path, 'w') as file:
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

        current_module = {module},

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

        """
        Rules to create the jupyter notebook:
        1. metadata tag must be present in code cell
        """

        notebook = self.ipynb_template

        # Adding the cells from the input JSON to the notebook template
        for cell in input_json['cells']:
            if cell['cell_type'] == "code":
                cell['metadata'] = {}

        notebook['cells'] = input_json['cells']

        with open(f'{file_name}.ipynb', 'w') as file:
            json.dump(notebook, file, indent=2)


    async def content_pipeline(self, curriculum, path):

        """
        This function generate content sequentially
        """

        total_tokens = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
        previous_part = "NA"
        curriculum = json.loads(curriculum)

        content_dir = os.path.join(path, curriculum['title'].replace(" ", "_"))
        os.makedirs(content_dir, exist_ok=True)
        curriculum_path = os.path.join(content_dir, "curriculum.json")

        with open(curriculum_path, 'w') as file:
            json.dump(curriculum, file, indent=2)

        for module, topics in curriculum['curriculum'].items():

            module_path = os.path.join(content_dir, module)
            os.makedirs(module_path, exist_ok=True)

            for i, topic in enumerate(topics):

                topic = topic.replace(":", "-")
                result = await self.generate_content_notebook(curriculum=curriculum, previous_part=previous_part, current_topic=topic)
            
                output = result['output']
                usage = result['total_usage'].model_dump()
                total_tokens = add_dicts(total_tokens, usage)
                notebook_json = json.loads(output)
                notebook_path = os.path.join(module_path, str(i+1) + "_" + topic.replace(" ", "_"))
                self.convert_to_jupyter_notebook(notebook_json, notebook_path)
                previous_part = notebook_json

        gpt_cost = calculate_cost_gpt4_omni(total_tokens)
        return total_tokens, gpt_cost
    

    async def content_pipeline2(self, curriculum, path):

        """
        This function generate content asynchronously, and much faster then the upper function
        """

        total_tokens = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
        curriculum = json.loads(curriculum)

        content_dir = os.path.join(path, curriculum['title'].replace(" ", "_"))
        os.makedirs(content_dir, exist_ok=True)
        curriculum_path = os.path.join(content_dir, "curriculum.json")

        with open(curriculum_path, 'w') as file:
            json.dump(curriculum, file, indent=2)

        tasks = []
        for module, topics in curriculum['curriculum'].items():
            for topic in topics:
                topic = topic.replace(":", "-")
                task = self.generate_content_notebook2(curriculum=curriculum, module = module, current_topic=topic)
                tasks.append(task)

        results = await asyncio.gather(*tasks)

        for i, result in enumerate(results):

            notebook_json, module, topic, usage = json.loads(result['output']), result['module'], result['topic'], result['total_usage'].model_dump()
            total_tokens = add_dicts(total_tokens, usage)

            module_path = os.path.join(content_dir, module)
            os.makedirs(module_path, exist_ok=True)
            self.convert_to_jupyter_notebook(notebook_json, os.path.join(module_path, str(i+1) + "_" + topic.replace(" ", "_")))

        gpt_cost = calculate_cost_gpt4_omni(total_tokens)
        return total_tokens, gpt_cost