from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from datetime import datetime
import requests
import json
from hello.data_generator import generate_daily_data, get_sensor_data, get_sensor_setting, get_all_sensor_data

all_people = ['', '']

possible_locations = ["home", "Room_1_1_140", "Room_1_1_141", "Room_1_1_142", "Room_1_1_143", "Room_1_1_144",
                      "Room_1_1_150", "Room_1_1_184", "busy"]

# Create your views here.
def index(request):
    
    r = requests.get('http://httpbin.org/status/418')
    return HttpResponse('<pre>' + r.text + '</pre>')

# Create your views here.
def tester(request, uuid=None):
    if request.headers["Authorization"] == "Bearer 7b8e7f8b-63cc-465c-9dad-b488b2351096":
        check_update()
        if uuid is not None:
            request_sec = datetime.now()
            if request.headers.get("time", None):
                request_sec = datetime.strptime(request.headers["time"], '%Y-%m-%d %H:%M:%S')
            data = json.loads(get_sensor_data(uuid, request_sec, all_people[0]))
            return JsonResponse(data)
    return HttpResponse("failed to identify your identity")

def all_data(request):
    if request.headers["Authorization"] == "Bearer 7b8e7f8b-63cc-465c-9dad-b488b2351096":
        check_update()
        request_sec = datetime.now()
        if request.headers.get("time", None):
            request_sec = datetime.strptime(request.headers["time"], '%Y-%m-%d %H:%M:%S')
        print(1)
        data = get_all_sensor_data(request_sec, all_people[0])
        return JsonResponse(data)
    return HttpResponse("failed to identify your identity")

def get_truth(request):
    if request.headers["Authorization"] == "Bearer 7b8e7f8b-63cc-465c-9dad-b488b2351096":
        check_update()
        result = dict()
        for person in all_people[0]:
            result[person.name] = dict()
            result[person.name]["Position"] = list(person.position)
            result[person.name]["Office"] = person.office
        return JsonResponse(result)
    return HttpResponse("failed to identify your identity")

def get_devices(request):
    if request.headers["Authorization"] == "Bearer 7b8e7f8b-63cc-465c-9dad-b488b2351096":
        return JsonResponse(get_sensor_setting())
    return HttpResponse("failed to identify your identity")

def get_locations(request):
    if request.headers["Authorization"] == "Bearer 7b8e7f8b-63cc-465c-9dad-b488b2351096":
        check_update()
        result = dict()
        current = datetime.now()
        sec = current.second + 60 * current.minute + 60 * 60 * current.hour
        for person in all_people[0]:
            result[person.name] = possible_locations[int(person.position[sec])]
        return JsonResponse(result)
    return HttpResponse("failed to identify your identity")

def check_update():
    global all_people
    if all_people[1] != str(datetime.now())[:10]:
        all_people = generate_daily_data()
