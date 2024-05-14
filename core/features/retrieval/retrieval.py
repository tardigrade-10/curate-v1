import asyncio
import json
import logging
import re
from typing import List, Dict, Any, Tuple
from tqdm import tqdm
import fitz

from core.features.retrieval.prompts import SIMPLE_INFO_RETRIEVAL_TEXT_PROMPT, SIMPLE_INFO_RETRIEVAL_IMAGE_PROMPT
from core.features.utils import add_dicts, calculate_cost_gpt4_omni, ServiceCost, encode_images, process_for_json
from core.features.provider import async_creator, text_model_defaults, vision_model_defaults
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

service_cost = ServiceCost()

class RetrievalTextService:
    def __init__(self):
        # self.prompt = SIMPLE_INFO_RETRIEVAL_TEXT_PROMPT
        # self.creator = async_creator
        # self.max_tries = 3
        pass

    def get_text_lists_from_raw_text(self, raw_text: str) -> List[str]:
        if not isinstance(raw_text, str):
            raise ValueError("raw_text must be a string")

        return [x.strip() for x in raw_text.split('. ') if x.strip()]
    

    def chunk_raw_text_list(self, raw_text_list: List[str], max_len=3000) -> List[List[str]]:
        text_list = []
        current_chunk = []
        current_len = 0

        for text in raw_text_list:
            text_len = len(text)
            if current_len + text_len > max_len and current_chunk:
                text_list.append(current_chunk)
                current_chunk = [text]
                current_len = text_len
            else:
                current_chunk.append(text)
                current_len += text_len

        if current_chunk:
            text_list.append(current_chunk)

        return text_list


    def text_path_to_chunk(self, path: str, page_start: int = 1, page_end: int = 1, max_len=20000) -> Tuple[int, List[List[str]]]:
        try:
            with fitz.open(path) as doc:
                _text = ""
                for i in range(page_start-1, page_end):
                    _text += doc[i].get_text()

        except IOError as e:
            logger.error(f"Error reading file: {e}")
            raise

        _text_list = self.get_text_lists_from_raw_text(_text)
        chunked_text_list = self.chunk_raw_text_list(_text_list, max_len)

        return len(_text), chunked_text_list
    

    async def retrieval_from_text(self, raw_text: str, queries: str, creator_args: Dict) -> Dict:
        conversation = [{"role": "system", "content": SIMPLE_INFO_RETRIEVAL_TEXT_PROMPT}]
        user_prompt = f"""
        RAW_TEXT:

        //raw_text//

        {raw_text}

        //raw_text//

        Queries:

        {queries}

        OUTPUT:
        """

        conversation.append({'role': 'user', "content": user_prompt})

        try:
            response = await async_creator(
                **text_model_defaults,
                messages=conversation,
                **creator_args
            )
            response = response.model_dump()
        except Exception as e:
            logger.error(f"Error in retrieval: {e}")
            raise

        output = response["choices"][0]["message"]["content"]
        return {"output": output, "total_usage": response["usage"]}


    async def retrieval_process(self, input_text_path: str, queries: str, page_start: int = 1, page_end: int = 1, creator_args: Dict = {}) -> Tuple[Dict, Dict]:
        try:
            input_len, chunked_text_list = self.text_path_to_chunk(input_text_path, page_start, page_end)
            print("chunked_text_list", chunked_text_list)
        except Exception as e:
            logger.error(f"Error in text chunking: {e}")
            raise
        
        indexed_queries = {str(i+1): query for i, query in enumerate(queries)}
        final_dict = {key: [] for key in indexed_queries.keys()}
        total_tokens = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}

        try:
            tasks = []
            for raw_text_list in tqdm(chunked_text_list):
                _text = "\n".join(raw_text_list)
                task = self.retrieval_from_text(_text, str(indexed_queries), creator_args)
                tasks.append(task)
            results = await asyncio.gather(*tasks)

        except Exception as e:
            logger.error(f"Error in retrieval process: {e}")

        print("result_dict", results)
        for result in results:
            # print(result)
            final_dict = add_dicts(final_dict, json.loads(result["output"]))
            total_tokens = add_dicts(total_tokens, result["total_usage"])

        result_with_query = {query: final_dict[index] for index, query in indexed_queries.items()}
        gpt_cost = calculate_cost_gpt4_omni(total_tokens)
        serv_cost = service_cost.retrieval_service(input_len=input_len, queries_count=len(queries))
        return result_with_query, total_tokens, input_len, gpt_cost, serv_cost



class RetrievalImageService:
    def __init__(self):
        self.max_tries = 3

    async def retrieval_from_image(self, image: Any, queries: List[str], creator_args: Dict) -> Dict:

        conversation = [{"role": "system", "content": SIMPLE_INFO_RETRIEVAL_IMAGE_PROMPT}]
        user_message = {
            "role": "user", "content": [str(queries), 
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}"}}
            ]
        }
        conversation.append(user_message)
        try:
            response = await async_creator(
                    **vision_model_defaults,
                    messages = conversation,
                    **creator_args
                    )
            response = response.model_dump()
            output = response["choices"][0]["message"]["content"]
            output = process_for_json(output)
        except:
            raise ValueError("Error in the response")
        return {"output": output, "total_usage": response["usage"]}
    
        
    async def retrieval_process(self, image_paths: List[str], queries: List[str], creator_args={}) -> Tuple[Dict[str, Any], Dict[str, int], float]:
        
        encoded_dict = encode_images(image_paths, verbose=True)
        indexed_queries = {str(i+1): query for i, query in enumerate(queries)}
        final_dict = {key: [] for key in indexed_queries.keys()}
        total_tokens = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
        
        try: 
            tasks = []
            for image in list(encoded_dict.values()):
                task = self.retrieval_from_image(image = image, queries = indexed_queries, creator_args = creator_args)
                tasks.append(task)
            results = await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error in retrieval process: {e}")

        for result in results:
            # print(result)
            final_dict = add_dicts(final_dict, json.loads(result["output"]))
            total_tokens = add_dicts(total_tokens, result["total_usage"])

        '''
        can add result list as well to track the retrieval from respective pages
        <here>
        '''
        # print(final_dict)
        result_with_query = {query: final_dict[index] for index, query in indexed_queries.items()}

        serv_cost = service_cost.retrieval_image_service(len(image_paths), len(queries))
        gpt_cost = calculate_cost_gpt4_omni(total_tokens)

        return result_with_query, total_tokens, gpt_cost, serv_cost
