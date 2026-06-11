import datetime
import nepali_datetime

def run():
    today_ad = datetime.date.today()
    today_bs = nepali_datetime.date.from_datetime_date(today_ad)

    # BS first day of month
    start_bs = nepali_datetime.date(today_bs.year, today_bs.month, 1)

    # BS last day of month
    if today_bs.month == 12:
        end_bs = nepali_datetime.date(today_bs.year + 1, 1, 1)
    else:
        end_bs = nepali_datetime.date(today_bs.year, today_bs.month + 1, 1)

    end_bs = end_bs - datetime.timedelta(days=1)

    # convert BS → AD
    start_ad = start_bs.to_datetime_date()
    end_ad = end_bs.to_datetime_date()
    return {
        "start_bs": start_bs,
        "end_bs": end_bs,
        "start_ad": start_ad,
        "end_ad": end_ad,
    }