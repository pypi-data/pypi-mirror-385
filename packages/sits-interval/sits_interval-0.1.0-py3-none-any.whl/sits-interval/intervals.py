from datetime import *

def is_leap_year(year):
    return (year % 4 == 0) and (year % 100 != 0 or year % 400 == 0)


def generate_intervals(year, gap=7):
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    intervals = []
    current_date = start_date

    leap = is_leap_year(year)
    # feb_28 = date(year, 2, 28)

    left = 365 % gap
    interval_count = 365 // gap

    extra = interval_count - left

    while current_date <= end_date:
        if extra == 0:
            interval_length = gap + 1
        else:
            extra -= 1
            interval_length = gap

        if leap and current_date <= date(year, 2, 29) <= current_date + timedelta(days=gap):
            interval_length = gap + 1

        interval_end = current_date + timedelta(days=interval_length - 1)
        if interval_end > end_date:
            interval_end = end_date

        intervals.append((current_date.strftime("%Y-%m-%d"), interval_end.strftime("%Y-%m-%d")))

        current_date = interval_end + timedelta(days=1)
    return intervals

def get_Intevels(stdate,eddate,gap=7):
    st_year = datetime.strptime(stdate, "%Y-%m-%d").year
    ed_year = datetime.strptime(eddate, "%Y-%m-%d").year
    if st_year == ed_year:
        yearInterval = generate_intervals(st_year,gap)
        for index,interval in enumerate(yearInterval):
            if interval[0] <= stdate <= interval[1]:
                print("start")
                start= interval[0]
                start_index = index
            if interval[0] <= eddate <= interval[1]:
                end= interval[1]
                end_index = index
                break
        print(start,stdate,eddate,end)
        date_list = yearInterval[start_index:end_index]
    else:
        year1Interval = generate_intervals(st_year,gap)
        year2Interval = generate_intervals(ed_year,gap)
        for index,interval in enumerate(year1Interval):
            if interval[0] <= stdate <= interval[1]:
                start= interval[0]
                start_index = index
        for index,interval in enumerate(year2Interval):
            if interval[0] <= eddate <= interval[1]:
                end= interval[1]
                end_index = index

        print(start,stdate,eddate,end)
        date_list = year1Interval[start_index:] + year2Interval[:end_index]
    return start,end, date_list