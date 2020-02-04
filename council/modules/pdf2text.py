"""
This modules takes a URL of a PDF and converts the PDF
to text using tesseract. It returns the converted text
as a string.
"""
import time
import io
import re
import requests
from pdf2image import convert_from_bytes
import pytesseract

def convert_pdf(pdf_url, progress_recorder):
    """
    Module function.
    """
    pdf_text = ""

    print("PDF2Text: Getting HTTP response...")
    response = requests.get(pdf_url)

    print("PDF2Text: Downloading PDF file...")
    progress_recorder.set_progress(1, 15, description="Connection successful. Downloading PDF...")
    file = io.BytesIO(response.content)
    time.sleep(3)

    print("PDF2Text: Converting PDF to images...")
    progress_recorder.set_progress(2, 15, description="Download complete. Getting page count...")
    images = convert_from_bytes(file.read())
    time.sleep(3)

    i = 1
    for image in images:
        print("PDF2Text: Converting page " + str(i) + "...")
        progress_desc = "Converting page " + str(i) + " of " + str(len(images)) + "..."
        progress_recorder.set_progress(i + 2, len(images) + 3, description=progress_desc)
        pdf_text += str(((pytesseract.image_to_string(image))))
        print("PDF2Text: Conversion of page " + str(i) + " complete.")
        i += 1
        match = re.search("adjourn", pdf_text, re.IGNORECASE)
        if match:
            print("PDF2Text: Adjourn keyword found. PDF2Text operation complete.")
            break

    return pdf_text
