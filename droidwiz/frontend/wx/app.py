# Copyright (C) 2020-2024, Svetlin Ankov

import subprocess
import sys
import wx

from droidwiz.android.adb import ADB
from droidwiz.android.device import Device
from .device_frame import DeviceFrame
from .list_devices_frame import ListDevicesFrame


def on_close_device(event):
    event.Skip()
    choose_device()


def choose_device():
    devices_frame = None

    def show_device(name):
        devices_frame.Close()
        devices_frame.Destroy()
        try:
            device = Device(name)
            frame = DeviceFrame(device, png=True)
            frame.Center()
            frame.Bind(wx.EVT_CLOSE, on_close_device)
            frame.Show()
        except subprocess.SubprocessError as e:
            dlg = wx.MessageDialog(
                None, e.stderr, "Error", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            choose_device()
        except Exception as e:
            dlg = wx.MessageDialog(
                None, str(e), "Error", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            choose_device()

    devices_frame = ListDevicesFrame(show_device)
    devices_frame.Center()
    devices_frame.Show()


def main():
    if not ADB.available():
        print('ADB not available', file=sys.stderr)
        sys.exit(1)

    app = wx.App()
    choose_device()
    app.MainLoop()


if __name__ == '__main__':
    main()
