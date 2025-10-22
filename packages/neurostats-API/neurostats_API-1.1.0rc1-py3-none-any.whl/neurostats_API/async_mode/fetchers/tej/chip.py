from datetime import datetime

from neurostats_API.async_mode.fetchers.base import AsyncBaseFetcher

from neurostats_API.async_mode.factory import get_extractor
from neurostats_API.transformers import TEJChipTransformer
from neurostats_API.utils import NotSupportedError

class AsyncTEJChipFetcher(AsyncBaseFetcher):
    def __init__(
        self,
        ticker,
        client
    ):
        self.ticker = ticker
        self.transformer_map = {"tw": TEJChipTransformer}
        try:
            self.extractor = get_extractor("TEJ_Chip", ticker, client)

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
            fetched_data = fetched_data
        )

        return transformed_data
