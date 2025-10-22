import pandas as pd
import numpy as np
import pytest

from sklearn.pipeline import Pipeline

from kio.pipeline_operations import NumericOneHotEncodePd


@pytest.fixture
def nohe_df():
    """
    Fixture to create dummy data for testing MultiOneHotEncodePd.

    :return: A simple DataFrame with sample categorical data.
    :rtype: pd.DataFrame
    """
    return pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [["K5"], ["K6"], ["K5"], ["K5", "K7"], ["K4", "K6", "K8"]],
        'C': [[1.0], [1.0], [1.0], [0.25, 0.75], [0.2, 0.2, 0.6]],
        'D': ["just", "some", "cool", "strings", "here"]
    })


def test_numeric_onehotencodedpd_basic(nohe_df):
    nohe = NumericOneHotEncodePd(targets=['B', 'C'],
                                 sep='_',
                                 prefix='Weight',
                                 required_columns=['Weight_K4',
                                                   'Weight_K5',
                                                   'Weight_K6',
                                                   'Weight_K7',
                                                   'Weight_K8'])
    result = nohe.fit_transform(nohe_df)

    expected_df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'D': ["just", "some", "cool", "strings", "here"],
        'Weight_K4': [0.0, 0.0, 0.0, 0.0, 0.2],
        'Weight_K5': [1.0, 0.0, 1.0, 0.25, 0.0],
        'Weight_K6': [0.0, 1.0, 0.0, 0.0, 0.2],
        'Weight_K7': [0.0, 0.0, 0.0, 0.75, 0.0],
        'Weight_K8': [0.0, 0.0, 0.0, 0.0, 0.6],
    })
    expected_df[["Weight_K4", "Weight_K5", "Weight_K6", "Weight_K7", "Weight_K8"]] = expected_df[
        ["Weight_K4", "Weight_K5", "Weight_K6", "Weight_K7", "Weight_K8"]].astype(float)
    pd.testing.assert_frame_equal(result, expected_df, check_like=True)


@pytest.mark.parametrize('df', [
    pd.DataFrame({
        'A': [1, np.nan, 3, 4, 5],
        'B': [["K1"], [], np.nan, ["K2", "K3"], ["K4"]],
        'C': [[1.0], [], np.nan, [0.5, 0.5], [1.0]],
        'D': ["text", "", np.nan, "string", "end"]
    }),
    pd.DataFrame({
        'A': [1, 2, 3],
        'B': [["K1", "K2"], ["K3"], ["K4", np.nan]],
        'C': [[0.4, 0.6], [1.0], [0.5, np.nan]],
        'D': ["has_nan", "clean", "list_nan"]
    })
])
def test_numeric_onehotencodedpd_mixed_nans(df):
    with pytest.raises(TypeError):
        nohe = NumericOneHotEncodePd(targets=['B', 'C'],
                                     sep='_',
                                     prefix='Weight',
                                     required_columns=['Weight_K1',
                                                       'Weight_K2',
                                                       'Weight_K3',
                                                       'Weight_K4'])
        result = nohe.fit_transform(df)


@pytest.mark.parametrize('df', [
    pd.DataFrame({
        'A': pd.Series(dtype='int'),
        'B': pd.Series(dtype='object'),
        'C': pd.Series(dtype='object'),
        'D': pd.Series(dtype='str')
    }),
    pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [np.nan] * 5,
        'C': [np.nan] * 5,
        'D': ["just", "some", "cool", "strings", "here"]
    }),
    pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [np.nan] * 5,
        'C': [[1.0], [1.0], [1.0], [0.25, 0.75], [0.2, 0.2, 0.6]],
        'D': ["just", "some", "cool", "strings", "here"]
    }),
    pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [["K5"], ["K6"], ["K5"], ["K5", "K7"], ["K4", "K6", "K8"]],
        'C': [np.nan] * 5,
        'D': ["just", "some", "cool", "strings", "here"]
    }),
])
def test_numeric_onehotencodedpd_empty_df(df):
    with pytest.raises(ValueError):
        nohe = NumericOneHotEncodePd(targets=['B', 'C'],
                                     sep='_',
                                     prefix='Weight',
                                     required_columns=['Weight_K1',
                                                       'Weight_K2',
                                                       'Weight_K3',
                                                       'Weight_K4'])
        result = nohe.fit_transform(df)


@pytest.fixture
def df_len_diff():
    """
    Fixture to create dummy data for testing MultiOneHotEncodePd.

    :return: A simple DataFrame with sample categorical data.
    :rtype: pd.DataFrame
    """
    return pd.DataFrame({
        'A': [1, 2, 3],
        'B': [["K1", "K2"], ["K3"], ["K4", "K5", "K6"]],
        'C': [[0.3, 0.3], [1.0], [0.5, 0.5]],  # Doesn't match list length of B for row 3
        'D': ["case1", "case2", "case3"]
    })


