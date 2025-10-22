import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

from kio.pipeline_operations import OneHotEncodePd


@pytest.fixture
def ohe_df():
    """
    Fixture to create dummy data for testing OneHotEncodePd.

    :return: A simple DataFrame with sample categorical data.
    :rtype: pd.DataFrame
    """
    return pd.DataFrame({
        'category': ['A', 'B', 'A', 'C'],
        'value': [1, 2, 3, 4]
    })


def test_onehotencodepd_basic(ohe_df):
    ohe = OneHotEncodePd(target='category',
                         sep='_',
                         prefix='category',
                         required_columns=['category_A', 'category_B', 'category_C'])
    result = ohe.fit_transform(ohe_df)
    expected_columns = ['value', 'category_A', 'category_B', 'category_C']
    assert list(result.columns) == expected_columns
    assert result['category_A'].sum() == 2
    assert result['category_B'].sum() == 1
    assert result['category_C'].sum() == 1


def test_onehotencodepd_pipeline_compatibility(ohe_df):
    pipe = Pipeline([
        ('ohe', OneHotEncodePd(target='category',
                               sep='_',
                               prefix='category',
                               required_columns=['category_A', 'category_B', 'category_C']))
    ])
    result = pipe.fit_transform(ohe_df)
    expected_columns = ['value', 'category_A', 'category_B', 'category_C']
    assert list(result.columns) == expected_columns
    assert result['category_A'].sum() == 2
    assert result['category_B'].sum() == 1
    assert result['category_C'].sum() == 1


def test_onehotencodepd_required_columns_cat_not_in_df(ohe_df):
    ohe = OneHotEncodePd(target='category',
                         sep='_',
                         prefix='category',
                         required_columns=['category_A', 'category_B', 'category_C', 'category_D'])
    result = ohe.fit_transform(ohe_df)
    assert set(result.columns) == {'value', 'category_A', 'category_B', 'category_C', 'category_D'}
    assert result['category_A'].sum() == 2
    assert result['category_B'].sum() == 1
    assert result['category_C'].sum() == 1


def test_onehotendcodepd_missing_column(ohe_df):
    ohe = OneHotEncodePd(target='non_existent',
                         sep='_',
                         prefix='category',
                         required_columns=['category_A', 'category_B', 'category_C'])
    with pytest.raises(KeyError):
        ohe.fit_transform(ohe_df)


INVALID_ARGS = [
    123,
    None,
    True,
    [123, 321],
    [None, None],
    [True, False],
]


# noinspection PyTypeChecker
@pytest.mark.parametrize('arg', INVALID_ARGS)
def test_onehotencodepd_wrong_argument_type_target(arg):
    with pytest.raises(TypeError):
        OneHotEncodePd(target=arg,
                       sep='_',
                       prefix='category',
                       required_columns=['category_A', 'category_B', 'category_C'])


# noinspection PyTypeChecker
@pytest.mark.parametrize('arg', INVALID_ARGS)
def test_onehotencodepd_wrong_argument_type_sep(arg):
    with pytest.raises(TypeError):
        OneHotEncodePd(target='category',
                       sep=arg,
                       prefix='category',
                       required_columns=['category_A', 'category_B', 'category_C'])


# noinspection PyTypeChecker
@pytest.mark.parametrize('arg', INVALID_ARGS)
def test_onehotencodepd_wrong_argument_type_prefix(arg):
    with pytest.raises(TypeError):
        OneHotEncodePd(target='category',
                       sep='_',
                       prefix=arg,
                       required_columns=['category_A', 'category_B', 'category_C'])


# noinspection PyTypeChecker
@pytest.mark.parametrize('arg', INVALID_ARGS)
def test_onehotencodepd_wrong_argument_type_required_cols(arg):
    with pytest.raises(TypeError):
        OneHotEncodePd(target='category',
                       sep='_',
                       prefix='category',
                       required_columns=arg)
