"""
Utilities for Pandas DataFrame manipulation.
"""
from typing import List
import pandas as pd


def deserialize_dataframe(json_dataframe: str) -> pd.DataFrame:
    """
    Deserializes a Pandas DataFrame from `split-JSON` format.

    :param json_dataframe: Pandas DataFrame as JSON.
    :return: Deserialized Pandas DataFrame.
    """
    return pd.read_json(json_dataframe, orient='split')


def merge_predictions(data: pd.DataFrame, predictions: List[int]) -> pd.DataFrame:
    """
    Merge list of predictions with the given Pandas DataFrame by appending a new column `prediction`.

    :param data: Pandas DataFrame.
    :param predictions: List of predictions.
    :return: Merged DataFrame containing a `prediction` column.
    """
    data['prediction'] = predictions
    return data
