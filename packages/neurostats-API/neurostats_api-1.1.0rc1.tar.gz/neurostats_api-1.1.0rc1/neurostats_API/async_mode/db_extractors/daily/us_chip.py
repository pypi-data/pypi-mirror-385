from datetime import datetime, timedelta
from pymongo import ASCENDING, DESCENDING
from .base import BaseDailyTechDBExtractor
from neurostats_API.utils import (
    NotSupportedError, StatsProcessor
)
from pymongo import AsyncMongoClient

class AsyncUS_F13DBExtractor(BaseDailyTechDBExtractor):

    def __init__(self, ticker, client, managerTicker=None):
        """
        ticker: Issuer Ticker, 被持有的股票代碼
        managerTicker: 持有者的股票代碼
        """
        super().__init__(ticker, client)
        self.issuerTicker = ticker
        self.managerTicker = managerTicker

        if (self.get_zone() not in ['us']):
            raise NotSupportedError("Supports US Company Only")

    def _get_collection_name(self):
        self.collection_name_map = {"us": "us_F13"}

        return self.collection_name_map.get(self.zone, None)

    def _prepare_query(self, start_date=None, end_date=None, get_latest=False):
        query = {"issuerTicker": self.issuerTicker}

        if (self.managerTicker):
            query.update(
                {
                    "managerTicker": self.managerTicker
                }
            )

        query = self._update_query_with_date(query, start_date, end_date)

        projection = {
            "_id": 0,
        }

        if (get_latest):
            sort = [("reportDate", DESCENDING)]
        else:
            sort = [("reportDate", ASCENDING)]

        return query, projection, sort

    def _update_query_with_date(self, query, start_date, end_date):
        start_date = self._transform_date(start_date)
        end_date = self._transform_date(end_date)

        date_range = {"$gte": start_date, "$lte": end_date}

        query.update({"reportDate": date_range})

        return query

    async def query_data(
        self, start_date=None, end_date=None, get_latest=False
    ):
        result = await super().query_data(start_date, end_date, get_latest)

        return result

class AsyncUS_CelebrityDBExtractor(AsyncUS_F13DBExtractor):
    """        
    用於查詢美國名人持股的專用extractor
    """
    def __init__(self, client:AsyncMongoClient, manager_name=None):
        """
        manager_name: 名人名稱
        """
        self.client = client
        self.zone = "us"
        self.manager = manager_name
        self.collection_name_map = {"us": "us_F13"}
        self.collection = self.client.get_database("company_us").get_collection("us_F13")
    

    def _get_collection_name(self):

        return self.collection_name_map.get(self.zone, None)
    
    def _prepare_query(
            self, start_date=None, end_date=None, get_latest=False,
            value_throshold=None, title=None
        ):
        query = {"manager": self.manager}

        if start_date:
            start_date = self._transform_date(start_date)
        if end_date:
            end_date = self._transform_date(end_date)

        if start_date or end_date:
            date_range = {}
            if start_date:
                date_range["$gte"] = start_date
            if end_date:
                date_range["$lte"] = end_date
            query["reportDate"] = date_range

        if value_throshold:
            query["value"] = {"$gt": value_throshold}

        if title:
            query["titleOfClass"] = title

        projection = {"_id": 0}

        if (get_latest):
            sort = [("reportDate", DESCENDING)]
        else:
            sort = [("reportDate", ASCENDING)]

        return query, projection, sort
    
    async def query_data(
        self, start_date=None, end_date=None, get_latest=False,
        value_throshold=None, title=None
    ):
        query, projection, sort = self._prepare_query(
            start_date=start_date, end_date=end_date, get_latest=get_latest,
            value_throshold=value_throshold, title=title
        )

        if (get_latest):
            cursor = self.collection.find(query, projection).sort(sort).limit(1)
        else:
            cursor = self.collection.find(query, projection).sort(sort)

        fetched_data = [data async for data in cursor]

        return fetched_data
    