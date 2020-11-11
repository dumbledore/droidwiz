import wx

import droidwiz.android.device


class DeviceFrame(wx.Frame):
    def __init__(self, device, *args, **kwargs):
        super().__init__(None, title=device.name, *args, **kwargs)

        self.device = device
        self.screen_size = device.get_screen_size()
        self.screen_aspect = device.get_screen_aspect()
        self.bmp = self.device.get_screenshot()

        self.SetClientSize(self.FromDIP(self.choose_size()))
        self.SetPosition((self.FromDIP(50),) * 2)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_up)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)

        self.pos = None
        self.timestamp = None

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.statusbar = self.CreateStatusBar()

    def choose_size(self):
        size = self.screen_size
        divisor = max(size) // 640
        return [ s // divisor for s in size ]

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
            self.statusbar.SetStatusText("[down] {} -> {}".format(event.GetPosition(), self.pos))

    def on_mouse_move(self, event):
        if self.pos and self.timestamp:
            elapsed = event.Timestamp - self.timestamp

            # Skip events out of the screen
            x, y, inside = self.get_coord_inside(event.GetPosition())

            if inside and elapsed > 250 and self.pos != (x, y):
                self.pos = x, y
                self.timestamp = event.Timestamp
                self.statusbar.SetStatusText("[drag] {} -> {}".format(event.GetPosition(), self.pos))

    def on_mouse_up(self, event):
        self.pos = None
        self.timestamp = None

        x, y, inside = self.get_coord_inside(event.GetPosition())
        if inside:
            new_pos = x, y
            self.statusbar.SetStatusText("[up] {} -> {}".format(event.GetPosition(), new_pos))

    def on_size(self, event):
        width, _ = self.GetClientSize()
        size = (width, int(width / self.device.get_screen_aspect()))
        print(self.GetClientSize())

        if self.GetClientSize() != size:
            self.SetClientSize(size)

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC (self)
        bmp = wx.Bitmap.FromBufferRGBA(*self.device.get_screen_size(), self.bmp)
        img = bmp.ConvertToImage()
        img.Rescale(*self.GetSize(), wx.IMAGE_QUALITY_HIGH)
        dc.DrawBitmap(img.ConvertToBitmap(), 0, 0)
