import io, re, requests
from pdf2image import convert_from_bytes
import pytesseract
from .ImageProcessor import ImageProcessor

class PDFConverter:

    def __init__(self, agenda, progress_recorder):
        self.agenda = agenda
        self.pdf_url = agenda.pdf_link
        self.progress_recorder = progress_recorder

    def __repr__(self):
        return "{} Agenda PDFConverter".format(str(self.agenda))

    def convert_pdf(self):
        status = "Converting {} - {}: {}".format(
            self.agenda.department.agency,
            self.agenda.department,
            self.agenda
        )
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
            print("({} image(s) created)".format(len(images)))
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
                pdf_text += "{}".format(self.extract_text(image))
            except:
                print("ERROR: Unable to extract text.")
                raise
            match = re.search("adjourn", pdf_text, re.IGNORECASE)
            if match:
                # Stop extracting when "adjorn" text is found (aka the end of the agenda)
                print("Adjourn keyword found. No further extraction necessary.")
                break
        try:
            self.agenda.agenda_text = pdf_text
            self.progress_recorder.update(4, 5, "Extraction complete. Saving PDF text to database...")
            self.agenda.save()
        except:
            print("ERROR: Unable to save agenda text.")
            raise
        return "Done."

    def request_pdf(self):
        return requests.get(self.pdf_url)

    @staticmethod
    def read_pdf(request):
        return io.BytesIO(request.content)

    @staticmethod
    def get_images(pdf_file):
        return convert_from_bytes(pdf_file.read(), last_page=20)

    @staticmethod
    def process_image(pdf_image):
        processor = ImageProcessor(pdf_image)
        return processor.process()

    @staticmethod
    def extract_text(pdf_image):
        return pytesseract.image_to_string(pdf_image)
