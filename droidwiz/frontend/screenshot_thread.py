import threading
import time


class ScreenshotThread(threading.Thread):
    def __init__(self, callback, device, png=True):
        super().__init__()

        self.callback = callback
        self.device = device
        self.png = png

        self.timestamp = time.time()
        self.count = 0
        self.fps = 0

        self.stopping = False
        self.start()

    def update_screenshot(self):
        data = self.device.get_screenshot(self.png)

        self.count += 1
        timestamp = time.time()
        elapsed = timestamp - self.timestamp
        if elapsed >= 5:
            self.fps = self.count / elapsed
            self.timestamp = timestamp
            self.count = 0

        self.callback(data, self.fps)

    def run(self):
        while not self.stopping:
            self.update_screenshot()

    def stop(self):
        self.stopping = True
        self.join()
