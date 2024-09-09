# Copyright (C) 2020-2024, Svetlin Ankov

import io
import wx
import wx.lib.newevent

from droidwiz.frontend.screenshot_thread import ScreenshotThread as ST


ScreenshotEvent, EVT_SCREENSHOT = wx.lib.newevent.NewEvent()


class ScreenshotThread(ST):
    def __init__(self, window, device, png, on_error):
        super().__init__(self._callback, self._on_error, device, png)

        self.window = window
        self.screen_size = device.wm.get_size()
        self.on_error = on_error

    def _callback(self, data, fps):
        if self.png:
            screenshot = wx.Image(io.BytesIO(data), wx.BITMAP_TYPE_PNG)

            # Raise if failed to create image from buffer
            if not screenshot.IsOk():
                raise Exception("Not a valid PNG")
        else:
            # the first 4 DWORDS are width, height, pixel format, data space
            # so skip the first 16 bytes
            screenshot = wx.Bitmap.FromBufferRGBA(
                *self.screen_size, data[16:]).ConvertToImage()

        event = ScreenshotEvent(screenshot=screenshot, fps=fps)
        wx.PostEvent(self.window, event)

    def _on_error(self, error):
        wx.CallAfter(self.on_error, error)
