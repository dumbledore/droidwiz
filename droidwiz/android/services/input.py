# Copyright (C) 2020-2024, Svetlin Ankov

from droidwiz.android.services.service import Service


class Input(Service):
    def __init__(self, adb):
        self.adb = adb

    @property
    def name(self):
        return "input"

    def tap(self, pos):
        self.adb.shell('input tap {} {}'.format(*pos))

    def swipe(self, start, end, duration):
        self.adb.shell('input swipe {} {} {} {} {}'.format(
            start[0], start[1], end[0], end[1], duration
        ))

    def text(self, text):
        self.adb.shell(f'input text "{text}"')

    # see https://developer.android.com/reference/android/view/KeyEvent
    def keyevent(self, key):
        self.adb.shell(f'input keyevent KEYCODE_{key.upper()}')
