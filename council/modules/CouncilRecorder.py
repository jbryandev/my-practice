import time
from celery_progress.backend import ProgressRecorder

class CouncilRecorder(ProgressRecorder):

    def update(self, start, end, message, delay=1):
        self.set_progress(start, end, message)
        time.sleep(delay)
