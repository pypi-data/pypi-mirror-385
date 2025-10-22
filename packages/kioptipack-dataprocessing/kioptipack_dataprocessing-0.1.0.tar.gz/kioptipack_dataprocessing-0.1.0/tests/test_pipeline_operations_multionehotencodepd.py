import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

from kio.pipeline_operations import MultiOneHotEncodePd


@pytest.fixture
def mohe_df():
    """
    Fixture to create dummy data for testing MultiOneHotEncodePd.

    :return: A simple DataFrame with sample categorical data.
    :rtype: pd.DataFrame
    """
    return pd.DataFrame({
        'Komponente': [['A', 'B'],
                       ['B', 'C'],
                       ['A', 'C'],
                       ['A', 'B']],
        'category2': ['X', 'Y', 'X', 'Z'],
        'value': [1, 2, 3, 4]
    })


def test_multi_onehotencodepd_basic(mohe_df):
    mohe = MultiOneHotEncodePd(target='Komponente',
                               sep='_',
                               prefix='Komponente',
                               required_columns=['Komponente_A', 'Komponente_B', 'Komponente_C'])
    result = mohe.fit_transform(mohe_df)
    expected_columns = ['category2', 'value', 'Komponente_A', 'Komponente_B', 'Komponente_C']
    assert list(result.columns) == expected_columns
    assert result['Komponente_A'].sum() == 3
    assert result['Komponente_B'].sum() == 3
    assert result['Komponente_C'].sum() == 2


def test_multi_onehotencodepd_pipeline_compatibility(mohe_df):
    pipe = Pipeline([
        ('mohe', MultiOneHotEncodePd(target='Komponente',
                                     sep='_',
                                     prefix='Komponente',
                                     required_columns=['Komponente_A', 'Komponente_B', 'Komponente_C']))
    ])
    result = pipe.fit_transform(mohe_df)
    expected_columns = ['category2', 'value', 'Komponente_A', 'Komponente_B', 'Komponente_C']
    assert list(result.columns) == expected_columns
    assert result['Komponente_A'].sum() == 3
    assert result['Komponente_B'].sum() == 3
    assert result['Komponente_C'].sum() == 2
