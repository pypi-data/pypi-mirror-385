from .base import BaseChipTransformer
from datetime import date, datetime
import inspect
import numpy as np
import pandas as pd
from neurostats_API.utils import StatsProcessor
from collections import defaultdict
from typing import List, Optional, Union

class US_F13_Transformer(BaseChipTransformer):
    def __init__(self, ticker, company_name, zone):
        super().__init__(ticker, company_name, zone)
        self.return_keys = ['chip_data']

    def process_transform(self, fetched_datas):
        """
        fetched_datas:[
            {

            }, ....
        ]
        """
        if not fetched_datas:
            return self._get_empty_structure()    # 若查無資料，回傳空表結構

        def flatten_nested_data(data_dict, key):
            pop_dict = data_dict.pop(key, {})
            for sub_key, value in pop_dict.items():
                data_dict[f"{key}_{sub_key}"] = value
            
            return data_dict

        result = [flatten_nested_data(data, 'votingAuthority') for data in fetched_datas]

        return_dict = {
            "ticker": self.ticker,
            "company_name": self.company_name,
            "chip_data": pd.DataFrame(result)
        }

        return return_dict

class US_CelebrityTransformer():

    def __init__(self):
        pass

    def process_transform(
        self,
        fetched_datas: List[dict],
        strftime: Optional[str] = None
    ) -> dict[str, dict[Union[str, datetime], float]]:
        
        result = defaultdict(lambda: defaultdict(dict))

        for record in fetched_datas:
            ticker = record.get("issuerTicker")
            report_date = record.get("reportDate")
            value = record.get("value")
            title = record.get("titleOfClass")

            if ticker and report_date and title:
                key = report_date.strftime(strftime) if strftime else report_date
                result.setdefault(ticker, {}).setdefault(title, {})[key] = value

        return dict(result)