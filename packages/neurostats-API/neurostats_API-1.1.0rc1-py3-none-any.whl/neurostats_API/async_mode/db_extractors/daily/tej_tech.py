from .base import BaseDailyTechDBExtractor
from pymongo import AsyncMongoClient, ASCENDING, DESCENDING

class AsyncTEJDailyTechDBExtractor(BaseDailyTechDBExtractor):

    def __init__(self, ticker, client):
        super().__init__(ticker, client)

    def _get_collection_name(self):
        self.collection_name_map = {"tw": "TEJ_share_price"}

        return self.collection_name_map.get(self.zone, None)

class AsyncBatchTechDBExtractor(BaseDailyTechDBExtractor):

    def __init__(self, ticker:list, client: AsyncMongoClient, zone:str):
        self.tickers = ticker
        self.zone = zone
        self.client = client

        self.collection_map = {
            'tw':{
                'db': "company_test",
                'collection': "twse_daily_share_price"
            },
            'us':{
                'db': "company_us",
                'collection': "us_technical"
            },            
        }

        db_name = self.collection_map.get(self.zone).get('db')
        collection_name = self.collection_map.get(self.zone).get('collection')
        self.collection = self.client.get_database(db_name).get_collection(collection_name)

    def _prepare_query(
        self, start_date=None, end_date=None, get_latest=False, sort_by_ticker = False
    ):
        query = {"ticker":{"$in": self.tickers}}

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
            query["date"] = date_range

        projection = {
            "_id": 0,
            "ticker": 1,
            "date": 1,
            "open": 1,
            "high": 1,
            "low": 1,
            "close": 1,
            "volume": 1
        }
        
        sort = []

        if (sort_by_ticker):
            sort += [("ticker", ASCENDING)]

        if (get_latest):
            sort += [("date", DESCENDING)]
        else:
            sort += [("date", ASCENDING)]

        return query, projection, sort
    
    async def query_data(
        self, start_date=None, end_date=None, get_latest=False, sort_by_ticker = False
    ):
        query, projection, sort = self._prepare_query(
            start_date=start_date, end_date=end_date, get_latest=get_latest, sort_by_ticker=sort_by_ticker
        )

        cursor = self.collection.find(query, projection).sort(sort)

        fetched_data = [data async for data in cursor]

        return fetched_data