import numpy as np
from datetime import datetime, timedelta
import json
import os

start_work = 9 * 60 * 60  # Work start from 9:00. unit: second
end_work = 17 * 60 * 60  # Work end at 17:00. unit: second
daily_report = 16 * 60 * 60  # Daily progress report at 16:00, in meeting room
daily_report_mean = 15 * 60  # Daily progress report average length 15 min
daily_report_std = 1 * 60  # Daily progress report std.dev 1 min
come_leave_flex_coef = 30 * 60  # Tend to come 8:30, average arrive at 9:00. Leave is similar. Exponential distribution
call_for_absence = 0.01  # Possibility of not come to the office
lunch_start_time = 12 * 60 * 60  # Lunch serve start time 12:00. unit: second
lunch_end_time = 13 * 60 * 60  # Lunch serve end time 13:00. unit: second
eat_time_a = 10  # average time for each person to eat lunch. Beta distribution
eat_time_b = 50  # average time for each person to eat lunch. Beta distribution
cut_off_time = 14 * 60 * 60  # After this time, the person won't come to work
day_cut_off = 24 * 60 * 60
start_synthetic_data = datetime(2020, 3, 25)  # start date
end_synthetic_data = datetime(2020, 3, 27)  # end date
report_interval = timedelta(seconds=1)  # Time interval between two consecutive package
guest_lambda = 3  # Poisson arrival for unknown customers. unit: person per day
visit_colleague = 3  # How many times a worker goes to a colleague's office
average_stay_in_colleague_office = 30 * 60
std_stay_in_colleague_office = 4 * 60
average_stay_customer = 30 * 60
std_stay_customer = 5 * 60
sensor_type = ["Room_Outlet_Controller",
               "Room_Motion_Sensor",
               "Room_Temperature_Sensor",
               "Room_Lock_Controller",
               "Room_Door_Camera"]
# value = (np.random.beta(eat_time_a, eat_time_b, 10000) + 0.1) * 100

possible_locations = ["home", "Room_1_1_140", "Room_1_1_141", "Room_1_1_142", "Room_1_1_143", "Room_1_1_144",
                      "Room_1_1_150", "Room_1_1_184", "busy"]
walking_time = {"Room_1_1_140": {"Room_1_1_140": 0,
                                 "Room_1_1_141": 2,
                                 "Room_1_1_142": 2,
                                 "Room_1_1_143": 3,
                                 "Room_1_1_144": 4,
                                 "Room_1_1_150": 1,
                                 "Room_1_1_184": 2},
                "Room_1_1_141": {"Room_1_1_140": 2,
                                 "Room_1_1_141": 0,
                                 "Room_1_1_142": 3,
                                 "Room_1_1_143": 4,
                                 "Room_1_1_144": 5,
                                 "Room_1_1_150": 1,
                                 "Room_1_1_184": 2},
                "Room_1_1_142": {"Room_1_1_140": 2,
                                 "Room_1_1_141": 3,
                                 "Room_1_1_142": 0,
                                 "Room_1_1_143": 2,
                                 "Room_1_1_144": 2,
                                 "Room_1_1_150": 1,
                                 "Room_1_1_184": 3},
                "Room_1_1_143": {"Room_1_1_140": 3,
                                 "Room_1_1_141": 4,
                                 "Room_1_1_142": 2,
                                 "Room_1_1_143": 0,
                                 "Room_1_1_144": 2,
                                 "Room_1_1_150": 1,
                                 "Room_1_1_184": 4},
                "Room_1_1_144": {"Room_1_1_140": 4,
                                 "Room_1_1_141": 5,
                                 "Room_1_1_142": 2,
                                 "Room_1_1_143": 2,
                                 "Room_1_1_144": 0,
                                 "Room_1_1_150": 1,
                                 "Room_1_1_184": 5},
                "Room_1_1_150": {"Room_1_1_140": 1,
                                 "Room_1_1_141": 1,
                                 "Room_1_1_142": 1,
                                 "Room_1_1_143": 1,
                                 "Room_1_1_144": 1,
                                 "Room_1_1_150": 0,
                                 "Room_1_1_184": 1},
                "Room_1_1_184": {"Room_1_1_140": 2,
                                 "Room_1_1_141": 4,
                                 "Room_1_1_142": 4,
                                 "Room_1_1_143": 5,
                                 "Room_1_1_144": 5,
                                 "Room_1_1_150": 1,
                                 "Room_1_1_184": 0}}
