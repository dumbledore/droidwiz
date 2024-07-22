# Copyright (C) 2020-2024, Svetlin Ankov

import threading
import time


class ScreenshotThread(threading.Thread):
    def __init__(self, callback, error_callback, device, png=True):
        super().__init__()

        self.callback = callback
        self.error_callback = error_callback
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
            try:
                self.update_screenshot()
            except Exception as e:
                self.error_callback(e)
                time.sleep(1)

    def stop(self):
        self.stopping = True
        self.join()
