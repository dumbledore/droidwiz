# Copyright (C) 2020-2024, Svetlin Ankov

import sys
import wx

from .screenshot_thread import ScreenshotThread, EVT_SCREENSHOT

ALLOWED_KEYS = "1234567890-=!@#$%^&*()_+qwertyuiop[]QWERTYUIOP{}asdfghjkl;'\\ASDFGHJKL:\"|`zxcvbnm,./~ZXCVBNM<>?"

ESCAPED_KEYS = {
    '"': '\\"',
    '`': '\\`',
    '\\': '\\\\',
}


class DeviceFrame(wx.Frame):
    def __init__(self, device,
                 png=True,
                 resize_quality=wx.IMAGE_QUALITY_NORMAL,
                 size_divisor=640,
                 *args, **kwargs):

        self.device = device
        self.screen_size = device.wm.get_size()
        self.screen_aspect = device.wm.get_aspect()
        self.resize_quality = resize_quality
        self.screenshot = None
        self.png = png

        super().__init__(None, title=device.name, *args, **kwargs)

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.panel = wx.Panel(self, wx.ID_ANY)
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_down)
        self.panel.Bind(wx.EVT_LEFT_UP, self.on_mouse_up)
        self.panel.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.panel.Bind(wx.EVT_CHAR, self.on_char)
        self.panel.SetFocus()

        size = self.FromDIP(self.choose_size(size_divisor))
        self.SetClientSize(size)
        self.panel.SetClientSize(size)

        self.pos = None
        self.timestamp = None
        self.moved = False

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.statusbar = self.CreateStatusBar(2)

        self.Bind(EVT_SCREENSHOT, self.update_screenshot)
        self.screenshot_thread = ScreenshotThread(
            self, device, png, self.on_error)

    def on_char(self, event):

        keycode = event.GetUnicodeKey()

        if keycode != wx.WXK_NONE and chr(keycode) in ALLOWED_KEYS:
            # It's a printable character
            keycode = chr(keycode)
            keycode = ESCAPED_KEYS.get(keycode, keycode)
            self.device.input.text(keycode)
        else:
            # It's a special key, deal with all the known ones:
            keycode = event.GetKeyCode()
            print(f"keycode: {keycode}")

    def choose_size(self, size_divisor):
        size = self.screen_size
        divisor = max(size) // size_divisor
        return [s // divisor for s in size]

    def get_coord(self, pos):
        w, h = self.screen_size
        cw, ch = self.GetClientSize()
        acw, ach = w / cw, h / ch
        x, y = pos
        return int(x * acw), int(y * ach)

    def get_coord_inside(self, pos):
        w, h = self.screen_size
        x, y = self.get_coord(pos)
        inside = (0 <= x < w) and (0 <= y < h)

        return x, y, inside

    def get_coord_clipped(self, pos):
        w, h = self.screen_size
        x, y = self.get_coord(pos)
        x = min(max(x, 0), w - 1)
        y = min(max(y, 0), h - 1)

        return x, y

    def on_mouse_down(self, event):
        x, y, inside = self.get_coord_inside(event.GetPosition())
        if inside:
            self.pos = x, y
            self.timestamp = event.Timestamp
            self.statusbar.SetStatusText("[down] {}".format(self.pos))

    def on_mouse_move(self, event):
        if self.pos:
            # Skip events out of the screen
            x, y, inside = self.get_coord_inside(event.GetPosition())

            if inside and self.pos != (x, y):
                self.moved = True
                self.statusbar.SetStatusText("[drag] {}".format((x, y)))

    def on_mouse_up(self, event):
        x, y, inside = self.get_coord_inside(event.GetPosition())
        if inside and self.pos:
            new_pos = x, y
            self.statusbar.SetStatusText("[up] {}".format(new_pos))

            if self.moved:
                elapsed = event.Timestamp - self.timestamp
                self.device.input.swipe(self.pos, new_pos, elapsed)
            else:
                self.device.input.tap(new_pos)

        self.pos = None
        self.timestamp = None
        self.moved = False

    def on_size(self, event):
        width, _ = self.GetClientSize()
        size = (width, int(width / self.screen_aspect))

        if self.GetClientSize() != size:
            self.SetClientSize(size)
            self.panel.SetClientSize(size)

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        if self.screenshot:
            img = self.screenshot
            img = img.Scale(*self.GetClientSize(), self.resize_quality)
            dc.DrawBitmap(img.ConvertToBitmap(), 0, 0)

    def update_screenshot(self, event):
        self.screenshot = event.screenshot
        self.statusbar.SetStatusText("%.2f FPS (%s)" % (
            event.fps, "PNG" if self.png else "RAW"), 1)
        self.Refresh()

    def on_error(self, error):
        self.statusbar.SetStatusText(f"Error: {error}")
        print(error, sys.stderr)

    def on_close(self, event):
        self.screenshot_thread.stop()
        event.Skip()
