"""
This modules takes a URL of a PDF and converts the PDF
to text using tesseract. It returns the converted text
as a string.
"""
import io
import re
import requests
from pdf2image import convert_from_bytes
import pytesseract
from celery_progress.backend import ProgressRecorder

def convert_pdf(self, pdf_url):
    """
    Module function.
    """
    progress_recorder = ProgressRecorder(self)
    pdf_text = ""
    print("PDF2Text: Getting HTTP response...")
    response = requests.get(pdf_url)
    print("PDF2Text: Downloading PDF file...")
    file = io.BytesIO(response.content)
    print("PDF2Text: Converting PDF to images...")
    images = convert_from_bytes(file.read())
    i = 1
    for image in images:
        progress_recorder.set_progress(images, len(images))
        print("PDF2Text: Converting page " + str(i) + "...")
        pdf_text += str(((pytesseract.image_to_string(image))))
        print("PDF2Text: Conversion of page " + str(i) + " complete.")
        i += 1
        match = re.search("adjourn", pdf_text, re.IGNORECASE)
        if match:
            print("PDF2Text: Adjourn keyword found. PDF2Text operation complete.")
            break

    return pdf_text
