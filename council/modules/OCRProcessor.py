import os
import tempfile
import subprocess

class OCRProcessor:

    def process(self, image, config, extension):
        # output_file = tempfile.NamedTemporaryFile(delete=False)
        # input_file = tempfile.NamedTemporaryFile(delete=False)
        # input_file_name = input_file.name + os.extsep + "ppm"
        # output_file_name = output_file.name + os.extsep + "txt"
        # image.save(input_file_name, "ppm")
        # process = subprocess.Popen(['tesseract', input_file_name, output_file_name, config, extension], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # process.communicate()

        # with open(output_file.name, 'r') as handle:
        #     contents = handle.read()

        # os.remove(output_file.name + '.hocr')
        # os.remove(output_file.name)
        # os.remove(input_file.name)

        with tempfile.TemporaryDirectory() as tmpdir:
            image.save(os.path.join(tmpdir, "input.ppm"))
            process = subprocess.Popen(['tesseract', "input.ppm", "output", config, extension], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=tmpdir)
            process.communicate()
            output_file_name = ('%s.%s' % (os.path.join(tmpdir, "output"), "txt"))
            with open(output_file_name, 'r') as handle:
                contents = handle.read()

        return contents
