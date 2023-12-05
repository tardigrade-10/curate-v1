from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, List
from uuid import uuid4
import os
import time
import aiofiles

from core.features.htp.htp import htp_process, async_htp_process
from core.features.htp.htp_class import HTPService
from core.features.utils import pdf_to_images

router = APIRouter(
    prefix="/htp",
    tags=["htp"],
    responses={404: {"description": "Not found"}},
)

htp_service = HTPService()

STORAGE = r"C:\Users\DELL\Documents\Curate\curate-v1\core\storage"

def ignored_text(text, i_text):
    for t in i_text:
        text = text.replace(t, "")
    return text

def file_management(file, file_ext):
    file_id = str(uuid4())
    file_path = f"{STORAGE}/{file_id}.{file_ext}"
    output_folder = f"{STORAGE}/{file_id}"

    os.makedirs(output_folder, exist_ok=True)  # create output folder

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return file_id, file_path, output_folder


async def async_file_management(file, file_ext):
    file_id = str(uuid4())
    file_path = f"{STORAGE}/{file_id}.{file_ext}"
    output_folder = f"{STORAGE}/{file_id}"
    os.makedirs(output_folder, exist_ok=True)  # create output folder

    async with aiofiles.open(file_path, "wb") as buffer:
        await buffer.write(await file.read())

    return file_id, file_path, output_folder


# @router.post("/htp_pdf")
# def text_recognition(file: UploadFile = File(...), page_start: int = 1, page_end: int = 1, remove_text: List = []) -> JSONResponse:

#     start_time = time.time()
#     file_ext = file.filename.split('.')[-1] in ("pdf", "PDF")
#     if not file_ext:
#         raise HTTPException(status_code=400, detail="Invalid file format")

#     file_id, file_path, output_folder = file_management(file, file_ext)
#     image_paths = pdf_to_images(file_path, output_folder, page_start, page_end)
#     text_dict, total_tokens = htp_process(image_paths = image_paths)

#     for k, v in text_dict.items():
#         text_dict[k]["text"] = ignored_text(v["text"], remove_text)

#     # Constructing the response
#     latency = f"{round(time.time() - start_time, 2)} s"
#     response = {
#         "filename": file.filename,
#         "content_type": file.content_type,
#         "recognized_text": text_dict,
#         "token_usage": total_tokens,
#         "cost": cost,
#         "latency": latency
#     }

#     return JSONResponse(content=response)


@router.post("/async_htp_pdf")
async def async_text_recognition(file: UploadFile = File(...), page_start: int = 1, page_end: int = 1, remove_text: List[str] = []) -> JSONResponse:

    start_time = time.time()
    file_ext = file.filename.split('.')[-1] in ("pdf", "PDF")
    if not file_ext:
        raise HTTPException(status_code=400, detail="Invalid file format")

    file_id, file_path, output_folder = await async_file_management(file, file_ext)
    image_paths = pdf_to_images(file_path, output_folder, page_start, page_end)
    text_dict, total_tokens, gpt_cost, service_cost = await htp_service.async_htp_process(image_paths = image_paths)

    for k, v in text_dict.items():
        text_dict[k]["text"] = ignored_text(v["text"], remove_text)

    # Constructing the response
    latency = f"{round(time.time() - start_time, 2)} s"
    response = {
        "filename": file.filename,
        "content_type": file.content_type,
        "recognized_text": text_dict,
        # "token_usage": total_tokens,
        "gpt_cost": gpt_cost,
        "service_cost": service_cost,
        "latency": latency
    }

    return JSONResponse(content=response)
