# Copyright (C) 2020-2024, Svetlin Ankov

import subprocess
import sys
import wx

from droidwiz.android.adb import ADB
from droidwiz.android.device import Device
from .device_frame import DeviceFrame
from .list_devices_frame import ListDevicesFrame


class App(wx.App):
    def OnInit(self):
        self.device = False
        self.choose_device()
        wx.Log.SetActiveTarget(wx.LogStderr())
        return True

    def OnExit(self):
        if self.device:
            self.device.Close()

        return 0

    def Quit(self):
        # This will close left-over windows (if any)
        self.ExitMainLoop()

    def on_close_device(self, event):
        event.Skip()
        self.choose_device()

    def choose_device(self):
        devices_frame = None

        def show_device(name):
            devices_frame.Close()
            devices_frame.Destroy()
            try:
                device = Device(name)
                self.device = DeviceFrame(device, png=True, resize_quality=wx.IMAGE_QUALITY_BILINEAR)
                self.device.Center()

                # Make sure the window controls are always visible
                position = self.device.GetPosition()
                position = [x if x > 30 else 30 for x in position]
                self.device.SetPosition(position)

                self.device.Bind(wx.EVT_CLOSE, self.on_close_device)
                self.device.Show()
            except subprocess.SubprocessError as e:
                dlg = wx.MessageDialog(
                    None, e.stderr, "Error", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.choose_device()
            except Exception as e:
                dlg = wx.MessageDialog(
                    None, str(e), "Error", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.choose_device()

        devices_frame = ListDevicesFrame(self, show_device)
        devices_frame.Center()
        devices_frame.Show()


def main():
    if not ADB.available():
        print('ADB not available', file=sys.stderr)
        sys.exit(1)

    App().MainLoop()


if __name__ == '__main__':
    main()
