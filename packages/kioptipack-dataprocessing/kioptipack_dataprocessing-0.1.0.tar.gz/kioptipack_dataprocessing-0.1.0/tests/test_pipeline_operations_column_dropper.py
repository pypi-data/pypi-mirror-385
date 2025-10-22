import pytest
from sklearn.pipeline import Pipeline

from kio.pipeline_operations import ColumnDropper

VALID_ARGS_TARGET = [['a'],
                     ['b'],
                     ['c'],
                     ['a', 'b'],
                     ['a', 'c'],
                     ['b', 'c'],
                     ['c', 'a'],
                     ['a', 'b', 'c']]

INVALID_ARGS_TARGET = ['a',
                       'b',
                       'c',
                       123,
                       [123, 321],
                       True,
                       [True, False],
                       None,
                       [None]]


@pytest.mark.parametrize('target', VALID_ARGS_TARGET)
def test_column_dropper_basic(df, target):
    dropper = ColumnDropper(target=target)
    result = dropper.fit_transform(df)
    assert all(col not in result.columns for col in target)


@pytest.mark.parametrize('target', VALID_ARGS_TARGET)
def test_column_dropper_pipeline_compatibility(df, target):
    pipe = Pipeline([
        ('drop', ColumnDropper(target=target))
    ])
    result = pipe.fit_transform(df)
    assert all(col not in result.columns for col in target)


def test_column_dropper_no_columns(df):
    with pytest.raises(ValueError):
        ColumnDropper(target=[])


def test_column_dropper_no_columns_pipeline(df):
    with pytest.raises(ValueError):
        Pipeline([
            ('drop', ColumnDropper(target=[]))
        ])


def test_column_dropper_missing_column(df):
    dropper = ColumnDropper(target=['x'])  # 'x' doesn't exist
    with pytest.raises(KeyError):
        dropper.fit_transform(df)


# noinspection PyTypeChecker
@pytest.mark.parametrize('target', INVALID_ARGS_TARGET)
def test_column_dropper_wrong_argument_type(target):
    with pytest.raises(TypeError):
        ColumnDropper(target=target)
