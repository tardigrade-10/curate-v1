from __future__ import annotations

from typing import List
from pdf2image import convert_from_path
from PIL import Image


POPPLER_PATH=r"core/libs/poppler/Library/bin"


def doc_upload(file_path):
    with open(file_path, 'r') as f:
        f.read()
    return


def pdf_to_images(
        pdf_path=None,
        first_page=1,
        last_page=1,
    ) -> List[Image.Image]:
    
    images = convert_from_path(
        pdf_path=pdf_path,
        poppler_path=POPPLER_PATH
    )

    return images

