from droidwiz.android.wm import WindowManager


class Device(object):
    def __init__(self, adb):
        self.adb = adb
        self.wm = WindowManager(adb)

    @property
    def name(self):
        return self.adb.name

    def get_screenshot(self, png=True):
        return self.adb.shell('screencap%s' % (" -p" if png else ""))
