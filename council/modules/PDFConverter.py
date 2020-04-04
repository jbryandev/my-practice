import io
import re
import requests
from pdf2image import convert_from_bytes
import pytesseract
from .ImageProcessor import ImageProcessor

class PDFConverter:

    def __init__(self, pdf_url):
        self.pdf_url = pdf_url

    def convert_pdf(self):
        request = self.request_pdf()
        file = self.read_pdf(request)
        images = self.get_images(file)
        i = 1
        pdf_text = ""
        for image in images:
            status = "Converting page {} of {}...".format(i, len(images))
            print("PDF2Text: {}".format(status))
            processed_image = self.process_image(image)
            pdf_text += "{}".format(self.extract_text(processed_image))
            print("PDF2Text: Conversion of page " + str(i) + " complete.")
            i += 1
            match = re.search("adjourn", pdf_text, re.IGNORECASE)
            if match:
                print("PDF2Text: Adjourn keyword found. PDF2Text operation complete.")
                break
        return pdf_text

    def request_pdf(self):
        print("PDF2Text: Getting HTTP response...")
        return requests.get(self.pdf_url)

    def read_pdf(self, request):
        print("PDF2Text: Downloading PDF file...")
        return io.BytesIO(request.content)

    def get_images(self, pdf_file):
        print("PDF2Text: Converting PDF to images...")
        return convert_from_bytes(pdf_file.read())

    def process_image(self, pdf_image):
        print("PDF2Text: Pre-processing image...")
        processor = ImageProcessor(pdf_image)
        return processor.process()

    def extract_text(self, pdf_image):
        print("PDF2Text: Extracting text using OCR...")
        return pytesseract.image_to_string(pdf_image)
