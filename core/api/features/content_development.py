from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, List
from uuid import uuid4
import os
import time
import aiofiles
import json

from core.features.content_development.python.python_content import PythonContentGeneration 
from core.features.utils import pdf_to_images

router = APIRouter(
    prefix="/content_development",
    tags=["content_development"],
    responses={404: {"description": "Not found"}},
)

python_content_class = PythonContentGeneration()

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


@router.post("/python_curriculum_development")
async def python_curriculum_development(title, scope, duration_in_hours, num_modules) -> JSONResponse:

    start_time = time.time()
    
    curriculum, gpt_cost = await python_content_class.generate_course_structure(title, scope, duration_in_hours, num_modules, path=STORAGE)

    # Constructing the response
    latency = f"{round(time.time() - start_time, 2)} s"
    response = {
        "title": title,
        "scope": scope,
        "duration_in_hours": duration_in_hours,
        "num_modules": num_modules,
        "curriculum": curriculum,
        "gpt_cost": gpt_cost,
        "latency": latency
    }
    return JSONResponse(content=response)


@router.post("/python_content_development")
async def python_content_development(curriculum) -> JSONResponse:

    start_time = time.time()
    total_usage, gpt_cost = await python_content_class.content_pipeline2(curriculum, STORAGE)

    # Constructing the response
    latency = f"{round(time.time() - start_time, 2)} s"
    response = {
        "curriculum": json.loads(curriculum),
        "total_usage": total_usage,
        "gpt_cost": gpt_cost,
        "latency": latency
    }
    return JSONResponse(content=response)

