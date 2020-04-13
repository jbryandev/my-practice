from importlib import import_module

class PDFConverterFactory:

    def __init__(self, agenda, progress_recorder):
        self.name = agenda.department.converter.name
        self.agenda = agenda
        self.progress_recorder = progress_recorder

    def create_converter(self):
        module_path = "council.modules"
        if not self.name == "PDFConverter":
            module_path = "council.converters"
        module = import_module("{}.{}".format(module_path, self.name))
        converter = getattr(module, self.name)(self.agenda, self.progress_recorder)
        return converter
