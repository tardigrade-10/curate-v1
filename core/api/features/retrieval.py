from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, List
from uuid import uuid4
import os
import time
import aiofiles
import json

from core.features.retrieval.retrieval_class import RetrievalTextService, RetrievalImageService
from core.features.utils import pdf_to_images

router = APIRouter(
    prefix="/retrieval",
    tags=["retrieval"],
    responses={404: {"description": "Not found"}},
)

retrieval_text_service = RetrievalTextService()
retrieval_image_service = RetrievalImageService()

STORAGE = r"C:\Users\DELL\Documents\Curate\curate-v1\core\storage"

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


@router.post("/async_retrieval_text")
async def async_retrieval_text(queries: List[str], file: UploadFile = File(...), page_start: int = 1, page_end: int = 1) -> JSONResponse:

    start_time = time.time()
    file_ext = file.filename.split('.')[-1] in ("pdf", "PDF")
    if not file_ext:
        raise HTTPException(status_code=400, detail="Invalid file format")

    file_id, file_path, output_folder = await async_file_management(file, file_ext)
    result_dict, total_tokens, total_chars, gpt_cost, service_cost = await retrieval_image_service.retrieval_process(file_path, queries, page_start, page_end)

    with open(f"{output_folder}/result.json", "w") as buffer:
        json.dump(result_dict, buffer, indent=4)

    # Constructing the response
    latency = f"{round(time.time() - start_time, 2)} s"
    response = {
        "filename": file.filename,
        "file_id": file_id,
        "content_type": file.content_type,
        # "total_pages": page_end-page_start + 1,
        "retrieved_text": result_dict,
        "token_usage": total_tokens,
        "total_character": total_chars,
        "gpt_cost": gpt_cost,
        "service_cost": service_cost,
        "latency": latency
    }
    return JSONResponse(content=response)


@router.post("/async_retrieval_image")
async def async_retrieval_image(queries: List[str], file: UploadFile = File(...), page_start: int = 1, page_end: int = 1) -> JSONResponse:

    start_time = time.time()
    file_ext = file.filename.split('.')[-1] in ("pdf", "PDF")
    if not file_ext:
        raise HTTPException(status_code=400, detail="Invalid file format")

    file_id, file_path, output_folder = await async_file_management(file, file_ext)
    image_paths = pdf_to_images(file_path, output_folder, page_start, page_end)
    result_dict, total_tokens, gpt_cost, service_cost = await retrieval_image_service.retrieval_process(image_paths, queries)

    with open(f"{output_folder}/result.json", "w") as buffer:
        json.dump(result_dict, buffer, indent=4)

    # Constructing the response
    latency = f"{round(time.time() - start_time, 2)} s"
    response = {
        "filename": file.filename,
        "file_id": file_id,
        "content_type": file.content_type,
        "total_pages": page_end-page_start + 1,
        "retrieved_text": result_dict,
        "token_usage": total_tokens,
        "gpt_cost": gpt_cost,
        "service_cost": service_cost,
        "latency": latency
    }

    return JSONResponse(content=response)
