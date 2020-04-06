import io, os, re, requests, tempfile
from pdf2image import convert_from_path
import pytesseract
from .ImageProcessor import ImageProcessor

class PDFConverter:

    def __init__(self, pdf_url,):
        self.pdf_url = pdf_url
        self.temp_dir = tempfile.TemporaryDirectory()

    def convert_pdf(self):
        request = self.request_pdf()
        file = self.read_pdf(request)
        images = self.get_images(file)
        i = 1
        pdf_text = ""
        for image in images:
            processed_image = self.process_image(image)
            pdf_text += "{}".format(self.extract_text(processed_image))
            i += 1
            match = re.search("adjourn", pdf_text, re.IGNORECASE)
            if match:
                break
        return pdf_text

    def request_pdf(self):
        return requests.get(self.pdf_url)

    def read_pdf(self, request):
        return io.BytesIO(request.content)

    def get_images(self, pdf_file):
        images = None
        fh, temp_filename = tempfile.mkstemp()
        with open(temp_filename, "wb") as f:
            f.write(pdf_file.read())
            f.flush()
            images = convert_from_path(f.name)
        os.close(fh)
        os.remove(temp_filename)
        return images

    def process_image(self, pdf_image):
        processor = ImageProcessor(pdf_image)
        return processor.process()

    def extract_text(self, pdf_image):
        return pytesseract.image_to_string(pdf_image)
