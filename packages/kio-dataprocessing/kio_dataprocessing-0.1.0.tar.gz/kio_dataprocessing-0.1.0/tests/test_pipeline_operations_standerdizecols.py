import pytest
import pandas as pd
import numpy as np

from sklearn.pipeline import Pipeline

from itertools import product

from kio.pipeline_operations import StandardizeCols


@pytest.fixture
def standardize_cols_df():
    df = pd.DataFrame(
        data={
            "A": [10, 12, 14, 16, 18],
            "B": [100, 110, 90, 120, 130]},
        dtype='float64'
    )
    return df


@pytest.fixture
def standardize_cols_df_mean(standardize_cols_df):
    return standardize_cols_df.mean()


@pytest.fixture
def standardize_cols_df_std(standardize_cols_df):
    return standardize_cols_df.std(ddof=0)


def test_standardize_cols_basic(standardize_cols_df,
                                standardize_cols_df_std,
                                standardize_cols_df_mean):
    """
    Test basic functionality StandardizeCols.
    """
    std_cols = StandardizeCols(target="A",
                               mean=standardize_cols_df_mean['A'],
                               std=standardize_cols_df_std['A'])
    result = std_cols.fit_transform(standardize_cols_df)
    standardize_cols_df['A'] = (standardize_cols_df['A'] - standardize_cols_df_mean['A']) / standardize_cols_df_std['A']
    pd.testing.assert_frame_equal(result, standardize_cols_df)


def test_standardize_cols_pipeline_compatibility(standardize_cols_df,
                                                 standardize_cols_df_std,
                                                 standardize_cols_df_mean):
    """
    Test functionality of StandardizeCols within the pipeline construct.
    """
    pipe = Pipeline([(
        'std_col', StandardizeCols(target="A",
                                   mean=standardize_cols_df_mean['A'],
                                   std=standardize_cols_df_std['A'])
    )])
    result = pipe.fit_transform(standardize_cols_df)
    standardize_cols_df['A'] = (standardize_cols_df['A'] - standardize_cols_df_mean['A']) / standardize_cols_df_std['A']
    pd.testing.assert_frame_equal(result, standardize_cols_df)


def test_standardize_cols_missing_values(standardize_cols_df_mean,
                                         standardize_cols_df_std):
    """
    Test StandardizeCols with incomplete data.
    """
    df = pd.DataFrame(
        data={
            "A": [10, np.nan, 14, 16, np.nan],
            "B": [100, 110, 90, 120, 130]},
        dtype='float64'
    )
    std_col = StandardizeCols(target="A",
                              mean=standardize_cols_df_mean['A'],
                              std=standardize_cols_df_std['A'])
    with pytest.raises(ValueError):
        std_col.fit_transform(df)


def test_standardize_cols_mixed_datatypes(standardize_cols_df_mean,
                                          standardize_cols_df_std):
    """
    Test StandardizeCols with mixed data.
    """
    df = pd.DataFrame(
        data={
            "A": ["10", 12, True, 16, None],
            "B": [100, 110, 90, 120, 130]}
    )
    std_col = StandardizeCols(target="A",
                              mean=standardize_cols_df_mean['A'],
                              std=standardize_cols_df_std['A'])
    with pytest.raises(ValueError):
        std_col.fit_transform(df)


INVALID_ARGS = ['10', True, None, [1], {'mean': 1}]


@pytest.mark.parametrize("mean, std, target", list(product(INVALID_ARGS, INVALID_ARGS, INVALID_ARGS)))
def test_standardize_cols_incorrect_arguments(standardize_cols_df,
                                              target,
                                              mean,
                                              std):
    """
    Test StandardizeCols with incorrect arguments.
    """
    with pytest.raises(TypeError):
        StandardizeCols(target=target, mean=mean, std=std)
