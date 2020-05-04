import os, tempfile, subprocess, shlex

class OCRProcessor:

    def process(self, image, config="", mode=""):
        with tempfile.TemporaryDirectory() as tmpdir:
            image.save(os.path.join(tmpdir, "input.ppm"))
            command = "tesseract input.ppm output {} {}".format(config, mode)
            process = subprocess.Popen(
                shlex.split(command),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=tmpdir
            )
            process.communicate()
            extension = "txt"
            if mode == "hocr":
                extension = mode
            output_file_name = ('%s.%s' % (os.path.join(tmpdir, "output"), extension))
            with open(output_file_name, 'r') as handle:
                contents = handle.read()
            os.remove(output_file_name)
        return contents
