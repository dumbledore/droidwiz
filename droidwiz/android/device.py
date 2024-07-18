# Copyright (C) 2020-2024, Svetlin Ankov

from droidwiz.android.adb import ADB
from droidwiz.android.services.input import Input
from droidwiz.android.services.wm import WindowManager


class Device(ADB):
    def __init__(self, name):
        super().__init__(name)

        self.wm = WindowManager(self)
        self.input = Input(self)

    def get_screenshot(self, png=True, display=None):
        cmd = [
            "screencap"
        ]

        if display is not None:
            cmd += [
                "-d", str(display),
            ]

        if png:
            cmd += ["-p"]

        return self.exec_out(" ".join([str(x) for x in cmd]))