lock_setting = {"Room_1_1_140": "Room_1_1_150",
                "Room_1_1_141": "Room_1_1_150",
                "Room_1_1_142": "Room_1_1_150",
                "Room_1_1_143": "Room_1_1_150",
                "Room_1_1_144": "Room_1_1_150",
                "Room_1_1_150": "Room_1_1_184",
                "Room_1_1_184": "home",
                "home": "Room_1_1_184"}

class Person:
    def __init__(self, name, email, office=None):
        self.name = name
        self.office = office
        self.email = email
        self.position = np.zeros(day_cut_off)

    def customer_come(self, start_time, end_time, dest):
        start_time = start_time - int(np.random.exponential(5 * 60))  # Come eariler than expected
        # decide the time takes from Room_1_1_150 door to the meeting room
        arrive_office = start_time - 3 + get_white_bias(1)
        # Decide the time takes to get to the building, average 3 second to the Room_1_1_150 door
        arrive_door = arrive_office - 3 + get_white_bias(1)

        # decide the time takes from meeting room to Room_1_1_150 door
        leave_office = end_time + 3 + get_white_bias(1)
        # Decide the time takes to leave to the building, average 3 second to the Room_1_1_150 door
        leave_door = end_time + 3 + get_white_bias(1)

        # Apply to the daily route
        self.position[start_time:arrive_door] = possible_locations.index("Room_1_1_184")
        self.position[arrive_door:arrive_office] = possible_locations.index("Room_1_1_150")
        self.position[arrive_office:leave_office] = possible_locations.index(dest)
        self.position[leave_office:leave_door] = possible_locations.index("Room_1_1_150")
        self.position[leave_door:end_time] = possible_locations.index("Room_1_1_184")

    def decide_come(self):
        """
        Each person need to decide if he/she will come to work today, when exactly they come, and when exactly
        they leave. Each person target to come at 8:30 am and leave at 5 pm, with a exponential distribution where
        mu = 30 minute. Use exponential distribution because people tend to come/leave on time with a very small
        chance of being late. In the meantime, assume that people directly goes into their own office right away.
        They require some time to walk to their office.
        :return: True if come to work, False otherwise
        """
        self.position = np.zeros(day_cut_off)
        # Decide absence
        if np.random.random() < call_for_absence:
            return False
        else:
            # Decide when come to office
            arrival_time = (start_work - come_leave_flex_coef) + int(np.random.exponential(come_leave_flex_coef))
            if arrival_time > cut_off_time:
                return False
            else:
                # Decide when go back home
                leave_time = end_work + int(np.random.exponential(come_leave_flex_coef))
                if leave_time >= day_cut_off:
                    leave_time = day_cut_off - 1

                # Decide the time takes to get to the building, average 3 second to the Room_1_1_150 door
                arrive_door = arrival_time + 3 + get_white_bias(1)
                # decide the time takes from Room_1_1_150 door to the office
                arrive_office = arrive_door + int(self.office[-3:]) - 138 + get_white_bias(1)

                # Decide the time takes to leave to the building, average 3 second to the Room_1_1_150 door
                leave_door = leave_time - 3 + get_white_bias(1)
                # decide the time takes from office to Room_1_1_150 door
                leave_office = leave_door - int(self.office[-3:]) + 138 + get_white_bias(1)

                # Apply to the daily route
                self.position[arrival_time:arrive_door] = possible_locations.index("Room_1_1_184")
                self.position[arrive_door:arrive_office] = possible_locations.index("Room_1_1_150")
                self.position[arrive_office:leave_office] = possible_locations.index(self.office)
                self.position[leave_office:leave_door] = possible_locations.index("Room_1_1_150")
                self.position[leave_door:leave_time] = possible_locations.index("Room_1_1_184")

                return True

    def generate_lunch(self):
        # Usually go for lunch immediately, with average delay of 5 minute
        lunch_delay = int(np.random.exponential(5 * 60))
        lunch_delay = max(lunch_delay, 20 * 60)

        time_in_corridor_go = lunch_start_time + lunch_delay + walking_time[self.office][
            "Room_1_1_184"] + get_white_bias(1)
        lunch_finish_time = time_in_corridor_go + int((np.random.beta(eat_time_a, eat_time_b) + 0.1) * 6000)
        time_in_corridor_back = lunch_finish_time + walking_time["Room_1_1_184"][self.office] + get_white_bias(1)

        # Apply to the daily route
        self.position[lunch_start_time:time_in_corridor_go] = possible_locations.index("Room_1_1_150")
        self.position[time_in_corridor_go:lunch_finish_time] = possible_locations.index("Room_1_1_184")
        self.position[lunch_finish_time:time_in_corridor_back] = possible_locations.index("Room_1_1_150")

    def generate_daily_meeting(self):
        # Arrive maximum 3 min early, 2 min late
        meeting_attend = int(np.random.exponential(3 * 60))
        meeting_attend = daily_report - max(meeting_attend, 5 * 60)
        time_in_corridor_go = meeting_attend - walking_time[self.office]["Room_1_1_141"] + get_white_bias(1)
        meeting_end = daily_report + int(np.random.normal(daily_report_mean, daily_report_std))
        time_in_corridor_back = meeting_end + walking_time["Room_1_1_141"][self.office] + get_white_bias(1)

        # Apply to the daily route
        self.position[time_in_corridor_go:meeting_attend] = possible_locations.index("Room_1_1_150")
        self.position[meeting_attend:meeting_end] = possible_locations.index("Room_1_1_141")
        self.position[meeting_end:time_in_corridor_back] = possible_locations.index("Room_1_1_150")

    def check_in_office(self, start, end):
        return np.sum(self.position[start:end] == possible_locations.index(self.office)) == (end - start)

    def get_in_office_range(self):
        in_office = np.concatenate(([0],
                                    np.equal(self.position, possible_locations.index(self.office)).view(np.int8),
                                    [0]))
        absdiff = np.abs(np.diff(in_office))
        # Runs start and end where absdiff is 1.
        ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
        return ranges

    def handle_customer(self, num_customer):
        # Set-up meeting time
        in_office_range = self.get_in_office_range()
        visit_length = int(np.random.normal(average_stay_customer, std_stay_customer))
        in_office_duration = in_office_range[:, 1] - in_office_range[:, 0]
        in_office_idx = np.nonzero(in_office_duration > visit_length)[0]
        if len(in_office_idx) == 0:
            visit_length = np.max(in_office_duration)
            in_office_idx = np.nonzero(in_office_duration == visit_length)[0]
        idx = np.random.choice(in_office_idx)
        start_time = np.random.randint(in_office_range[idx, 0], in_office_range[idx, 1] - visit_length + 1)
        end_time = start_time + visit_length

        in_room = start_time + walking_time[self.office]["Room_1_1_141"] + get_white_bias(1)
        out_room = end_time - walking_time["Room_1_1_141"][self.office] + get_white_bias(1)

        # Decide meeting location
        if num_customer > 1:
            # Go meet in meeting room
            room_name = "Room_1_1_141"
            self.position[start_time:in_room] = possible_locations.index("Room_1_1_150")
            self.position[in_room:out_room] = possible_locations.index("Room_1_1_141")
            self.position[out_room:end_time] = possible_locations.index("Room_1_1_150")
        else:
            self.position[in_room:out_room] = possible_locations.index("busy")
            room_name = self.office

        return in_room, out_room, room_name

    def generate_go_other_office(self):
        for _ in range(np.random.poisson(visit_colleague)):
            # Find available time for current person to meet some colleague
            in_office_range = self.get_in_office_range()
            visit_length = int(np.random.normal(average_stay_in_colleague_office, std_stay_in_colleague_office))
            in_office_idx = np.nonzero((in_office_range[:, 1] - in_office_range[:, 0]) > visit_length)[0]
            if len(in_office_idx) == 0:
                continue
            idx = np.random.choice(in_office_idx)
            start_time = np.random.randint(in_office_range[idx, 0], in_office_range[idx, 1] - visit_length + 1)
            end_time = start_time + visit_length

            # Find available colleague
            for coworker in worker_assign:
                if coworker.check_in_office(start_time, end_time):
                    # Go meet the colleague
                    in_colleague = start_time + walking_time[self.office][coworker.office] + get_white_bias(1)
                    out_colleague = end_time - walking_time[coworker.office][self.office] + get_white_bias(1)

                    self.position[start_time:in_colleague] = possible_locations.index("Room_1_1_150")
                    self.position[in_colleague:out_colleague] = possible_locations.index(coworker.office)
                    self.position[out_colleague:end_time] = possible_locations.index("Room_1_1_150")

                    coworker.position[in_colleague:out_colleague] = possible_locations.index("busy")
                    break

    def generate_daily_route(self, customer_list):
        time_list = list()
        self.generate_lunch()
        self.generate_daily_meeting()
        for num_customer in customer_list:
            time_list.append(self.handle_customer(num_customer))
        self.generate_go_other_office()
        return time_list

    def get_position(self, sec):
        if self.position[sec] == possible_locations.index("busy"):
            return self.office
        return possible_locations[int(self.position[sec])]

    def get_trigger(self):
        pass


