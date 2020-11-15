import re
import wx

from droidwiz.android.adb import ADB


class ListDevicesFrame(wx.Frame):
    def __init__(self, on_select, *args, **kwargs):
        super().__init__(None, title="Devices", *args, **kwargs)

        self.on_select = on_select

        self.devices = [ ]

        panel = wx.Panel(self)

        self.list = wx.ListBox(panel)
        button_panel = wx.Panel(panel)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list, 4, wx.EXPAND)
        sizer.Add(button_panel, -1, wx.EXPAND)
        panel.SetSizer(sizer)
        panel.Fit()

        self.start_button = wx.Button(button_panel, label="Start")
        self.start_button.Disable()
        self.start_button.Bind(wx.EVT_BUTTON, self.on_start_device)

        self.connect_button = wx.Button(button_panel, label="Connect")
        self.connect_button.Bind(wx.EVT_BUTTON, self.on_connect)

        self.disconnect_button = wx.Button(button_panel, label="Disconnect")
        self.disconnect_button.Disable()
        self.disconnect_button.Bind(wx.EVT_BUTTON, self.on_disconnect)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.start_button)
        sizer.Add(self.connect_button)
        sizer.Add(self.disconnect_button)
        button_panel.SetSizer(sizer)
        button_panel.Fit()

        self.Bind(wx.EVT_LISTBOX, self.on_select_device)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.on_start_device)

        self.timer = wx.Timer(self, 0)
        self.Bind(wx.EVT_TIMER, self.update_devices)
        self.timer.Start(1000)

        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.update_devices()

    def update_devices(self, event=None):
        devices = sorted(ADB.list_devices())

        if self.devices != devices:
            self.start_button.Disable()
            self.disconnect_button.Disable()

            self.devices = devices
            self.list.Clear()
            for device in devices:
                self.list.Append(device)

    NET_DEVICE = re.compile(r'(.*):(\d+)')

    def on_select_device(self, event):
        self.start_button.Enable()

        sel = self.list.GetSelection()
        device = self.list.GetString(sel)

        self.disconnect_button.Enable(bool(
                ListDevicesFrame.NET_DEVICE.fullmatch(device)))

    def on_start_device(self, event):
        sel = self.list.GetSelection()
        device = self.list.GetString(sel)

        self.on_select(device)

    def on_connect(self, event):
        device = wx.GetTextFromUser('Enter device: IP[:PORT]', 'Connect device')
        if device:
            port = ADB.PORT
            full_device = ListDevicesFrame.NET_DEVICE.findall(device)
            if full_device:
                device, port = full_device[0]

            ADB.connect(device, port)
            self.update_devices()

    def on_disconnect(self, event):
        sel = self.list.GetSelection()
        device = self.list.GetString(sel)

        device = ListDevicesFrame.NET_DEVICE.findall(device)
        ADB.disconnect(*device[0])
        self.update_devices()

    def on_close(self, event):
        self.timer.Stop()
        event.Skip()
