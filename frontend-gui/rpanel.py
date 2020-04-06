import wx
import wx.adv
import random
import util
import config

import time
import datetime
import threading

import requests
import json


from functools import partial

class ReqeusterThread(threading.Thread):
    # https://www.oreilly.com/library/view/python-cookbook/0596001673/ch06s03.html

    def __init__(self, name, parent_thread, parent_panel):
        threading.Thread.__init__(self, name=name)
        
        self._stopevent = threading.Event()
        self.parent_panel = parent_panel
        self.parent_thread = parent_thread


    def run(self):
        while (not self._stopevent.is_set()) and self.parent_thread.is_alive():
            print("hello")
            # print(self.parent_panel.info_widget_dict)
            # print(self.parent_panel.info)

            # chnage to real time
            end = datetime.datetime.now()
            start = end - datetime.timedelta(minutes=1)
            self.parent_panel.info["start"] = util.convert_to_GMT_zone(start)
            self.parent_panel.info["end"] = util.convert_to_GMT_zone(end)

            
            self.parent_panel._send_request(self.parent_panel.info)
            self._stopevent.wait(5.0)


    def join(self, timeout=None):
        self._stopevent.set()
        print("thread stop")
        threading.Thread.join(self, timeout)


class RightPanel(wx.Panel):
    
    def __init__(self, parent, info={}):
        wx.Panel.__init__(self, parent=parent)
        self.drop_down_menu_ID = None
        self.result_visual_ID = None

        self.info = info
        self._init_UI()

    def _init_UI(self):
        self.SetBackgroundColour("#BAB86C")
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(20)

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        # add question label
        st1 = wx.StaticText(self, label='Question')
        st1.SetFont(font)
        hbox1.Add(st1, proportion=2, flag=wx.RIGHT, border=10)

        # add drop down menu
        question_list = [   
                            "1. How many people are in the building?", 
                            "2. How many people are in a specific room?", 
                            "3. Where is someone?",
                            # "4. Which room has someone visited?",
                            "4. What is the utilization of a specific room?"
                        ]
        drop_down_menu = wx.ComboBox(self, choices=question_list)
        hbox1.Add(drop_down_menu, proportion=8, flag=wx.TOP, border=5)

        vbox1 = wx.BoxSizer(wx.VERTICAL)
        
        # add result label
        # st2 = wx.StaticText(self, label='Result')
        # st2.SetFont(font)
        # vbox1.Add(st2, proportion=1, flag=wx.ALIGN_CENTER, border=1)

        # add canvas panel
        # canvas_panel = CanvasPanel(self)
        # vbox1.Add(canvas_panel, proportion=9, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
        result_panel = ResultPanel(self)
        # result_panel.SetBackgroundColour("#000000")
        vbox1.Add(result_panel, proportion=9, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)


        vbox.Add(hbox1, proportion=1, flag=wx.EXPAND|wx.ALL, border=10)
        vbox.Add(vbox1, proportion=9, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        # listen combo
        drop_down_menu.Bind(wx.EVT_COMBOBOX, partial(self.on_selection, 
                                                    combo_box=drop_down_menu, 
                                                    panel=result_panel))


    def on_selection(self, event, combo_box, panel):
        # print(self.drop_down_menu.GetValue())
        print(combo_box.GetValue())
        panel.init_question_UI(combo_box.GetValue()[0])

        # st2 = wx.StaticText(self, label=combo_box.GetValue())
        # st2.SetFont(font)
        # sizer1.Add(st2, proportion=1, flag=wx.ALIGN_CENTER, border=1)


class ResultPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        # self._init_UI()

        self._q_dict = {"1": self._q1_panel,
                        "2": self._q2_panel,
                        "3": self._q3_panel,
                        # "4": self._q4_panel,
                        "4": self._q5_panel,}
        
        self.info_widget_dict = {"feeder": {}, "consumer": {}}
        self.worker = None
        self.server = config.SERVER
        
        self._set_font()


    def _set_font(self):
        self.font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        self.font.SetPointSize(12)
        self.font.MakeBold()

    def init_question_UI(self, q_idx):
        # clean the panel
        for child in self.GetChildren():
            child.Destroy()

        # stop the worker
        if self.worker:
            # print("the worker has been stop")
            self.worker.join()
            self.worker = None

        self.info_widget_dict["feeder"].clear()
        self.info_widget_dict["consumer"].clear()

        decorate_panel = self._q_dict[q_idx]
        decorate_panel()

    def add_date_time_picker_layout(self):
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        # Start
        start_label = wx.StaticText(self, label="START TIME")
        start_label.SetFont(self.font)
        dpc1 = wx.adv.DatePickerCtrl(self, -1, wx.DefaultDateTime)
        tpc1 = wx.adv.TimePickerCtrl(self, -1, wx.DefaultDateTime)
        
        hbox1.Add(start_label, proportion=2, flag=wx.RIGHT|wx.TOP, border=4)
        hbox1.Add(dpc1, proportion=3, flag=wx.RIGHT, border=5)
        hbox1.Add(tpc1, proportion=3, flag=wx.RIGHT, border=5)
        vbox.Add(hbox1, proportion=0, flag=wx.ALL, border=5)

        # End
        end_label = wx.StaticText(self, label="END   TIME")
        end_label.SetFont(self.font)
        dpc2 = wx.adv.DatePickerCtrl(self, -1, wx.DefaultDateTime)
        tpc2 = wx.adv.TimePickerCtrl(self, -1, wx.DefaultDateTime)
        hbox2.Add(end_label, proportion=2, flag=wx.RIGHT|wx.TOP, border=4)
        hbox2.Add(dpc2, proportion=3, flag=wx.RIGHT, border=5)
        hbox2.Add(tpc2, proportion=3, flag=wx.RIGHT, border=5)
        vbox.Add(hbox2, proportion=0, flag=wx.ALL, border=5)

        # Real time box
        real_label = wx.StaticText(self, label="REAL TIME")
        real_label.SetFont(self.font)
        cb = wx.CheckBox(self)
        hbox3.Add(real_label, proportion=2, flag=wx.RIGHT|wx.TOP, border=4)
        hbox3.Add(cb, proportion=3, flag=wx.RIGHT|wx.TOP, border=5)
        vbox.Add(hbox3, proportion=0, flag=wx.ALL, border=5)


        self.info_widget_dict["feeder"]["start_date"] = dpc1
        self.info_widget_dict["feeder"]["start_time"] = tpc1
        self.info_widget_dict["feeder"]["end_date"] = dpc2
        self.info_widget_dict["feeder"]["end_time"] = tpc2
        self.info_widget_dict["feeder"]["real_time"] = cb
        
        # self.SetBackgroundColour("#000000")
        # r = lambda: random.randint(0,255)
        # color = '#%02X%02X%02X' % (r(),r(),r())
        return vbox

    def _add_confirm_button(self, sizer, question_index):
        """
            question_index => {1, 2, 3, 4}
        """
        comfirm_btn = wx.Button(self, id=-1, label="Confirm")
        sizer.Add(comfirm_btn, proportion=0, flag=wx.TOP|wx.LEFT, border=5)

        # self.Bind(wx.EVT_BUTTON, self.OnClick, comfirm_btn)

        self.Bind(wx.EVT_BUTTON, lambda event: self.OnClick(event, question_index), comfirm_btn)


    def _add_result_label(self, sizer):
        result_label = wx.StaticText(self, label="RESULT")
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(20)
        font.MakeBold()
        result_label.SetFont(font)
        sizer.Add(result_label, proportion=0, flag=wx.ALIGN_CENTER_HORIZONTAL, border=20)


    def OnClick(self, event, question_index):
        info = {}

        # handle date and time
        if question_index in [1, 2, 3, 4]:
            start_date = self.info_widget_dict["feeder"]["start_date"].GetValue()
            start_time = self.info_widget_dict["feeder"]["start_time"].GetValue()

            end_date = self.info_widget_dict["feeder"]["end_date"].GetValue()
            end_time = self.info_widget_dict["feeder"]["end_time"].GetValue()

            info["start"] = util.combine_datetime(start_date, start_time)
            info["end"] = util.combine_datetime(end_date, end_time)
            
            # print("start time = {}".format(info["start"]))
            # print("end time = {}".format(info["end"]))

            if_real_time = self.info_widget_dict["feeder"]["real_time"].GetValue()

            if question_index == 1:
                # requester send request to server
                pass


            elif question_index == 2:
                # requester send request to server
                room = self.info_widget_dict["feeder"]["room_select"].GetValue()
                print(room)

                info["room"] = room

            elif question_index == 3:
                # requester send request to server
                name = self.info_widget_dict["feeder"]["name_select"].GetValue()
                print(name)

                info["name"] = name

            else: # question_index = 4
                name = self.info_widget_dict["feeder"]["name_select"].GetValue()
                print(name)

                info["name"] = name

        
        else: # question_index == 5
            if_real_time = False

            date = self.info_widget_dict["feeder"]["date_picker"].GetValue()
            time = self.info_widget_dict["feeder"]["time_picker"].GetValue()
            room = self.info_widget_dict["feeder"]["room_select"].GetValue()

            info["date"] = util.combine_datetime(date, time)
            info["room"] = room

        # requester send request to server
        info["question_index"] = question_index
        self.info = info

        if if_real_time:
            if not self.worker:
                self.worker = ReqeusterThread(name="question_{}_requester".format(question_index), parent_thread=threading.currentThread(), parent_panel=self)
                self.worker.start()
                print("start worker")
        else:
            # first check if the worker is working
            if self.worker:
                self.worker.join()
                self.worker = None

            self._send_request(info)

    def _request_handle(self, url,  body={}, params={}, METHOD="post"):
        # https://stackoverflow.com/questions/15900338/python-request-post-with-param-data
        print("url", url)
        print("body", body)
        print("params", params)
        resp = {}
        if METHOD == "post":
            r = requests.post(url, data=body)
        else:
            r = requests.get(url, params=params)

        print(r.status_code)
        if r.status_code == 200:
            resp = r.json()
            print(resp)
            print(type(resp))
        
        return resp


    def _send_request(self, info):
        question_index = int(info["question_index"])

        if question_index == 1:
            ## get ##
            url = self.server + "/people_building/"
            body = {"start": info["start"], "end": info["end"]}
            # body = {'start': '2020-04-05 21:00:00', 'end': '2020-04-05 21:10:00'}
            response = self._request_handle(url=url, body=body, METHOD="post")
            
            try:
                occu = str(response['count'])
            except:
                occu = str(0)
            
            ## received##
            self.info_widget_dict["consumer"]["occu_label"].SetLabel(occu)

        elif question_index == 2:
            ## get ##
            url = self.server + "/people_room/"
            body = {"room": info["room"],
                    "start": info["start"],
                    "end": info["end"],
                    # 'start': '2020-04-05 21:00:00', 'end': '2020-04-05 21:10:00'
                    }

            response = self._request_handle(url=url, body=body, METHOD="post")

            try:
                occu = str(response['count'])
                occupancy_info = response['occupancy_info']
            except:
                occu = str(0)
                occupancy_info = []


            ## received ##
            self.info_widget_dict["consumer"]["occu_label"].SetLabel(occu)

            nlb = self.info_widget_dict["consumer"]["name_list"]
            nlb.Clear()

            for name in occupancy_info:
                nlb.Append(name)


        elif question_index == 3:
            ## get ##
            url = self.server + "/person_room/"
            body = {"name": info["name"],
                    "start": info["start"],
                    "end": info["end"],
                    # 'start': '2020-04-05 21:00:00', 'end': '2020-04-05 21:10:00'
                    }

            response = self._request_handle(url=url, body=body, METHOD="post")

            try:
                room_list = response['room']
                count = str(len(room_list))
            except:
                count = str(0)
                room_list = []

            ## received ##
            self.info_widget_dict["consumer"]["count_label"].SetLabel(count)

            rlb = self.info_widget_dict["consumer"]["room_list"]
            rlb.Clear()

            for name in room_list:
                rlb.Append(name)


        elif question_index == 4:
            ## get ##
            url = self.server + "question/4"
            body = {"name": info["name"],
                    # "start_time": info["start"],
                    # "end_time": info["end"],
                    "time": info["start"],
                    }

            response = self._request_handle(url=url, body=body, METHOD="post")

            count = str(random.randint(0, 20))
            room_list = ["Room_1_1_140", "Room_1_1_141"]

            ## received ##
            self.info_widget_dict["consumer"]["count_label"].SetLabel(count)

            rlb = self.info_widget_dict["consumer"]["room_list"]
            rlb.Clear()

            for name in room_list:
                rlb.Append(name)


        elif question_index == 5:
            ## get ##
            url = self.server + "/utilization/"
            body = {"room": info["room"],
                    "date": info["date"],
                    # 'date': '2020-04-05 20:00:00'
                    }

            response = self._request_handle(url=url, body=body, METHOD="post")
            # self.request_handle(url, body, METHOD="post")

            try:
                response = json.loads(response)
                utilization = "{:.2f}".format(response["utilization"]*100) + "%"
            except:
                utilization = "0%"
            
            ## received##
            self.info_widget_dict["consumer"]["utilization_label"].SetLabel(utilization)

        

    def _q1_panel(self):
        print("q1")

        main_vbox = self.add_date_time_picker_layout()

        # confirm button
        self._add_confirm_button(main_vbox, 1)

        # add result label
        self._add_result_label(main_vbox)

        # add result widget
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, label="Occupancy")
        label.SetFont(self.font)
        hbox.Add(label, proportion=2, flag=wx.TOP|wx.RIGHT, border=5)
        occu_label = wx.StaticText(self, label="__")
        occu_label.SetFont(self.font)
        hbox.Add(occu_label, proportion=2, flag=wx.TOP|wx.RIGHT, border=5)
        main_vbox.Add(hbox, proportion=0, flag=wx.ALL, border=5)

        self.info_widget_dict["consumer"]["occu_label"] = occu_label


        self.SetSizer(main_vbox)
        # https://stackoverflow.com/questions/42365239/wxpython-after-changing-panel-and-redo-layout-panel-is-very-small
        self.Fit()
        self.GetParent().SendSizeEvent()



    def _q2_panel(self):
        print("q2")

        main_vbox = self.add_date_time_picker_layout()

        # Room Info
        room_hbox = wx.BoxSizer(wx.HORIZONTAL)
        room_label = wx.StaticText(self, label="Room")
        room_label.SetFont(self.font)
        room_hbox.Add(room_label, proportion=2, flag=wx.TOP|wx.RIGHT, border=5)
        
        room_list = [
                "",
                "Room_1_1_140",
                "Room_1_1_141",
                "Room_1_1_142",
                "Room_1_1_143",
                "Room_1_1_144",
                "Room_1_1_150",
                "Room_1_1_184"]
        
        room_combobox = wx.ComboBox(self, choices=room_list)
        room_hbox.Add(room_combobox, proportion=8, flag=wx.TOP, border=5)
        # room_info = wx.TextCtrl(self)
        # room_hbox.Add(room_combobox, proportion=8, flag=wx.TOP, border=5)
        
        main_vbox.Add(room_hbox, proportion=0, flag=wx.ALL, border=5)

        # confirm button
        self._add_confirm_button(main_vbox, 2)

        # add result label
        self._add_result_label(main_vbox)

        # add widget infomation to dict
        self.info_widget_dict["feeder"]["room_select"] = room_combobox

        # add result widget
        # add count
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, label="Occupancy")
        label.SetFont(self.font)
        hbox.Add(label, proportion=2, flag=wx.TOP|wx.RIGHT, border=5)
        occu_label = wx.StaticText(self, label="__")
        occu_label.SetFont(self.font)
        hbox.Add(occu_label, proportion=2, flag=wx.TOP|wx.RIGHT, border=5)
        main_vbox.Add(hbox, proportion=0, flag=wx.ALL, border=5)

        # add name list
        namelb = wx.ListBox(self)
        main_vbox.Add(namelb, proportion=0, flag=wx.ALL, border=5)

        self.info_widget_dict["consumer"]["occu_label"] = occu_label
        self.info_widget_dict["consumer"]["name_list"] = namelb


        self.SetSizer(main_vbox)
        # https://stackoverflow.com/questions/42365239/wxpython-after-changing-panel-and-redo-layout-panel-is-very-small
        self.Fit()
        self.GetParent().SendSizeEvent()

    def _q3_panel(self):
        print("q3")

        vbox = self.add_date_time_picker_layout()

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        name_label = wx.StaticText(self, label="Name")
        name_label.SetFont(self.font)
        hbox1.Add(name_label, proportion=2, flag=wx.TOP|wx.RIGHT, border=5)
        
        name_text_ctrl = wx.TextCtrl(self)
        name_text_ctrl.AppendText('Please enter unique name')
        hbox1.Add(name_text_ctrl, proportion=8, flag=wx.TOP, border=5)

        vbox.Add(hbox1, proportion=0, flag=wx.ALL, border=5)

        # confirm button
        self._add_confirm_button(vbox, 3)

        # add result label
        self._add_result_label(vbox)

        # add widget infomation to dict
        self.info_widget_dict["feeder"]["name_select"] = name_text_ctrl

        # add result widget
        # add count
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, label="Room Count")
        label.SetFont(self.font)
        hbox.Add(label, proportion=2, flag=wx.TOP|wx.RIGHT, border=5)
        occu_label = wx.StaticText(self, label="__")
        occu_label.SetFont(self.font)
        hbox.Add(occu_label, proportion=2, flag=wx.TOP|wx.RIGHT, border=5)
        vbox.Add(hbox, proportion=0, flag=wx.ALL, border=5)

        # add name list
        roomlb = wx.ListBox(self)
        vbox.Add(roomlb, proportion=0, flag=wx.ALL, border=5)

        self.info_widget_dict["consumer"]["count_label"] = occu_label
        self.info_widget_dict["consumer"]["room_list"] = roomlb

        self.SetSizer(vbox)
        # https://stackoverflow.com/questions/42365239/wxpython-after-changing-panel-and-redo-layout-panel-is-very-small
        self.Fit()
        self.GetParent().SendSizeEvent()



    def _q4_panel(self):
        print("q4")
        
        main_vbox = self.add_date_time_picker_layout()

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        name_label = wx.StaticText(self, label="Name")
        name_label.SetFont(self.font)
        hbox1.Add(name_label, proportion=2, flag=wx.TOP|wx.RIGHT, border=5)
        
        name_text_ctrl = wx.TextCtrl(self)
        name_text_ctrl.AppendText('Please enter unique name')
        hbox1.Add(name_text_ctrl, proportion=8, flag=wx.TOP, border=5)

        main_vbox.Add(hbox1, proportion=0, flag=wx.ALL, border=5)

        # confirm button
        self._add_confirm_button(main_vbox, 4)

        # add result label
        self._add_result_label(main_vbox)

        # add widget infomation to dict
        self.info_widget_dict["feeder"]["name_select"] = name_text_ctrl

        # add result widget
        # add count
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, label="Room Count")
        label.SetFont(self.font)
        hbox.Add(label, proportion=2, flag=wx.TOP|wx.RIGHT, border=5)
        occu_label = wx.StaticText(self, label="__")
        occu_label.SetFont(self.font)
        hbox.Add(occu_label, proportion=2, flag=wx.TOP|wx.RIGHT, border=5)
        main_vbox.Add(hbox, proportion=0, flag=wx.ALL, border=5)

        # add name list
        roomlb = wx.ListBox(self)
        main_vbox.Add(roomlb, proportion=0, flag=wx.ALL, border=5)

        self.info_widget_dict["consumer"]["count_label"] = occu_label
        self.info_widget_dict["consumer"]["room_list"] = roomlb

        self.SetSizer(main_vbox)
        # https://stackoverflow.com/questions/42365239/wxpython-after-changing-panel-and-redo-layout-panel-is-very-small
        self.Fit()
        self.GetParent().SendSizeEvent()


    def _q5_panel(self):
        print("q5")

        vbox = wx.BoxSizer(wx.VERTICAL)

        # datetime
        date_hbox = wx.BoxSizer(wx.HORIZONTAL)
        date_label = wx.StaticText(self, label="Datetime")
        date_label.SetFont(self.font)
        dpc = wx.adv.DatePickerCtrl(self, -1, wx.DefaultDateTime)
        tpc = wx.adv.TimePickerCtrl(self, -1, wx.DefaultDateTime)
        date_hbox.Add(date_label, proportion=2, flag=wx.RIGHT|wx.TOP, border=4)
        date_hbox.Add(dpc, proportion=3, flag=wx.RIGHT, border=5)
        date_hbox.Add(tpc, proportion=3, flag=wx.RIGHT, border=5)
        vbox.Add(date_hbox, proportion=0, flag=wx.ALL, border=5)

        # Room Info
        room_hbox = wx.BoxSizer(wx.HORIZONTAL)
        room_label = wx.StaticText(self, label="Room")
        room_label.SetFont(self.font)
        room_hbox.Add(room_label, proportion=2, flag=wx.TOP|wx.RIGHT, border=5)
        
        room_list = [
                "",
                "Room_1_1_140",
                "Room_1_1_141",
                "Room_1_1_142",
                "Room_1_1_143",
                "Room_1_1_144",
                "Room_1_1_150",
                "Room_1_1_184"]
        
        room_combobox = wx.ComboBox(self, choices=room_list)
        room_hbox.Add(room_combobox, proportion=8, flag=wx.TOP, border=5)
        vbox.Add(room_hbox, proportion=0, flag=wx.ALL, border=5)

        # confirm button
        self._add_confirm_button(vbox, 5)

        # add result label
        self._add_result_label(vbox)

        # add widget infomation to dict
        self.info_widget_dict["feeder"]["date_picker"] = dpc
        self.info_widget_dict["feeder"]["time_picker"] = tpc
        self.info_widget_dict["feeder"]["room_select"] = room_combobox


        # add result widget
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, label="Utilization")
        label.SetFont(self.font)
        hbox.Add(label, proportion=2, flag=wx.TOP|wx.RIGHT, border=5)
        occu_label = wx.StaticText(self, label="__")
        occu_label.SetFont(self.font)
        hbox.Add(occu_label, proportion=2, flag=wx.TOP|wx.RIGHT, border=5)
        vbox.Add(hbox, proportion=0, flag=wx.ALL, border=5)

        self.info_widget_dict["consumer"]["utilization_label"] = occu_label

        self.SetSizer(vbox)
        # https://stackoverflow.com/questions/42365239/wxpython-after-changing-panel-and-redo-layout-panel-is-very-small
        self.Fit()
        self.GetParent().SendSizeEvent()
