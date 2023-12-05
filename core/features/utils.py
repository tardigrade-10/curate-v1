import os
import requests
import fitz  # import the bindings PyMuPDF
import aiofiles
import asyncio 
import base64

from dotenv import load_dotenv
load_dotenv()

def process_for_json(text):
    # Find the index of the first '{' and the last '}'
    start_index = text.find('{')
    end_index = text.rfind('}')

    # Extract the text between the first '{' and the last '}'
    if start_index != -1 and end_index != -1 and end_index > start_index:
        extracted_text = text[start_index:end_index + 1]

    else:
        extracted_text = ''

    return extracted_text


def calculate_cost_gpt4_8k(token_usage):
    prompt = token_usage['prompt_tokens']
    completion = token_usage['completion_tokens']

    cost =  (prompt * 0.03 + completion * 0.06) / 1000

    return {"usd": cost, "inr": usd2inr(cost)}

def calculate_cost_gpt4_turbo(token_usage):
    prompt = token_usage['prompt_tokens']
    completion = token_usage['completion_tokens']

    cost =  (prompt * 0.01 + completion * 0.03) / 1000

    return {"usd": cost, "inr": usd2inr(cost)}


def add_dicts(a, b):
    return {k: a[k] + b[k] for k in a.keys() & b.keys()}


def usd2inr(amount):
    response = requests.get(
        "https://anyapi.io/api/v1/exchange/convert",
        params={
            'apiKey': os.environ.get("ANYAPI_API_KEY"),
            'base': 'USD',
            'to': 'INR',
            'amount': amount
        }
    )
    return response.json()["converted"]


def pdf_to_images(pdf_path, output_folder, start, end, dpi=300, zoom = 1):
    fname = pdf_path  # get filename from command line
    doc = fitz.open(fname)  # open document
    l = len(doc)

    if start > end or end > l:
        raise ValueError(f"Invalid page range. Document has only {l} pages.")

    file_paths = []
    for i in range(start-1, end):  # iterate through the pages
        pix = doc[i].get_pixmap(dpi = 200)  # render page to an image
        img_path = os.path.join(output_folder, f"page-{i+1}.png")
        pix.save(img_path)  # store image as a PNG
        file_paths.append(img_path)

    print("Total pages in document:", l)
    print("start_page:", start, "end_page:", end)
    print("Total images generated:", end-start+1)

    return file_paths


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def encode_images(image_paths, verbose = False):

    enc_dict = {}
    for path in image_paths:
        enc_dict[os.path.basename(path)] = encode_image(path)
    if verbose:
        print("Total images:", len(image_paths))
    return enc_dict


class ServiceCost:
    def __init__(self):
        pass

    def htp_service(self, total_images):
        # INR 2/- per page 
        return total_images * 2.0

    def retrieval_text_service(self, input_len: int, queries_count: int):
        # INR 1 per 1000 chars + 10% of the cost of input per query
        base = input_len*0.0003
        return round(base *(1 + 0.1 * queries_count), 2)
    
    def retrieval_image_service(self, total_image: int, queries_count: int):
        # INR 2 per image + 10% of the cost of input per query
        base = total_image*2
        return round(base *(1 + 0.1 * queries_count), 2)




    

