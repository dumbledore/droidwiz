import re


class WindowManager(object):
    def __init__(self, adb):
        self.adb = adb

    GET_SIZE_PATTERN = re.compile('Physical size: (\d+)x(\d+)')

    def get_size(self):
        out = self.adb.shell('wm size').decode('utf-8')
        return tuple((int(x) for x in WindowManager.GET_SIZE_PATTERN.findall(out)[0]))

    def get_aspect(self):
        return (lambda width, height: width / height)(*self.get_size())
