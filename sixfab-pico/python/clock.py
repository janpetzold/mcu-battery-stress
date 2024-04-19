from machine import RTC

def get_current_time():
    rtc = RTC()
    year, month, day, _, hour, minute, second, _ = rtc.datetime()
    # Format the timestamp as ISO8601 - this assumes the RTC is set to UTC time
    return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(year, month, day, hour, minute, second)