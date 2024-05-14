from openai import OpenAI, AsyncOpenAI

from dotenv import load_dotenv
load_dotenv()

client = OpenAI()
async_client = AsyncOpenAI()

creator = client.chat.completions.create
async_creator = async_client.chat.completions.create
moderator = client.moderations.create
async_moderator = async_client.moderations.create


text_model_defaults_3_5 = {"model" : "gpt-3.5-turbo", "temperature" : 0.5, "response_format" : {"type": "json_object"}}
text_model_defaults = {"model" : "gpt-4o", "temperature" : 0.5, "response_format" : {"type": "json_object"}}
vision_model_defaults = {"model" : "gpt-4o", "temperature" : 1, "max_tokens": 4000}