import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

from kio.pipeline_operations import NormalizeCols

@pytest.fixture
def normalize_df():
    """
    Fixture to create dummy data for testing NormalizeCols.

    :return: A simple DataFrame with sample numerical data.
    :rtype: pd.DataFrame
    """
    return pd.DataFrame({
        'a': [1, 2, 3],
        'b': [4, 5, 6],
        'c': [7, 8, 9]
    })

def test_normalizecols_basic(normalize_df):
    normalize = NormalizeCols(target='a', feature_range=(0, 1), column_range=(1, 3))
    result = normalize.fit_transform(normalize_df)
    expected = pd.DataFrame({
        'a': [0.0, 0.5, 1.0],
        'b': [4, 5, 6],
        'c': [7, 8, 9]
    })
    pd.testing.assert_frame_equal(result, expected)

def test_normalizecols_pipeline_compatibility(normalize_df):
    pipe = Pipeline(
        steps=[('normalize1', NormalizeCols(target='a', feature_range=(0, 1), column_range=(0, 10))),
               ('normalize2', NormalizeCols(target='b', feature_range=(0, 1), column_range=(0, 10))),
               ('normalize3', NormalizeCols(target='c', feature_range=(0, 1), column_range=(0, 10)))]
    )
    result = pipe.fit_transform(normalize_df)
    expected = pd.DataFrame({
        'a': [0.1, 0.2, 0.3],
        'b': [0.4, 0.5, 0.6],
        'c': [0.7, 0.8, 0.9]
    })
    pd.testing.assert_frame_equal(result, expected)