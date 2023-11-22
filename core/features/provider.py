from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()

client = OpenAI()

creator = client.chat.completions.create

text_model_defaults = {"model" : "gpt-4-1106-preview", "temperature" : 0.1, "response_format" : {"type": "json_object"}}
vision_model_defaults = {"model" : "gpt-4-vision-preview", "temperature" : 0.1, "max_tokens": 4000}