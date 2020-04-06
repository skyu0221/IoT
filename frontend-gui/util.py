import datetime
import wx
import pytz

def wxdate2pydate(date):
    f = date.Format('%y-%m-%d %H:%M')
    # print(f)
    x = datetime.datetime.strptime(f,'%y-%m-%d %H:%M')
    return x


def combine_datetime(date, time):
    str_date = "20" + date.Format('%y-%m-%d %H:%M:%S').split()[0]
    str_time = time.Format('%y-%m-%d %H:%M:%S').split()[1]
    
    datetime_object = datetime.datetime.strptime(str_date + " " + str_time, '%Y-%m-%d %H:%M:%S')
    source_timezone = pytz.timezone('Canada/Mountain')
    loc_dt = source_timezone.localize(datetime_object)

    target_timezone = pytz.timezone('UTC')
    
    gmt_dt = loc_dt.astimezone(target_timezone)

    result = gmt_dt.strftime("%Y-%m-%d %H:%M:%S")
    # print(result)
    
    return result


def convert_to_GMT_zone(datetime_object):
    source_timezone = pytz.timezone('Canada/Mountain')
    loc_dt = source_timezone.localize(datetime_object)

    target_timezone = pytz.timezone('UTC')
    gmt_dt = loc_dt.astimezone(target_timezone)

    result = gmt_dt.strftime("%Y-%m-%d %H:%M:%S")

    return result
    