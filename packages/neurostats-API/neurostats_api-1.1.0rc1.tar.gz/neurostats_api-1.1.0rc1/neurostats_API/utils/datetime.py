from datetime import datetime
from pytz import timezone

class StatsDateTime():

    def __init__(self, date, year, month, day, season):
        self.date = date
        self.year = year
        self.month = month
        self.day = day
        self.season = season
    
    @classmethod
    def get_today(cls):
        today = datetime.today()
        this_year = today.year
        this_month = today.month
        this_day = today.day
        this_season = ((this_month - 1) // 3) + 1

        return StatsDateTime(today, this_year, this_month, this_day,
                             this_season)

    @classmethod
    def get_latest_time(cls, ticker, collection):
        return collection.find_one(
            { "ticker" : ticker }, 
            { "_id": 0, "last_update_time": 1 }
        )

    @classmethod
    def transform_date(cls, date, tz:str = None):
        if (isinstance(date, str)):
            try:
                date = datetime.strptime(date, "%Y-%m-%d")
                if (tz):
                    date = date.astimezone(tz = timezone(tz))
                return date 
            except Exception as e:
                print(e)
                raise ValueError(
                    "date string format imcompatible, should be \"YYYY-MM-DD\""
                )
        elif (isinstance(date, datetime)):
            if (tz):
                return date.astimezone(tz = timezone(tz))
            else:
                return date
        else:
            raise ValueError(
                "date type imcompatible, should be string(\"YYYY-MM-DD\") or datetime.datetime"
            )