def get_white_bias(second):
    return np.random.randint(second * 2 + 1) - second


worker_assign = [Person("Employee 1", "employee1@company.com", "Room_1_1_140"),
                 Person("Employee 2", "employee2@company.com", "Room_1_1_142"),
                 Person("Employee 3", "employee3@company.com", "Room_1_1_144"),
                 Person("Employee 4", "employee4@company.com", "Room_1_1_143")]


def generate_daily_data():
    available_worker = list()
    for i, worker in enumerate(worker_assign):
        if worker.decide_come():
            available_worker.append(i)

    # print(available_worker)

    guests = np.random.poisson(guest_lambda)
    guest_assign = np.random.choice(available_worker, size=guests)
    all_people = list()
    guest_counter = 0

    for i in available_worker:
        worker = worker_assign[i]
        all_people.append(worker)
        guest_list = np.random.randint(1, 4, size=np.sum(guest_assign == i))
        appointments = worker.generate_daily_route(guest_list)
        for j, appointment in enumerate(appointments):
            for _ in range(guest_list[j]):
                new_guest = Person(f"Guest {guest_counter}", "")
                guest_counter += 1
                new_guest.customer_come(*appointment)
                all_people.append(new_guest)

    return all_people, str(datetime.now())[:10]


class Sensor:
    def __init__(self, label, uuid, brick_name, room):
        if label == "Room_Temperature_Sensor":
            self.data = {'deviceId': uuid,
                         'name': label,
                         'label': label,
                         'locationId': '76bf589a-a8d9-471b-9db6-d4838e9eea6f',
                         'roomId': room,
                         'deviceTypeId': brick_name,
                         'deviceTypeName': 'SmartSense Button',
                         'deviceNetworkType': 'ZIGBEE',
                         'components': [{'id': 'main',
                                         'capabilities': [{'id': 'temperatureMeasurement', 'version': 1},
                                                          {'id': 'battery', 'version': 1},
                                                          {'id': 'configuration', 'version': 1},
                                                          {'id': 'refresh', 'version': 1},
                                                          {'id': 'button', 'version': 1},
                                                          {'id': 'sensor', 'version': 1},
                                                          {'id': 'healthCheck', 'version': 1},
                                                          {'id': 'holdableButton', 'version': 1}]}],
                         'dth': {'deviceTypeId': brick_name,
                                 'deviceTypeName': 'SmartSense Button',
                                 'deviceNetworkType': 'ZIGBEE',
                                 'completedSetup': True,
                                 'networkSecurityLevel': 'UNKNOWN',
                                 'hubId': 'ede0ef78-70b7-4756-9dd6-db82d33fc9eb'},
                         'type': 'DTH'}
            self.response = {'components': {'main': {'battery': {'battery': {'unit': '%', 'value': 95}},
                                                     'button': {'button': {'value': 'pushed'},
                                                                'numberOfButtons': {'value': 1},
                                                                'supportedButtonValues': {'value': ['pushed',
                                                                                                    'held',
                                                                                                    'double']}},
                                                     'configuration': {},
                                                     'healthCheck': {'DeviceWatch-DeviceStatus': {'value': None},
                                                                     'DeviceWatch-Enroll': {
                                                                         'value': {'checkInterval': 7260,
                                                                                   'hubHardwareId': '0035',
                                                                                   'lowBatteryThresholds': [15,
                                                                                                            7,
                                                                                                            3],
                                                                                   'offlinePingable': '1',
                                                                                   'protocol': 'zigbee',
                                                                                   'scheme': 'TRACKED'}},
                                                                     'checkInterval': {'data': {'hubHardwareId': '0035',
                                                                                                'offlinePingable': '1',
                                                                                                'protocol': 'zigbee'},
                                                                                       'unit': 's',
                                                                                       'value': 720},
                                                                     'healthStatus': {'value': None}},
                                                     'holdableButton': {'button': {'value': 'pushed'},
                                                                        'numberOfButtons': {'value': 1}},
                                                     'refresh': {},
                                                     'sensor': {},
                                                     'temperatureMeasurement': {'temperature': {'unit': 'C',
                                                                                                'value': 26}}}}}
        elif label == "Room_Outlet_Controller":
            self.data = {'deviceId': uuid,
                         'name': label,
                         'label': label,
                         'locationId': '76bf589a-a8d9-471b-9db6-d4838e9eea6f',
                         'roomId': room,
                         'deviceTypeId': brick_name,
                         'deviceTypeName': 'SmartPower Outlet',
                         'deviceNetworkType': 'ZIGBEE',
                         'components': [{'id': 'main',
                                         'capabilities': [{'id': 'switch', 'version': 1},
                                                          {'id': 'configuration', 'version': 1},
                                                          {'id': 'refresh', 'version': 1},
                                                          {'id': 'powerMeter', 'version': 1},
                                                          {'id': 'sensor', 'version': 1},
                                                          {'id': 'actuator', 'version': 1},
                                                          {'id': 'healthCheck', 'version': 1},
                                                          {'id': 'outlet', 'version': 1}]}],
                         'dth': {'deviceTypeId': brick_name,
                                 'deviceTypeName': 'SmartPower Outlet',
                                 'deviceNetworkType': 'ZIGBEE',
                                 'completedSetup': True,
                                 'networkSecurityLevel': 'UNKNOWN',
                                 'hubId': 'ede0ef78-70b7-4756-9dd6-db82d33fc9eb'},
                         'type': 'DTH'}
            self.response = {'components': {'main': {'actuator': {},
                                                     'configuration': {},
                                                     'healthCheck': {'DeviceWatch-DeviceStatus': {'value': None},
                                                                     'DeviceWatch-Enroll': {'value': None},
                                                                     'checkInterval': {'data': {'hubHardwareId': '0035',
                                                                                                'protocol': 'zigbee'},
                                                                                       'unit': 's',
                                                                                       'value': 720},
                                                                     'healthStatus': {'value': None}},
                                                     'outlet': {'switch': {'value': 'on'}},
                                                     'powerMeter': {'power': {'unit': 'W', 'value': 0.0}},
                                                     'refresh': {},
                                                     'sensor': {},
                                                     'switch': {'switch': {'value': 'on'}}}}}

        elif label == "Room_Lock_Controller":
            self.data = {'deviceId': uuid,
                         'name': label,
                         'label': label,
                         'deviceManufacturerCode': '033F-0001-0001',
                         'locationId': '76bf589a-a8d9-471b-9db6-d4838e9eea6f',
                         'roomId': room,
                         'deviceTypeId': brick_name,
                         'deviceTypeName': 'Z-Wave Lock Without Codes',
                         'deviceNetworkType': 'ZWAVE',
                         'components': [{'id': 'main',
                                         'capabilities': [{'id': 'battery', 'version': 1},
                                                          {'id': 'configuration', 'version': 1},
                                                          {'id': 'lock', 'version': 1},
                                                          {'id': 'refresh', 'version': 1},
                                                          {'id': 'sensor', 'version': 1},
                                                          {'id': 'actuator', 'version': 1},
                                                          {'id': 'healthCheck', 'version': 1}]}],
                         'dth': {'deviceTypeId': brick_name,
                                 'deviceTypeName': 'Z-Wave Lock Without Codes',
                                 'deviceNetworkType': 'ZWAVE',
                                 'completedSetup': True,
                                 'networkSecurityLevel': 'ZWAVE_S0_DOWNGRADE',
                                 'hubId': 'ede0ef78-70b7-4756-9dd6-db82d33fc9eb'},
                         'type': 'DTH'}
            self.response = {'components': {'main': {'actuator': {},
                                                     'battery': {'battery': {'unit': '%', 'value': 100}},
                                                     'configuration': {},
                                                     'healthCheck': {'DeviceWatch-DeviceStatus': {'data': {},
                                                                                                  'value': None},
                                                                     'DeviceWatch-Enroll': {'value': None},
                                                                     'checkInterval': {'data': {'hubHardwareId': '0035',
                                                                                                'offlinePingable': '1',
                                                                                                'protocol': 'zwave'},
                                                                                       'unit': 's',
                                                                                       'value': 3600},
                                                                     'healthStatus': {'data': {},
                                                                                      'value': None}},
                                                     'lock': {'lock': {'data': {}, 'value': 'locked'}},
                                                     'refresh': {},
                                                     'sensor': {}}}}

        elif label == "Room_Motion_Sensor":
            self.data = {'deviceId': uuid,
                         'name': label,
                         'label': label,
                         'locationId': '76bf589a-a8d9-471b-9db6-d4838e9eea6f',
                         'roomId': room,
                         'deviceTypeId': brick_name,
                         'deviceTypeName': 'SmartSense Motion Sensor',
                         'deviceNetworkType': 'ZIGBEE',
                         'components': [{'id': 'main',
                                         'capabilities': [{'id': 'temperatureMeasurement', 'version': 1},
                                                          {'id': 'battery', 'version': 1},
                                                          {'id': 'motionSensor', 'version': 1},
                                                          {'id': 'configuration', 'version': 1},
                                                          {'id': 'refresh', 'version': 1},
                                                          {'id': 'sensor', 'version': 1},
                                                          {'id': 'healthCheck', 'version': 1}]}],
                         'dth': {'deviceTypeId': brick_name,
                                 'deviceTypeName': 'SmartSense Motion Sensor',
                                 'deviceNetworkType': 'ZIGBEE',
                                 'completedSetup': True,
                                 'networkSecurityLevel': 'UNKNOWN',
                                 'hubId': 'ede0ef78-70b7-4756-9dd6-db82d33fc9eb'},
                         'type': 'DTH'}
            self.response = {'components': {'main': {'battery': {'battery': {'unit': '%', 'value': 100}},
                                                     'configuration': {},
                                                     'healthCheck': {'DeviceWatch-DeviceStatus': {'value': None},
                                                                     'DeviceWatch-Enroll': {
                                                                         'value': {'checkInterval': 7260,
                                                                                   'hubHardwareId': '0035',
                                                                                   'lowBatteryThresholds': [15,
                                                                                                            7,
                                                                                                            3],
                                                                                   'offlinePingable': '1',
                                                                                   'protocol': 'zigbee',
                                                                                   'scheme': 'TRACKED'}},
                                                                     'checkInterval': {'data': {'hubHardwareId': '0035',
                                                                                                'offlinePingable': '1',
                                                                                                'protocol': 'zigbee'},
                                                                                       'unit': 's',
                                                                                       'value': 720},
                                                                     'healthStatus': {'data': {},
                                                                                      'value': None}},
                                                     'motionSensor': {'motion': {'value': 'inactive'}},
                                                     'refresh': {},
                                                     'sensor': {},
                                                     'temperatureMeasurement': {'temperature': {'unit': 'C',
                                                                                                'value': 27}}}}}
        elif label == "Room_Door_Camera":
            self.data = {'deviceId': uuid,
                         'name': label,
                         'label': label,
                         'deviceManufacturerCode': 'Synthetic',
                         'locationId': '76bf589a-a8d9-471b-9db6-d4838e9eea6f',
                         'roomId': room,
                         'deviceTypeId': brick_name,
                         'deviceTypeName': 'Z-Wave Door Camera',
                         'deviceNetworkType': 'ZWAVE',
                         'components': [{'id': 'main',
                                         'capabilities': [{'id': 'configuration', 'version': 1},
                                                          {'id': 'face', 'version': 1},
                                                          {'id': 'refresh', 'version': 1},
                                                          {'id': 'actuator', 'version': 1},
                                                          {'id': 'healthCheck', 'version': 1}]}],
                         'dth': {'deviceTypeId': brick_name,
                                 'deviceTypeName': 'Z-Wave Door Camera',
                                 'deviceNetworkType': 'ZWAVE',
                                 'completedSetup': True,
                                 'networkSecurityLevel': 'UNKNOWN',
                                 'hubId': 'ede0ef78-70b7-4756-9dd6-db82d33fc9eb'},
                         'type': 'DTH'}
            self.response = {'components': {'main': {'actuator': {},
                                                     'configuration': {},
                                                     'healthCheck': {'DeviceWatch-DeviceStatus': {'value': None},
                                                                     'DeviceWatch-Enroll': {'value': None},
                                                                     'checkInterval': {'data': {'hubHardwareId': '0035',
                                                                                                'protocol': 'zigbee'},
                                                                                       'unit': 's',
                                                                                       'value': 3600},
                                                                     'healthStatus': {'value': None}},
                                                     'face': {'face': {'name': ['Alice', 'Bob', 'Charlie'], 'email': ['123@gmail.com']}},
                                                     'refresh': {},
                                                     'sensor': {}}}}
        else:
            self.data = {'deviceId': uuid,
                         'name': label,
                         'label': label,
                         'locationId': '76bf589a-a8d9-471b-9db6-d4838e9eea6f',
                         'components': [{'id': 'main',
                                         'capabilities': [{'id': 'bridge', 'version': 1}]}],
                         'childDevices': [{'deviceId': '709459f7-dd70-43b7-b4d7-c4a4b4ab885a'}],
                         'profile': {'id': '3e28a82b-ba46-3f7e-80ea-432e23069551'},
                         'type': 'HUB'}
            self.response = None

    def generate_json(self, current, all_person):
        if self.response is None:
            return json.dumps({})
        temp = 26
        outlet = "off"
        power = 0
        lock = "locked"
        motion = "inactive"
        names = list()
        emails = list()
        sec = current.second + 60 * current.minute + 60 * 60 * current.hour
        if self.data["name"] == "Room_Temperature_Sensor":
            temp = self.get_temp(sec, all_person)
        elif self.data["name"] == "Room_Outlet_Controller":
            outlet, power = self.get_outlet()
        elif self.data["name"] == "Room_Lock_Controller":
            lock = self.get_lock(sec, all_person)
        elif self.data["name"] == "Room_Motion_Sensor":
            motion = self.get_motion(sec, all_person)
        elif self.data["name"] == "Room_Door_Camera":
            names, emails = self.get_face(sec, all_person)

        if self.data["name"] == "Room_Temperature_Sensor":
            self.response["components"]["main"]["temperatureMeasurement"]["temperature"]["value"] = temp

        elif self.data["name"] == "Room_Outlet_Controller":
            self.response["components"]["main"]["outlet"]["switch"]["value"] = outlet
            self.response["components"]["main"]["switch"]["switch"]["value"] = \
                self.response["components"]["main"]["outlet"]["switch"]["value"]
            if self.response["components"]["main"]["outlet"]["switch"]["value"] == "off":
                self.response["components"]["main"]["powerMeter"]["power"]["value"] = 0.0
            else:
                self.response["components"]["main"]["powerMeter"]["power"]["value"] = power
        elif self.data["name"] == "Room_Lock_Controller":
            self.response["components"]["main"]["lock"]["lock"]["value"] = lock
        elif self.data["name"] == "Room_Motion_Sensor":
            self.response["components"]["main"]["motionSensor"]["motion"]["value"] = motion
        elif self.data["name"] == "Room_Door_Camera":
            self.response["components"]["main"]["face"]["face"]["name"] = names
            self.response["components"]["main"]["face"]["face"]["email"] = emails

        # file_name = str(current).replace(' ', '_').replace(':', '_').replace('-', '_') + \
        #             '_' + self.data["roomId"] + \
        #             '_' + self.data["name"] + '.json'
        # with open("output/" + file_name, 'w') as json_out:
        #     json.dump(self.response, json_out)
        # print(self.response)
        return json.dumps(self.response)

    def get_temp(self, sec, all_person):
        temp = 26
        for person in all_person:
            if person.get_position(sec) == self.data["roomId"]:
                temp += 0.5
        return temp

    def get_outlet(self):
        return np.random.choice(["on", "off"], p=[0.85, 0.15]), np.random.randint(10, 61) / 10

    def get_lock(self, sec, all_person):
        for person in all_person:
            for delay_sec in range(1, 3):
                if person.get_position(sec) == self.data["roomId"]:
                    # Get into the room
                    if sec - delay_sec < 0:
                        continue
                    if person.get_position(sec - delay_sec) == lock_setting[self.data["roomId"]]:
                        return "unlocked"

                    # Get out of the room
                    if sec + delay_sec >= 86400:
                        continue
                    if person.get_position(sec + delay_sec) == lock_setting[self.data["roomId"]]:
                        return "unlocked"
        return "locked"

    def get_motion(self, sec, all_person):
        for person in all_person:
            if person.get_position(sec) == self.data["roomId"]:
                # print("Yes!")
                return "active"
        return "inactive"

    def get_face(self, sec, all_person):
        name = list()
        email = list()
        for person in all_person:
            for delay_sec in range(1, 5):
                if person.get_position(sec) == self.data["roomId"]:
                    # Get into the room
                    if sec - delay_sec < 0:
                        continue
                    if person.get_position(sec - delay_sec) == lock_setting[self.data["roomId"]]:
                        name.append(person.name)
                        email.append(person.email)
                        break

                    # Get out of the room
                    if sec + delay_sec >= 86400:
                        continue
                    if person.get_position(sec + delay_sec) == lock_setting[self.data["roomId"]]:
                        name.append(person.name)
                        email.append(person.email)
                        break
        # if len(name) != 0:
        #     print(name)
        return name, email

