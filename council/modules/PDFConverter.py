from abc import ABC
import io, re, requests
from pdf2image import convert_from_bytes
import pytesseract
from django.utils.html import linebreaks
from .ImageProcessor import ImageProcessor
from .OCRProcessor import OCRProcessor

class PDFConverter(ABC):

    def __init__(self, agenda, progress_recorder):
        self.agenda = agenda
        self.pdf_url = agenda.pdf_link
        self.progress_recorder = progress_recorder
        self.ocr_config = r'--oem 3 --psm 6'

    def __repr__(self):
        return "{} - {} Agenda".format(self.__class__.__name__, str(self.agenda))

    def convert(self):
        status = "Converting {} - {}: {}".format(
            self.agenda.department.agency,
            self.agenda.department,
            self.agenda
        )
        print(status)
        self.progress_recorder.update(0, 5, status)

        try:
            self.progress_recorder.update(1, 5, "Downloading PDF file...")
            request = self.request_pdf()
            file = self.read_pdf(request)
        except:
            print("ERROR: Unable to download PDF file.")
            raise

        try:
            self.progress_recorder.update(2, 5, "Converting PDF into images...")
            images = self.get_images(file)
        except:
            print("ERROR: Unable to create images.")
            raise

        self.progress_recorder.update(3, 5, "Extracting text using OCR...")
        pdf_text = ""
        for image in images:
            try:
                processed_image = self.process_image(image)
            except:
                print("ERROR: Unable to pre-process image.")
                raise
            try:
                # pdf_text += "{}".format(self.extract_text(processed_image))
                extracted_text = self.extract_text(processed_image)
            except:
                print("ERROR: Unable to extract text.")
                raise
            try:
                formatted_text = self.format_text(extracted_text)
                pdf_text += formatted_text
            except:
                print("ERROR: Unable to format text.")
                raise
            match = re.search("adjourn", pdf_text, re.IGNORECASE)
            if match:
                # Stop extracting when "adjorn" text is found (aka the end of the agenda)
                break
        try:
            self.agenda.agenda_text = pdf_text
            self.progress_recorder.update(4, 5, "Extraction complete. Saving PDF text to database...")
            self.agenda.save()
        except:
            print("ERROR: Unable to save agenda text.")
            raise
        return "Done."
        # return formatted_text

    def request_pdf(self):
        return requests.get(self.pdf_url)

    @staticmethod
    def read_pdf(request):
        return io.BytesIO(request.content)

    @staticmethod
    def get_images(pdf_file):
        return convert_from_bytes(pdf_file.read(), last_page=20)

    def process_image(self, pdf_image):
        # Crop image to remove unwanted headers/footers
        cropped_image = self.crop_image(pdf_image)
        # Run image through pre-processor to prep for OCR
        processor = ImageProcessor(cropped_image)
        return processor.process()

    def extract_text(self, pdf_image):
        # This method should be overriden by subclasses
        ocr = OCRProcessor()
        return ocr.process(pdf_image, config=self.ocr_config)

    def format_text(self, extracted_text):
        # This method should be overriden by subclasses
        return str(extracted_text)

    @staticmethod
    def crop_image(pdf_image):
        # This method should be overriden by subclasses
        return pdf_image
