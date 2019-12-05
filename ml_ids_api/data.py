import pandas as pd
from typing import List


def deserialize_dataframe(request_body: str) -> pd.DataFrame:
    return pd.read_json(request_body, orient='split')


def merge_predictions(data: pd.DataFrame, predictions: List[int]) -> pd.DataFrame:
    data['prediction'] = predictions
    return data
