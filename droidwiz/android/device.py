from droidwiz.android.adb import ADB
from droidwiz.android.input import Input
from droidwiz.android.wm import WindowManager


class Device(ADB):
    def __init__(self, name):
        super().__init__(name)

        self.wm = WindowManager(self)
        self.input = Input(self)

    def get_screenshot(self, png=True):
        return self.shell('screencap%s' % (" -p" if png else ""))
