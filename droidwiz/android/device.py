from droidwiz.android.adb import ADB
from droidwiz.android.services.input import Input
from droidwiz.android.services.wm import WindowManager


class Device(ADB):
    def __init__(self, name):
        super().__init__(name)

        self.wm = WindowManager(self)
        self.input = Input(self)

    def get_screenshot(self, png=True, display=0):
        return self.shell('screencap%s -d %d' % (" -p" if png else "", display))
