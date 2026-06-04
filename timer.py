import time

class ResettableTimer:
    def __init__(self, duration):
        self.duration = duration
        self.start_time = time.time()

    def reset(self):
        self.start_time = time.time()

    def expired(self):
        return (time.time() - self.start_time) >= self.duration
