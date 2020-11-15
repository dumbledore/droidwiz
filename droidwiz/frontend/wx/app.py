import wx

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
        device = Device(name)
        frame = DeviceFrame(device)
        frame.SetPosition((frame.FromDIP(50),) * 2)
        frame.Bind(wx.EVT_CLOSE, on_close_device)
        frame.Show()

    devices_frame = ListDevicesFrame(show_device)

    devices_frame.Show()

def main():
    app = wx.App()
    choose_device()
    app.MainLoop()

if __name__ == '__main__':
    main()
