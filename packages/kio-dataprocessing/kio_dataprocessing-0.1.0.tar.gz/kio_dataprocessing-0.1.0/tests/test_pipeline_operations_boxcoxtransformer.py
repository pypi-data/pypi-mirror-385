import pytest
import pandas as pd
import numpy as np

from scipy.stats import boxcox
from sklearn.pipeline import Pipeline

from itertools import product

from src.kio.pipeline_operations import BoxCoxTransformer


@pytest.fixture
def boxcox_df():
    df = pd.DataFrame({
        "A": [0.5, 1.0, 2.0, 4.0, 8.0, 16.0],
        "B": [0.33, 1.0, 3.0, 9.0, 27.0, 81.0]
    })
    return df


@pytest.fixture
def boxcox_lambda():
    return 1.5


@pytest.fixture
def boxcox_df_control(boxcox_df, boxcox_lambda):
    expected_res = boxcox_df.copy()
    expected_res_array = boxcox(x=boxcox_df['A'].to_numpy(), lmbda=boxcox_lambda)
    expected_res['A'] = pd.Series(expected_res_array)
    return expected_res


def test_boxcox_basic(boxcox_df,
                      boxcox_lambda,
                      boxcox_df_control):
    """
    Test basic functionality BoxCoxTransformer.
    """
    bc = BoxCoxTransformer(target='A',
                           lambda_val=boxcox_lambda)
    res = bc.fit_transform(boxcox_df)
    pd.testing.assert_frame_equal(res, boxcox_df_control)


def test_boxcox_pipeline_compatibility(boxcox_df,
                                       boxcox_lambda,
                                       boxcox_df_control):
    """
    Test functionality of BoxCoxTransformer within the pipeline construct.
    """
    pipe = Pipeline([(
        'bc', BoxCoxTransformer(target='A',
                                lambda_val=boxcox_lambda)
    )])
    res = pipe.fit_transform(boxcox_df)
    pd.testing.assert_frame_equal(res, boxcox_df_control)


def test_boxcox_missing_values(boxcox_lambda):
    """
    Test BoxCoxTransformer with incomplete data.
    """
    df = pd.DataFrame({
        "A": [np.nan, 1.0, 2.0, np.nan, 8.0, np.nan],
        "B": [0.33, 1.0, 3.0, 9.0, 27.0, 81.0]
    })
    with pytest.raises(ValueError):
        bc = BoxCoxTransformer(target='A',
                               lambda_val=boxcox_lambda)
        bc.fit_transform(df)


@pytest.mark.parametrize('df', [
    pd.DataFrame({
        "A": [0.0, 1.0, 2.0, 4.0, 8.0, 16.0],
        "B": [0.33, 1.0, 3.0, 9.0, 27.0, 81.0]
    }),
    pd.DataFrame({
        "A": [0.5, -1.0, 2.0, 4.0, 8.0, 16.0],
        "B": [0.33, 1.0, 3.0, 9.0, 27.0, 81.0]
    }),
    pd.DataFrame({
        "A": [0.0, 1.0, 2.0, -4.0, 8.0, 16.0],
        "B": [0.33, 1.0, 3.0, 9.0, 27.0, 81.0]
    }),
    pd.DataFrame({
        "A": [0.5, 1.0, 2.0, -4.0, 8.0, 0.0],
        "B": [0.33, 1.0, 3.0, 9.0, 27.0, 81.0]
    })
])
def test_boxcox_invalid_values(df, boxcox_lambda):
    """
    Test BoxCoxTransformer with data containing invalid values.
    """
    with pytest.raises(ValueError):
        bc = BoxCoxTransformer(target='A',
                               lambda_val=boxcox_lambda)
        bc.fit_transform(df)


def test_boxcox_mixed_datatypes(boxcox_lambda):
    """
    Test BoxCoxTransformer with data containing not exclusively floats.
    """
    df = pd.DataFrame({
        "A": [0.5, [1.0], '2.0', 4.0, True, None],
        "B": [0.33, 1.0, 3.0, 9.0, 27.0, 81.0]
    })
    with pytest.raises(ValueError):
        bc = BoxCoxTransformer(target='A',
                               lambda_val=boxcox_lambda)
        bc.fit_transform(df)


INVALID_ARGS = ['10', True, None, [1], {'mean': 1}]


@pytest.mark.parametrize('lambda_val, target', list(product(INVALID_ARGS, INVALID_ARGS)))
def test_boxcox_invalid_argument_types(boxcox_df,
                                       lambda_val,
                                       target):
    """
    Test StandardizeCols with incorrect arguments.
    """
    with pytest.raises(TypeError):
        bc = BoxCoxTransformer(target=target,
                               lambda_val=lambda_val)
        bc.fit_transform(boxcox_df)
