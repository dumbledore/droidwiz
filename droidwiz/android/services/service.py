import time


class Service(object):
    def __init__(self, adb,):
        self.adb = adb

    @property
    def name(self):
        raise NotImplementedError()

    FOUND_PATTERN = "Service {}: found"

    def is_running(self):
        out = self.adb.shell("service check " + self.name).decode('utf-8')

        return Service.FOUND_PATTERN.format(self.name) in out

    def wait_for(self, timeout=-1):
        left = timeout

        while (left > 0) or (timeout <= 0):
            if self.is_running():
                return

            time.sleep(1)
            left -= 1

        raise TimeoutError("Timed out waiting for " + self.name)
