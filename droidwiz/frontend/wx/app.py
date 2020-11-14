import wx

from droidwiz.android.device import Device
from .device_frame import DeviceFrame


def main():
    app = wx.App()

    device = Device.create_default()
    frame = DeviceFrame(device)
    frame.SetPosition((frame.FromDIP(50),) * 2)
    frame.Show()

    app.MainLoop()

if __name__ == '__main__':
    main()
