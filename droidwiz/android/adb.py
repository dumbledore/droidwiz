class ADB(object):
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    @staticmethod
    def create_default():
        return ADB("some_device")

    # list device, etc.
