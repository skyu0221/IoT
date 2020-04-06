import config

import wx
from pubsub import pub

import json
import requests

class LeftPanel(wx.Panel):
    
    def __init__(self, parent, info={}):
        wx.Panel.__init__(self, parent=parent)
        self.info = info

        self.info["room_number_widget_id"] = wx.NewIdRef(count=1)
        self.info["people_list_widget_id"] = wx.NewIdRef(count=1)
        self.info["room_name_widget_id"] = wx.NewIdRef(count=1)
        self.info["list_ctrl_id"] = wx.NewIdRef(count=1)
        ri_panel = RoomInfoPanel(self, info)
        fp_panel = FloorPlanPanel(self, info)

        # for room in fp_panel.buttons:
        #     fp_panel.Bind(wx.EVT_BUTTON, ri_panel._update_room_info, fp_panel[room])

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(fp_panel, proportion=12, flag=wx.EXPAND)
        vbox.Add(ri_panel, proportion=1, flag=wx.EXPAND)
        self.SetSizer(vbox)


class FloorPlanPanel(wx.Panel):
    
    def __init__(self, parent, info={}):
        wx.Panel.__init__(self, parent=parent)
        self.parent = parent
        self.info = info
        self._setup_private_var()
        self._init_UI()

    def _setup_private_var(self):
        self.room_info = {
            "Room_1_1_140": (615, 345),
            "Room_1_1_141": (690, 370),
            "Room_1_1_142": (615, 400),
            "Room_1_1_143": (680, 435),
            "Room_1_1_144": (615, 450),
            "Room_1_1_150": (625, 520),
            "Room_1_1_184": (510, 220),
        }
        
    def _init_UI(self):
        # self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        # imageFile = "../floorplan.jpg"
        # vbox = wx.BoxSizer(wx.VERTICAL)

        # add dots button
        self._add_dots_button()

        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

        pub.subscribe(self._update_room_count, 'room_count.update')

    def _update_room_count(self, message):
        # print("received " + message)
        room_count = json.loads(message)

        for btn in self.button_list:
            count = room_count[btn.room_name]
            btn.SetLabel(str(count))


    def _add_dots_button(self):
        self.button_list = []
        
        for room in self.room_info:
            btn = wx.Button(self, id=-1, label="", pos=self.room_info[room], size=(35, 20))
            btn.room_name = room
            btn.SetBackgroundColour("#fe1919")
            btn.SetForegroundColour("#fe1919")

            self.button_list.append(btn)
            self.Bind(wx.EVT_BUTTON, self.OnClick, btn)


    def OnClick(self, evt):
        room_name = evt.GetEventObject().room_name
        
        # requester send request
        url = config.SERVER + "/room_info/"
        my_list = []
        data = {"room": room_name}
        r = requests.post(url, data=data)

        if r.status_code == 200:
            resp = r.json()
            for person_info in resp["occupancy_info"]:
                my_list.append(person_info[1])

        
        room_name_widget = self.parent.FindWindowById(self.info["room_name_widget_id"])
        room_name_widget.SetLabel(room_name)

        room_number_widget = self.parent.FindWindowById(self.info["room_number_widget_id"])
        room_number_widget.SetLabel(str(len(my_list)))

        list_ctrl = self.parent.FindWindowById(self.info["list_ctrl_id"])
        list_ctrl.Clear()

        for item in my_list:
            list_ctrl.Append(item)

        



    def _scale_image(self, image, width, height):
        # https://stackoverflow.com/questions/2504143/how-to-resize-and-draw-an-image-using-wxpython
        # image = bitmap.ConvertToImage()
        # image.SaveFile('check1.jpg', wx.BITMAP_TYPE_JPEG)
        image = image.Rescale(width, height, wx.IMAGE_QUALITY_HIGH)
        # image.SaveFile('check2.jpg', wx.BITMAP_TYPE_JPEG)
        result = image.ConvertToBitmap()
        return result

    def OnEraseBackground(self, evt):
        """
        Add a picture to the background
        """
        # yanked from ColourDB.py
        
        dc = evt.GetDC()
                
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()

        panel_size = self.info["size"]
        # print(panel_size)
        # bm = wx.Image("../floorplan.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        img = wx.Image("floorplan.jpg", wx.BITMAP_TYPE_JPEG)
        bm = self._scale_image(img, int(panel_size[0]), int(panel_size[1])-100)
        dc.DrawBitmap(bm, 0, 0)



class RoomInfoPanel(wx.Panel):

    def __init__(self, parent, info={}):
        wx.Panel.__init__(self, parent=parent)

        self.info = info
        self._init_UI()

    def _init_UI(self):
        # self.SetBackgroundColour("#000000")
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        room_name = wx.StaticText(self, id=self.info["room_name_widget_id"], label='Room name')
        vbox.Add(room_name, flag=wx.LEFT, border=2)
        
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        room_number = wx.StaticText(self, id=self.info["room_number_widget_id"], label='Room number')
        total_number = wx.StaticText(self, id=-1, label='Total Number: ')
        hbox1.Add(total_number, proportion=1, flag=wx.ALL, border=2)
        hbox1.Add(room_number, proportion=1, flag=wx.ALL, border=2)
        vbox.Add(hbox1)

        hbox.Add(vbox, proportion=3, flag=wx.EXPAND, border=2)
        # list_ctrl = wx.ListCtrl(self, 
        #                         id=self.info["list_ctrl_id"], 
        #                         # size=(680, 340), 
        #                         style=wx.LC_REPORT| wx.BORDER_SUNKEN)
        # list_ctrl.AppendColumn("Name", width=100)
        # list_ctrl.AppendColumn("Last visited time", width=150)

        # hbox.Add(list_ctrl, proportion=7, flag=wx.ALL, border=2)
        lb = wx.ListBox(self, id=self.info["list_ctrl_id"])
        hbox.Add(lb, proportion=7, flag=wx.ALL, border=2)

        self.SetSizer(hbox)