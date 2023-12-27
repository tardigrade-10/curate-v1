from openai import OpenAI, AsyncOpenAI

from dotenv import load_dotenv
load_dotenv()

client = OpenAI()
async_client = AsyncOpenAI()

creator = client.chat.completions.create
async_creator = async_client.chat.completions.create

text_model_defaults = {"model" : "gpt-4-1106-preview", "temperature" : 0.5, "response_format" : {"type": "json_object"}}
vision_model_defaults = {"model" : "gpt-4-vision-preview", "temperature" : 1, "max_tokens": 4000}