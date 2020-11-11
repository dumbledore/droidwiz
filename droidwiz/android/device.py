from droidwiz.android.wm import WindowManager


class Device(object):
    def __init__(self, adb):
        self.adb = adb
        self.wm = WindowManager(adb)

        # TODO: remove
        self.screenshot = self.generate_screenshot()

    @property
    def name(self):
        return self.adb.name

    def get_screenshot(self, png=True):
        # TODO: FIX
        if png:
            raise Exception("PNG not supported")

        return self.screenshot

    # TODO: remove
    def generate_screenshot(self):
        width, height = self.wm.get_size()
        screenshot = bytearray(width * height * 4)

        for i in range(width * height):
            screenshot[i*4:(i+1)*4] = (
                (i >> 0) & 0xFF,
                (i >> 8) & 0xFF,
                (i >> 16) & 0xFF,
                255,
            )

        return screenshot
