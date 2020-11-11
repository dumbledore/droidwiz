import wx

from droidwiz.android.adb import ADB
from droidwiz.android.device import Device
from .device_frame import DeviceFrame


def main():
    app = wx.App()

    adb = ADB.create_default()
    device = Device(adb)
    frame = DeviceFrame(device)
    frame.SetPosition((frame.FromDIP(50),) * 2)
    frame.Show()

    app.MainLoop()

if __name__ == '__main__':
    main()
