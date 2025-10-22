from .base import AsyncBaseFetcher
from ..db_extractors import (
    AsyncDailyValueDBExtractor, AsyncTEJDailyValueDBExtractor, AsyncUS_CelebrityDBExtractor
)
from neurostats_API.async_mode.factory import get_extractor
from neurostats_API.transformers import US_F13_Transformer, US_CelebrityTransformer
from neurostats_API.utils import NotSupportedError


class AsyncUSChipF13Fetcher(AsyncBaseFetcher):
    def __init__(self, 
        ticker, 
        client,
        managerTicker = None,
    ):
        self.issuerTicker = ticker
        self.managerTicker = managerTicker
        self.transformer_map = {"us": US_F13_Transformer}
        try:
            self.extractor = get_extractor(
                "US_Chip_F13", ticker, client, managerTicker=self.managerTicker
            )

            company_name = self.extractor.get_company_name()
            zone = self.extractor.get_zone()

            transformer = self.get_transformer(zone)
            self.transformer = transformer(ticker, company_name, zone)

        except NotSupportedError as e:
            raise NotSupportedError(
                f"{self.__class__.__name__} only support {list(self.transformer_map.keys())} companies now, {ticker} is not available"
            ) from e

    async def query_data(
        self, start_date=None, end_date=None, get_latest=False
    ):
        fetched_data = await self.extractor.query_data(
            start_date, end_date, get_latest
        )

        transformed_data = self.transformer.process_transform(
            fetched_data
        )

        return transformed_data

class AsyncUSCelebrityFetcher(AsyncBaseFetcher):

    def __init__(self, client, manager_name):
        self.manager_name = manager_name
        self.extractor = AsyncUS_CelebrityDBExtractor(client, manager_name)
        self.transformer = US_CelebrityTransformer()

    async def query_data(
        self, start_date=None, end_date=None, get_latest=False,
        value_threshold=None, title=None, strftime=None
    ):
        fetched_data = await self.extractor.query_data(
            start_date, end_date, get_latest,
            value_throshold=value_threshold, title=title
        )

        transformed_data = self.transformer.process_transform(
            fetched_datas = list(fetched_data),
            strftime = strftime
        )

        return transformed_data