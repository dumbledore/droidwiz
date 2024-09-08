# Copyright (C) 2024, Svetlin Ankov

import wx


class ButtonWindow(wx.Frame):
    def __init__(self, parent, buttons=[]):
        super().__init__(parent, style=wx.FRAME_NO_TASKBAR | wx.FRAME_FLOAT_ON_PARENT)

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        for bitmap, callback in buttons:
            button = wx.BitmapButton(panel, bitmap=bitmap, style=wx.BU_EXACTFIT)
            if callback:
                button.Bind(wx.EVT_BUTTON, callback)
            sizer.Add(button, 0, flag=wx.EXPAND, border=5)

        panel.SetSizer(sizer)
        panel.Fit()
        self.Fit()
