from .base import BaseTEJTransformer
import pandas as pd

class TEJChipTransformer(BaseTEJTransformer):
    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)
        self.return_keys = ["chip_data"]
        

    def process_transform(
        self,
        fetched_data
    ):
        if (not fetched_data):
            return self._get_empty_structure()

        fetched_data = pd.DataFrame(fetched_data)

        return {
            "ticker": self.ticker,
            "company_name": self.company_name,
            "chip_data": fetched_data
        }
