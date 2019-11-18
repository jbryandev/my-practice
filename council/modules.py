# File for custom functions to be used by council app
# This makes functions more reusable for other apps
import requests
import io
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image

def pdf2text(pdf_url):
        # Takes a URL of a PDF and converts the PDF to text using tesseract
        # Returns the converted text as a string
        pdf_text = ""
        r = requests.get(pdf_url)
        f = io.BytesIO(r.content)
        images = convert_from_bytes(f.read())
        for image in images:
            pdf_text += str(((pytesseract.image_to_string(image)))) 
        return pdf_text