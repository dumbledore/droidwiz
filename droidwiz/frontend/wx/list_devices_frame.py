# Copyright (C) 2020-2024, Svetlin Ankov

import subprocess
import re
import wx

from droidwiz.android.adb import ADB


class ListDevicesFrame(wx.Frame):
    def __init__(self, on_select, *args, **kwargs):
        super().__init__(None, title="Devices", *args, **kwargs)

        self.on_select = on_select

        self.devices = []

        panel = wx.Panel(self)

        device_panel = wx.Panel(panel)
        self.list = wx.ListBox(device_panel)

        # Buttons that work on a selected device
        self.device_buttons = wx.Panel(device_panel)
        sizer = wx.BoxSizer(wx.VERTICAL)

        def add_device_button(name, cb):
            button = wx.Button(self.device_buttons, label=name)
            button.Bind(wx.EVT_BUTTON, cb)
            sizer.Add(button, 0, wx.EXPAND)

        add_device_button("Start", self.on_start_device)
        add_device_button("Root", lambda _: self.run_adb_command(["root"]))
        add_device_button("Unroot", lambda _: self.run_adb_command(["unroot"]))
        add_device_button(
            "Remount", lambda _: self.run_adb_command(["remount"]))
        add_device_button("Reboot", lambda _: self.run_adb_command(["reboot"]))
        add_device_button("Bootloader", lambda _: self.run_adb_command(
            ["reboot", "bootloader"]))

        self.device_buttons.Disable()
        self.device_buttons.SetSizer(sizer)
        self.device_buttons.Fit()

        # Buttons that don't require a selected device
        button_panel = wx.Panel(panel)
        self.connect_button = wx.Button(button_panel, label="Connect")
        self.connect_button.Bind(wx.EVT_BUTTON, self.on_connect)

        self.disconnect_button = wx.Button(button_panel, label="Disconnect")
        self.disconnect_button.Disable()
        self.disconnect_button.Bind(wx.EVT_BUTTON, self.on_disconnect)

        # device panel (list + buttons)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.list, 4, wx.EXPAND)
        sizer.Add(self.device_buttons, -1, wx.EXPAND)
        device_panel.SetSizer(sizer)
        device_panel.Fit()

        # buttons on the lower part
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.connect_button)
        sizer.Add(self.disconnect_button)
        button_panel.SetSizer(sizer)
        button_panel.Fit()

        # main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(device_panel, 4, wx.EXPAND)
        sizer.Add(button_panel, -1, wx.EXPAND)
        panel.SetSizer(sizer)
        panel.Fit()

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
            self.device_buttons.Disable()
            self.disconnect_button.Disable()

            self.devices = devices
            self.list.Clear()
            for device in devices:
                self.list.Append(device)

    NET_DEVICE = re.compile(r'(.*):(\d+)')

    def run_adb_command(self, command):
        try:
            ADB(self.get_selected_device()).command(command)
        except subprocess.SubprocessError as e:
            dlg = wx.MessageDialog(
                None, e.stderr, "Error", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        except Exception as e:
            dlg = wx.MessageDialog(
                None, str(e), "Error", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    def get_selected_device(self):
        return self.list.GetString(self.list.GetSelection())

    def on_select_device(self, event):
        if not event.IsSelection():
            return

        self.device_buttons.Enable()
        device = self.get_selected_device()
        self.disconnect_button.Enable(bool(
            ListDevicesFrame.NET_DEVICE.fullmatch(device)))

    def on_start_device(self, event):
        if not event.IsSelection():
            return

        self.on_select(self.get_selected_device())

    def on_connect(self, _):
        device = wx.GetTextFromUser(
            'Enter device: IP[:PORT]', 'Connect device')
        if device:
            port = ADB.PORT
            full_device = ListDevicesFrame.NET_DEVICE.findall(device)
            if full_device:
                device, port = full_device[0]

            ADB.connect(device, port)
            self.update_devices()

    def on_disconnect(self, _):
        device = self.get_selected_device()
        device = ListDevicesFrame.NET_DEVICE.findall(device)
        ADB.disconnect(*device[0])
        self.update_devices()

    def on_close(self, event):
        self.timer.Stop()
        event.Skip()
