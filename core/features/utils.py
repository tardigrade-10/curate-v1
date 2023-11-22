import os
import requests
import fitz  # import the bindings PyMuPDF

from dotenv import load_dotenv
load_dotenv()


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

    os.makedirs(output_folder, exist_ok=True)  # create output folder

    if start > end > l:
        raise ValueError("Invalid page range")

    for i in range(start-1, end):  # iterate through the pages
        pix = doc[i].get_pixmap(dpi = 200)  # render page to an image
        pix.save(os.path.join(output_folder, "page-%i.png" % i))  # store image as a PNG

    print("Total pages in document:", l)
    print("Total images generated:", end-start+1)