def test_numeric_onehotencodedpd_len_diff(df_len_diff):
    with pytest.raises(ValueError):
        nohe = NumericOneHotEncodePd(targets=['B', 'C'],
                                     sep='_',
                                     prefix='Weight',
                                     required_columns=['Weight_K1',
                                                       'Weight_K2',
                                                       'Weight_K3',
                                                       'Weight_K4'])
        result = nohe.fit_transform(df_len_diff)


@pytest.fixture
def df_mixed_list_types():
    """
    Fixture to create dummy data for testing MultiOneHotEncodePd.

    :return: A simple DataFrame with sample categorical data.
    :rtype: pd.DataFrame
    """
    return pd.DataFrame({
        'A': [1, 2, 3],
        'B': [["K1", 5], [None], ["K2"]],
        'C': [[0.5, "bad"], [np.nan], [1.0]],
        'D': ["mixed", "null", "valid"]
    })


def test_numeric_onehotencodedpd_mixed_list_types(df_mixed_list_types):
    with pytest.raises(TypeError):
        nohe = NumericOneHotEncodePd(targets=['B', 'C'],
                                     sep='_',
                                     prefix='Weight',
                                     required_columns=['Weight_K1',
                                                       'Weight_K2',
                                                       'Weight_K3',
                                                       'Weight_K4'])
        result = nohe.fit_transform(df_mixed_list_types)


@pytest.fixture
def df_prob_sum_error():
    """
    Fixture to create dummy data for testing MultiOneHotEncodePd.

    :return: A simple DataFrame with sample categorical data.
    :rtype: pd.DataFrame
    """
    return pd.DataFrame({
        'A': [1, 2],
        'B': [["Z1", "Z2"], ["Z3", "Z4"]],
        'C': [[0.4, 0.3], [0.5, 0.6]],  # sums are 0.7 and 1.1
        'D': ["not1", "too much"]
    })


def test_numeric_onehotencodedpd_sum_error(df_prob_sum_error):
    with pytest.raises(ValueError):
        nohe = NumericOneHotEncodePd(targets=['B', 'C'],
                                     sep='_',
                                     prefix='Weight',
                                     required_columns=['Weight_K1',
                                                       'Weight_K2',
                                                       'Weight_K3',
                                                       'Weight_K4'])
        result = nohe.fit_transform(df_prob_sum_error)


def test_numeric_onehotencodedpd_pipeline_compatibility(nohe_df):
    pipe = Pipeline([
        ('ohe', NumericOneHotEncodePd(targets=['B', 'C'],
                                      sep='_',
                                      prefix='Weight',
                                      required_columns=['Weight_K4',
                                                        'Weight_K5',
                                                        'Weight_K6',
                                                        'Weight_K7',
                                                        'Weight_K8']))
    ])
    result = pipe.fit_transform(nohe_df)

    expected_df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'D': ["just", "some", "cool", "strings", "here"],
        'Weight_K4': [0.0, 0.0, 0.0, 0.0, 0.2],
        'Weight_K5': [1.0, 0.0, 1.0, 0.25, 0.0],
        'Weight_K6': [0.0, 1.0, 0.0, 0.0, 0.2],
        'Weight_K7': [0.0, 0.0, 0.0, 0.75, 0.0],
        'Weight_K8': [0.0, 0.0, 0.0, 0.0, 0.6],
    })
    expected_df[["Weight_K4", "Weight_K5", "Weight_K6", "Weight_K7", "Weight_K8"]] = expected_df[
        ["Weight_K4", "Weight_K5", "Weight_K6", "Weight_K7", "Weight_K8"]].astype(float)
    pd.testing.assert_frame_equal(result, expected_df, check_like=True)


def test_numeric_onhotencodedpd_openhubdf(openhub_df):
    nohe = NumericOneHotEncodePd(
        targets=["ListeKomponenten", "Massenanteile"],
        sep="_",
        prefix="Weight",
        required_columns=[
            "Weight_K000055",
            "Weight_K000057"
        ]
    )
    df_copy = openhub_df.copy()
    result = nohe.fit_transform(openhub_df)
    encoded_weights = {
        "Weight_K000055": [1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
        "Weight_K000057": [0.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
    }
    encoded_weights_df = pd.DataFrame(encoded_weights)
    dropped_df = df_copy.drop(columns=["ListeKomponenten", "Massenanteile"])
    expected_result = pd.concat([dropped_df, encoded_weights_df], axis=1)
    pd.testing.assert_frame_equal(result, expected_result, check_like=True)
