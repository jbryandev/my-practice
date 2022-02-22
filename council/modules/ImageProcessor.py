import cv2
import numpy as np
from PIL import Image

class ImageProcessor:

    def __init__(self, image):
        self.image = image

    def process(self):
        converted = self.convert(self.image)
        return converted
        # resized = self.resize(converted)
        # gray = self.get_grayscale(resized)
        # denoise = self.remove_noise(gray) # This step sometimes introduces artifacts in tesseract output
        # thresh = self.thresholding(denoise)
        # deskewed = self.deskew(thresh) # This step is causing tesseract to spit out gibberish
        # processed_img = Image.fromarray(deskewed)
        # return processed_img

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
