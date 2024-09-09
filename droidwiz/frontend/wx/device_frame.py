# Copyright (C) 2020-2024, Svetlin Ankov

import sys
import wx

from droidwiz.android.resources.icons import get_icon
from .button_window import ButtonWindow
from .screenshot_thread import ScreenshotThread, EVT_SCREENSHOT

ALLOWED_KEYS = "1234567890-=!@#$%^&*()_+qwertyuiop[]QWERTYUIOP{}asdfghjkl;'\\ASDFGHJKL:\"|`zxcvbnm,./~ZXCVBNM<>? "

ESCAPED_KEYS = {
    '"': '\\"',
    '`': '\\`',
    '\\': '\\\\',
}


SPECIAL_KEYS = {
    wx.WXK_TAB: "tab",
    wx.WXK_RETURN: "enter",
    wx.WXK_ESCAPE: "escape",
    wx.WXK_BACK: "del",
    wx.WXK_DELETE: "forward_del",
    wx.WXK_INSERT: "insert",
    wx.WXK_LEFT: "dpad_left",
    wx.WXK_RIGHT: "dpad_right",
    wx.WXK_UP: "dpad_up",
    wx.WXK_DOWN: "dpad_down",
    wx.WXK_HOME: "move_home",
    wx.WXK_END: "move_end",
    wx.WXK_PAGEUP: "page_up",
    wx.WXK_PAGEDOWN: "page_down",
    wx.WXK_VOLUME_MUTE: "volume_mute",
    wx.WXK_VOLUME_UP: "volume_up",
    wx.WXK_VOLUME_DOWN: "volume_down",
}

# TODO: Use input keycombination KEYCODE_SHIFT_LEFT KEYCODE_A, etc. instead of input text


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

        self.buttons = ButtonWindow(self, [
            (get_icon("emulator-power"), lambda _: self.device.input.keyevent("power")),
            (get_icon("emulator-volume-up"), lambda _: self.device.input.keyevent("volume_up")),
            (get_icon("emulator-volume-down"), lambda _: self.device.input.keyevent("volume_down")),
            (get_icon("emulator-screenshot"), None),
            (get_icon("emulator-back"), lambda _: self.device.input.keyevent("back")),
            (get_icon("emulator-home"), lambda _: self.device.input.keyevent("home")),
            (get_icon("emulator-apps"), lambda _: self.device.input.keyevent("app_switch")),
        ])

        self.buttons.Show()

        self.Bind(wx.EVT_MOVE, self.on_move)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.panel = wx.Panel()
        self.panel.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.panel.Create(self)
        self.panel.Bind(wx.EVT_PAINT, self.on_paint)
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_down)
        self.panel.Bind(wx.EVT_LEFT_UP, self.on_mouse_up)
        self.panel.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.panel.Bind(wx.EVT_CHAR_HOOK, self.on_char)

        size = self.FromDIP(self.choose_size(size_divisor))
        self.SetClientSize(size)
        self.panel.SetClientSize(size)

        self.pos = None
        self.timestamp = None
        self.moved = False

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
            keycode = keycode.upper() if event.ShiftDown() else keycode.lower()
            self.device.input.text(keycode)
        else:
            # It's a special key, deal with all the known ones:
            keycode = event.GetKeyCode()
            if keycode in SPECIAL_KEYS:
                keycode = SPECIAL_KEYS[keycode]
                self.device.input.keyevent(keycode)

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

    def update_buttons(self):
        main_pos = self.GetPosition()
        main_size = self.GetSize()
        new_x = main_pos.x + main_size.x  # Right of main frame
        new_y = main_pos.y  # Align with top
        self.buttons.SetPosition((new_x, new_y))

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

    def on_move(self, event):
        self.update_buttons()
        event.Skip()

    def on_size(self, event):
        width, _ = self.GetClientSize()
        size = (width, int(width / self.screen_aspect))

        if self.GetClientSize() != size:
            self.SetClientSize(size)
            self.panel.SetClientSize(size)
            self.update_buttons()
            event.Skip()

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self.panel)
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
