import time

class ProgressObserver():

    def __init__(self, progress_recorder):
        self.progress_recorder = progress_recorder

    def update(self, start, end, message, delay=2):
        self.progress_recorder.set_progress(start, end, description=message)
        time.sleep(delay)
