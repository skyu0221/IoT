from lpanel import LeftPanel
from rpanel import RightPanel
import config

import wx
from pubsub import pub

from numpy import arange, sin, pi
import requests
# import matplotlib
# matplotlib.use('WXAgg')

from apscheduler.schedulers.background import BackgroundScheduler
import atexit

import random
import json



class MainFrame(wx.Frame):

    def __init__(self, parent, title, size, style):
        super(MainFrame, self).__init__(parent, title=title,
            size=size, style=style)

        self.InitUI(size=size)
        self.Centre()

    def InitUI(self, size):
        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        
        # floor plan panel
        l_panel = LeftPanel(splitter, info={"size": (int(size[0]*2/3), size[1])})
        
        # question panel
        r_panel = RightPanel(splitter, info={"size": (int(size[0]*1/3), size[1])})

        splitter.SplitVertically(l_panel, r_panel, int(size[0]*2/3))
        # splitter.SetMinimumPaneSize(20)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)


def message_update():
    received_meesage = {
        "Room_1_1_140": 0,
        "Room_1_1_141": 0,
        "Room_1_1_142": 0,
        "Room_1_1_143": 0,
        "Room_1_1_144": 0,
        "Room_1_1_150": 0,
        "Room_1_1_184": 0,
    }

    url = config.SERVER + "/room/"
    data = {}
    r = requests.post(url, data=data, )

    if r.status_code == 200:
        resp = json.loads(r.json())
        # print(resp["room_info"])
        for room_info in resp["room_info"]:
            # print(room_info)
            # print(room_info[0])
            # print(room_info[1])
            received_meesage[room_info[0]] = room_info[1]


        encode_message = json.dumps(received_meesage)

        pub.sendMessage('room_count.update', message=encode_message)  



def main():
    app = wx.App()

    frame = MainFrame(parent=None, 
                        title='Simple application', 
                        size=(1200, 750),
                        style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)
    frame.Show()

    # create a background scheduler to get data from server
    # https://www.coder.work/article/79477
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=message_update, trigger="interval", seconds=5)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())


    app.MainLoop()

if __name__ == "__main__":
    main()