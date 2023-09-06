from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import xml.etree.ElementTree as ET

pytesseract.pytesseract.tesseract_cmd = r'core\libs\tesseract\tesseract-ocr-w64.exe'

class HTR:
    def __init__(self, pdf_paths):
        self.pdf_paths = pdf_paths
        self.xml_data = []
    
    def pdf_to_image(self, pdf_path):
        return convert_from_path(pdf_path)
    
    def ocr_image(self, image):
        # Assuming we want to use pytesseract for OCR
        hocr = pytesseract.image_to_pdf_or_hocr(image, extension='hocr')
        return hocr.decode('utf-8')
    
    def process_pdf(self, pdf_path):
        images = self.pdf_to_image(pdf_path)
        for i, image in enumerate(images):
            hocr_data = self.ocr_image(image)
            self.xml_data.append({
                'page': i + 1,
                'hocr_data': hocr_data
            })
    
    def process_pdfs(self):
        for pdf_path in self.pdf_paths:
            self.process_pdf(pdf_path)
    
    def get_xml_data(self):
        return self.xml_data


# if __name__ == '__main__':
#     # Initialize the HTR class with some example PDFs
#     htr = HTR(['example1.pdf', 'example2.pdf'])
    
#     # Process the PDFs
#     htr.process_pdfs()
    
#     # Get the processed XML data
#     xml_data = htr.get_xml_data()
    
#     # For demonstration, let's just print out the XML data for the first page of the first PDF
#     if xml_data:
#         print(xml_data[0]['hocr_data'])
