# Copyright (C) 2020-2024, Svetlin Ankov

import subprocess
import sys
import re
import wx

from droidwiz.android.adb import ADB


class ListDevicesFrame(wx.Frame):
    def __init__(self, on_select, *args, **kwargs):
        super().__init__(None, title="Devices", *args, **kwargs)

        self.on_select = on_select

        # Menu bar
        self.SetMenuBar(self.create_menu())

        # Device list
        self.list = wx.ListBox(self)
        self.Bind(wx.EVT_LISTBOX, self.on_select_device)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.on_start_device)

        # Device update timer
        self.timer = wx.Timer(self, 0)
        self.Bind(wx.EVT_TIMER, self.update_devices)
        self.timer.Start(1000)

        # Make sure we handle close
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # Don't wait for initial timer event
        self.update_devices()

    def create_menu(self):
        menu_bar = wx.MenuBar()

        # File
        file_menu = wx.Menu()

        file_options = file_menu.Append(wx.ID_ANY, "Options", "Application configuration")
        menu_bar.Append(file_menu, "&File")

        # Device
        device_menu = wx.Menu()

        device_start = device_menu.Append(wx.ID_ANY, "&Start", "Start selected device")
        device_menu.AppendSeparator()

        device_root = device_menu.Append(wx.ID_ANY, "&Root", "Restart ADBD with root")
        device_unroot = device_menu.Append(wx.ID_ANY, "&Unroot", "Restart ADBD without root")
        device_remount = device_menu.Append(wx.ID_ANY, "Re&mount", "Remount partitions read-write")
        device_reboot = device_menu.Append(wx.ID_ANY, "Reboo&t", "Reboots the device")
        device_bootloader = device_menu.Append(wx.ID_ANY, "&Bootloader", "Reboots the device into the bootloader")
        device_menu.AppendSeparator()

        device_disconnect = device_menu.Append(wx.ID_ANY, "&Disconnect", "Disconnect from given TCP/IP device")

        menu_bar.Append(device_menu, "&Device")

        # Network
        network_menu = wx.Menu()

        network_connect = network_menu.Append(wx.ID_ANY, "&Connect", "Connect to a device via TCP/IP communication")
        network_disconnect = network_menu.Append(wx.ID_ANY, "&Disconnect", "Disconnect all TCP/IP devices")

        menu_bar.Append(network_menu, "&Network")

        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, "", "About this application")
        menu_bar.Append(help_menu, "&Help")

        # Bind the events
        self.Bind(wx.EVT_MENU, self.on_start_device, device_start)
        self.Bind(wx.EVT_MENU, lambda _: self.run_adb_command(["root"]), device_root)
        self.Bind(wx.EVT_MENU, lambda _: self.run_adb_command(["unroot"]), device_unroot)
        self.Bind(wx.EVT_MENU, lambda _: self.run_adb_command(["remount"]), device_remount)
        self.Bind(wx.EVT_MENU, lambda _: self.run_adb_command(["reboot"]), device_reboot)
        self.Bind(wx.EVT_MENU, lambda _: self.run_adb_command(["reboot", "bootloader"]), device_bootloader)
        self.Bind(wx.EVT_MENU, self.on_disconnect_device, device_disconnect)
        self.Bind(wx.EVT_MENU, self.on_connect, network_connect)
        self.Bind(wx.EVT_MENU, self.on_disconnect, network_disconnect)

        # Add Exit to File menu on non-MacOS
        if sys.platform != "darwin":
            file_menu.Append(wx.ID_EXIT)
            self.Bind(wx.EVT_MENU, self._on_quit, id=wx.ID_EXIT)

        for item in device_menu.MenuItems:
            item.Enable(False)

        # Save the following for later use
        self.device_disconnect = device_disconnect
        self.device_menu = device_menu

        return menu_bar

    def update_devices(self, event=None):
        devices = sorted(ADB.list_devices())

        if self.list.Items != devices:
            for item in self.device_menu.MenuItems:
                item.Enable(False)

            self.list.Items = devices

    NET_DEVICE = re.compile(r'(.*):(\d+)')

    def run_adb_command(self, command):
        try:
            ADB(self.get_selected_device()).command(command)
        except subprocess.SubprocessError as e:
            dlg = wx.MessageDialog(None, e.stderr, "Error", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        except Exception as e:
            dlg = wx.MessageDialog(None, str(e), "Error", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    def get_selected_device(self):
        return self.list.GetString(self.list.GetSelection())

    def on_select_device(self, event):
        # Enable all device items
        for item in self.device_menu.MenuItems:
            item.Enable(True)

        # Enable device disconnect only if selected device is a net device
        device = self.get_selected_device()
        self.device_disconnect.Enable(bool(ListDevicesFrame.NET_DEVICE.fullmatch(device)))

    def on_start_device(self, event):
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
        ADB.disconnect()
        self.update_devices()

    def on_disconnect_device(self, _):
        device = self.get_selected_device()
        device = ListDevicesFrame.NET_DEVICE.findall(device)
        ADB.disconnect(*device[0])
        self.update_devices()

    def on_close(self, event):
        self.timer.Stop()
        event.Skip()
