from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict
from uuid import uuid4
import io
import os
from PIL import Image
import pytesseract
from core.features.htp.htp import htr_batch_process
from core.features.utils import pdf_to_images, calculate_cost_gpt4_turbo, add_dicts


STORAGE = r"C:\Users\DELL\Documents\Curate\curate-v1\core\storage"
# Initialize the FastAPI app
app = FastAPI()

@app.post("/htp_batch")
async def text_recognition(file: UploadFile = File(...), page_start: int = 1, page_end: int = 1) -> JSONResponse:

    file_ext = file.filename.split('.')[-1] in ("pdf", "PDF")
    if not file_ext:
        raise HTTPException(status_code=400, detail="Invalid file format")


    file_id = str(uuid4())
    file_path = f"{STORAGE}/{file_id}.{file_ext}"
    output_folder = f"{STORAGE}/{file_id}"

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    pdf_to_images(file_path, output_folder, page_start, page_end)
    image_paths = [os.path.join(output_folder, x) for x in os.listdir(output_folder)]
    batch_names, final_text, total_tokens = htr_batch_process(image_paths = image_paths, batch_size = 1)
    cost = calculate_cost_gpt4_turbo(total_tokens)

    # Constructing the response
    response = {
        "filename": file.filename,
        "content_type": file.content_type,
        "recognized_text": final_text,
        "token_usage": total_tokens,
        "cost": cost
    }

    return JSONResponse(content=response)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