def get_sensor_data(uuid, current, all_people):
    for sensor in sensors:
        if sensor.data["deviceId"] == uuid:
            return sensor.generate_json(current, all_people)
    return json.dumps({"Error": "deviceId Invalid"})

def get_all_sensor_data(current, all_people):
    result = {"time": str(current), "data": dict()}
    for sensor in sensors:
        uuid = sensor.data["deviceId"]
        result["data"][uuid] = json.loads(sensor.generate_json(current, all_people))
    return result

def get_sensor_setting():
    scanned_devices = {"items": list(), "_links": {}}
    for sensor in sensors:
        scanned_devices["items"].append(sensor.data)
    return scanned_devices

def main():
    sensors = list()
    # label, uuid, brick_name, room
    with open("sensor_config.json", 'r') as json_file:
        sensor_config = json.load(json_file)
        for room in sensor_config:
            for brick in sensor_config[room]:
                uuid = sensor_config[room][brick]["UUID"]
                label = sensor_config[room][brick]["Type"]
                sensors.append(Sensor(label, uuid, brick, room))

    sensors.append(Sensor("SmartThings v3 Hub", "ede0ef78-70b7-4756-9dd6-db82d33fc9eb", None, None))
    # Generate sensor report
    with open("scanned_devices.json", 'w') as json_file:
        scanned_devices = {"items": list(), "_links": {}}
        for sensor in sensors:
            scanned_devices["items"].append(sensor.data)
        json.dump(scanned_devices, json_file, indent=4)

    current = start_synthetic_data
    all_people = list()
    results = dict()
    for _ in range(int((end_synthetic_data - start_synthetic_data) / report_interval)):
        # print(current)
        results[str(current)[-8:].replace(':', '_')] = dict()
        if current.hour + current.minute + current.second == 0:
            # Generate a whole day data
            all_people = generate_daily_data()
        # for person in all_people:
        #     print(person.get_position(current.second + 60 * current.minute + 60 * 60 * current.hour))

        for sensor in sensors:
            sensor.generate_json(current, all_people, results)
        current += report_interval

        if current.hour + current.minute + current.second == 0:
            time_str = str(current)[:10].replace(' ', '_').replace('-', '_')
            with open(f"output/{time_str}", 'w') as json_out:
                json.dump(results, json_out)
            results = dict()

sensors = list()
# label, uuid, brick_name, room
with open("sensor_config.json", 'r') as json_file:
    sensor_config = json.load(json_file)
    for room in sensor_config:
        for brick in sensor_config[room]:
            uuid = sensor_config[room][brick]["UUID"]
            label = sensor_config[room][brick]["Type"]
            sensors.append(Sensor(label, uuid, brick, room))

sensors.append(Sensor("SmartThings v3 Hub", "ede0ef78-70b7-4756-9dd6-db82d33fc9eb", None, None))
# print(len(np.nonzero(np.array([False, False, True]))[0]))

# value = (np.random.beta(eat_time_a, eat_time_b, 10000) + 0.1) * 100
# print(24 * 60 * 60)
# plt.hist(value)
# plt.show()
