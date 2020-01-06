"""
This modules takes a URL of a PDF and converts the PDF
to text using tesseract. It returns the converted text
as a string.
"""
import io
import re
import requests
from celery import task
from pdf2image import convert_from_bytes
import pytesseract

@task
def convert_pdf(pdf_url, progress_observer):
    """
    Module function.
    """
    pdf_text = ""
    print("PDF2Text: Getting HTTP response...")
    response = requests.get(pdf_url)
    print("PDF2Text: Downloading PDF file...")
    file = io.BytesIO(response.content)
    print("PDF2Text: Converting PDF to images...")
    images = convert_from_bytes(file.read())
    i = 1
    for image in images:
        print("PDF2Text: Converting page " + str(i) + "...")
        pdf_text += str(((pytesseract.image_to_string(image))))
        print("PDF2Text: Conversion of page " + str(i) + " complete.")
        i += 1
        match = re.search("adjourn", pdf_text, re.IGNORECASE)
        if match:
            print("PDF2Text: Adjourn keyword found. PDF2Text operation complete.")
            break
        progress_observer.set_progress(image, len(images))

    return pdf_text
