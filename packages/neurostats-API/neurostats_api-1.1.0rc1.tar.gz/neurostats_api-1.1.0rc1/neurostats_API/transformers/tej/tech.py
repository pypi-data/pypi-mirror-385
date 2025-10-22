from .base import BaseTEJTransformer
import pandas as pd


class TEJTechTransformer(BaseTEJTransformer):

    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)
        self.fetched_data = None

    def process_transform(self, fetched_data):
        self.fetched_data = pd.DataFrame(fetched_data)

        self.fetched_data = self.fetched_data.rename(
            columns={
                "open_d": "open",
                "high_d": "high",
                "low_d": "low",
                "close_d": "close",
                "vol": "volume"
            }
        )

        return self.fetched_data
