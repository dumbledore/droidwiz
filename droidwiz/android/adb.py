# TODO: Support for different ADB versions
# verified with adb:
# 30.0.5-6877874
import re
import subprocess


class ADB(object):
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def shell(self, command):
        return subprocess.check_output(
            [ 'adb', 'shell', command ]
        )

    @staticmethod
    def create_default():
        devices = ADB.list_devices()

        if not devices:
            raise Exception("No devices found")
        elif len(devices) > 1:
            raise Exception("Multiple devices found")

        return ADB(devices[0])

    DEVICES_PATTERN = re.compile(r'^(.*?)\W+device$', re.MULTILINE)

    @staticmethod
    def list_devices():
        out = subprocess.check_output(
            [ 'adb', 'devices' ]
        ).decode('utf-8')

        return ADB.DEVICES_PATTERN.findall(out)
