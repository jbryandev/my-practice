import os
import tempfile
import subprocess

class OCRProcessor:

    def process(self, image, config, extension):
        output_file = tempfile.NamedTemporaryFile(delete=False)
        input_file = tempfile.NamedTemporaryFile(delete=False)
        input_file_name = input_file.name + os.extsep + "ppm"
        image.save(input_file_name, "ppm")
        process = subprocess.Popen(['tesseract', input_file_name, output_file.name, config, extension], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        process.communicate()

        with open(output_file.name, 'r') as handle:
            contents = handle.read()

        os.remove(output_file.name + '.txt')
        os.remove(output_file.name)
        os.remove(input_file.name)

        return contents
