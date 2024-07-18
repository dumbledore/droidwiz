import re

from droidwiz.android.services.service import Service

class WindowManager(Service):
    GET_SIZE_PATTERN = re.compile(r'Physical size: (\d+)x(\d+)')

    @property
    def name(self):
        return "window"

    def get_size(self):
        out = self.adb.shell('wm size')
        return tuple((int(x) for x in WindowManager.GET_SIZE_PATTERN.findall(out)[0]))

    def get_aspect(self):
        return (lambda width, height: width / height)(*self.get_size())
