import os
import json
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from core.features.provider import creator, text_creator_defaults
from core.features.utils import calculate_cost_gpt4_turbo

# Load environment variables
load_dotenv()

class LanguageTranslator:
    def __init__(self):
        self.text_model_defaults = text_creator_defaults
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO)

    def translate_to_eng(self, input_text: str) -> Dict[str, Any]:
        return self._translate(input_text, "SIMPLE_ENGLISH_TRANS_PROMPT")

    def translate_to_hin(self, input_text: str) -> Dict[str, Any]:
        return self._translate(input_text, "SIMPLE_HINDI_TRANS_PROMPT")

    def _translate(self, input_text: str, prompt_type: str) -> Dict[str, Any]:
        if len(input_text) > 100000:
            raise ValueError("Input Text is too long. Should be less than 100000 characters")

        # Assuming prompts are stored in a dictionary or similar structure
        prompts = {
            "SIMPLE_ENGLISH_TRANS_PROMPT": "Your English prompt here...",
            "SIMPLE_HINDI_TRANS_PROMPT": "Your Hindi prompt here..."
        }

        conversation = [{"role": "system", "content": prompts[prompt_type]}]

        user_prompt = f"""INPUT_TEXT:

        //input_text//

        {input_text}

        //input_text//

        OUTPUT:
        """

        user_message = {'role': 'user', "content": user_prompt}
        conversation.append(user_message)

        try:
            response = creator(
                **self.text_model_defaults,
                messages=conversation,
            )

            output = json.loads(response.choices[0].message.content)
            total_usage = response.usage.model_dump()

            return {"output": output, "total_usage": total_usage}
        except Exception as e:
            self.logger.error(f"Error in translation: {e}")
            raise

    def calculate_cost(self, usage_data: Dict[str, Any]) -> float:
        return calculate_cost_gpt4_turbo(usage_data)


# if __name__ == "__main__":
#     translator = LanguageTranslator()

#     try:
#         # Example usage
#         text = "Your text here"
#         result = translator.translate_to_eng(text)
#         print(result["output"]["text"])
#         print(result["total_usage"])

#         cost = translator.calculate_cost(result["total_usage"])
#         print(cost)
#         print(cost / 10000)

#         # Add similar code for Hindi translation
#     except Exception as e:
#         print(f"An error occurred: {e}")
