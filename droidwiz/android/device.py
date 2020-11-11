class Device(object):
    def __init__(self, adb):
        self._adb = adb

    @property
    def name(self):
        return self._adb.name

    def get_screen_size(self):
        # TODO
        return (1080, 1920)

    def get_screen_aspect(self):
        return (lambda width, height: width / height)(*self.get_screen_size())

    def get_screenshot(self, png=True):
        # TODO: just generate dummy screenshot
        width, height = self.get_screen_size()
        screenshot = bytearray(width * height * 4)

        for i in range(width * height):
            screenshot[i*4:(i+1)*4] = (
                (i >> 0) & 0xFF,
                (i >> 8) & 0xFF,
                (i >> 16) & 0xFF,
                255,
            )

        return screenshot
