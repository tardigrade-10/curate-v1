from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import xml.etree.ElementTree as ET
from core.data_models import Service


class HTRService(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Any additional initialization for HTR-specific attributes

    def execute(self, input):
        """
        Override the execute method to include HTR specific execution logic
        """
        # Actual HTR processing logic here
        result = some_htr_processing_function(input)
        return result

    # You can override or add any other methods specific to HTR

