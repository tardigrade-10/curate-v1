
from pdf2image import convert_from_path


POPPLER_PATH = r"C:\Users\DELL\Documents\Curate\curate-v1\core\libs\poppler\Library\bin"

def pdf_to_image(pdf_path, image_folder_path, grayscale = True):
    images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH, dpi= 100, grayscale=True)

    images_folder = image_folder_path
    for i, img in enumerate(images):
        img.save(images_folder + "/phy_image"+str(i+1)+".jpg")



