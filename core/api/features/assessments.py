import os
import json
import time
import zipfile
import aiofiles
from uuid import uuid4
from typing import Dict, List
from fastapi.responses import JSONResponse
from fastapi import APIRouter, File, UploadFile, HTTPException

from core.features.assessments.check import AssignmentCheck 

router = APIRouter(
    prefix="/assessments",
    tags=["assessments"],
    responses={404: {"description": "Not found"}},
)

assessment_check = AssignmentCheck()

ASSESSMENTS_STORAGE = r"C:\Users\DELL\Documents\Curate\curate-v1\core\storage\assessments"

# def file_management(file, file_ext):
#     file_id = str(uuid4())
#     file_path = f"{STORAGE}/{file_id}.{file_ext}"
#     output_folder = f"{STORAGE}/{file_id}"
#     os.makedirs(output_folder, exist_ok=True)  # create output folder

#     with open(file_path, "wb") as buffer:
#         buffer.write(file.file.read())

#     return file_id, file_path, output_folder


# async def async_file_management(file, file_ext):
#     file_id = str(uuid4())
#     file_path = f"{STORAGE}/{file_id}.{file_ext}"
#     output_folder = f"{STORAGE}/{file_id}"
#     os.makedirs(output_folder, exist_ok=True)  # create output folder

#     async with aiofiles.open(file_path, "wb") as buffer:
#         await buffer.write(await file.read())

#     return file_id, file_path, output_folder



@router.post("/assess")
async def assignment_assess(
        path: str, 
        check_duplicates: bool = False
    ) -> JSONResponse:
    """
    Main assess endpoint: 
    - **path**: to a folder with ipynb files and one marks.json file for question tag to max_marks mapping
    - **check_duplicates**: if True, will check for duplicate files in the folder
    """

    start_time = time.time()
    total_usage, gpt_cost, run_report, api_call_count = await assessment_check.batch_assessment_check(
                                                        path=path,
                                                        check_duplicates=check_duplicates
                                                        )

    
    # Constructing the response
    latency = f"{round(time.time() - start_time, 2)} s"
    response = {
        "total_usage": total_usage,
        "gpt_cost": gpt_cost,
        "latency": latency,
        "report_count": len(run_report),
        "run_report": run_report,
        "api_call_count": api_call_count
    }

    return JSONResponse(content=response)

