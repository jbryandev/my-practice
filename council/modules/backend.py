""" Backend classes and methods for council app """
import time
import io
import re
import requests
import cv2
import numpy as np
from pdf2image import convert_from_bytes
import pytesseract
from celery_progress.backend import ProgressRecorder

class ImageProcessor:

    def __init__(self, image):
        self.image = image

    def process(self):
        converted = self.convert(self.image)
        resized = self.resize(converted)
        gray = self.get_grayscale(resized)
        denoise = self.remove_noise(gray)
        thresh = self.thresholding(denoise)
        processed_img = self.deskew(thresh)
        return processed_img

    # convert image to opencv format
    def convert(self, image):
        return np.array(image)

    # resize image
    def resize(self, image):
        return cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # get grayscale image
    def get_grayscale(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # noise removal
    def remove_noise(self, image):
        return cv2.medianBlur(image,5)

    #thresholding
    def thresholding(self, image):
        return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    #dilation
    def dilate(self, image):
        kernel = np.ones((5,5),np.uint8)
        return cv2.dilate(image, kernel, iterations=1)

    #erosion
    def erode(self, image):
        kernel = np.ones((5,5),np.uint8)
        return cv2.erode(image, kernel, iterations=1)

    #opening - erosion followed by dilation
    def opening(self, image):
        kernel = np.ones((5,5),np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

    #canny edge detection
    def canny(self, image):
        return cv2.Canny(image, 100, 200)

    #skew correction
    def deskew(self, image):
        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    #template matching
    def match_template(self, image, template):
        return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

class PDFConverter:

    def __init__(self, pdf_url):
        self.pdf_url = pdf_url

    def convert_pdf(self, progress_recorder):
        request = self.request_pdf()
        set_progress(progress_recorder, 1, 15, "Connection successful. Downloading PDF...")
        file = self.read_pdf(request)
        set_progress(progress_recorder, 2, 15, "Download complete. Getting page count...")
        images = self.get_images(file)
        i = 1
        pdf_text = ""
        for image in images:
            progress_desc = "Converting page {} of {}...".format(i, len(images))
            print("PDF2Text: {}".format(progress_desc))
            set_progress(progress_recorder, i + 2, len(images) + 3, progress_desc)
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

# Depricated; use CouncilRecorder
def set_progress(progress_recorder, start, end, descr, delay=1):
    """ This function controls a progress recorder instance """
    progress_recorder.set_progress(start, end, description=descr)
    time.sleep(delay)

class CouncilRecorder(ProgressRecorder):

    def update(self, start, end, message, delay=1):
        self.set_progress(start, end, message)
        time.sleep(delay)
