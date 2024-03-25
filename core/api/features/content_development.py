from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, List
from uuid import uuid4
import os
import time
import aiofiles
import json

from core.features.content_development.python.python_content import PythonContentGeneration 
from core.features.content_development.python.tableau import TableauContentGeneration 
from core.features.utils import pdf_to_images
from dotenv import load_dotenv
load_dotenv()
STORAGE = os.getenv("STORAGE_PATH")

router = APIRouter(
    prefix="/content_development",
    tags=["content_development"],
    responses={404: {"description": "Not found"}},
)

# initiate the classes inside the functions directly to remove previous states
python_content_class = PythonContentGeneration()
tableau_content_class = TableauContentGeneration()

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

    """
    CURRICULUM FORMAT

    {
    "title": "title of the course",
    "curriculum": {
      "module1": [
        list of subtopics for module1
      ],
      "module2": [
        list of subtopics for module2
      ]
    }
  }
    """

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

@router.post("/tableau_content_development")
async def tableau_content_development(curriculum) -> JSONResponse:

    """
    CURRICULUM FORMAT

    {
    "title": "title of the course",
    "curriculum": {
      "module1": [
        list of subtopics for module1
      ],
      "module2": [
        list of subtopics for module2
      ]
    }
  }
    """

    start_time = time.time()
    total_usage, gpt_cost = await tableau_content_class.content_pipeline2(curriculum, STORAGE)

    # Constructing the response
    latency = f"{round(time.time() - start_time, 2)} s"
    response = {
        "curriculum": json.loads(curriculum),
        "total_usage": total_usage,
        "gpt_cost": gpt_cost,
        "latency": latency
    }
    return JSONResponse(content=response)

