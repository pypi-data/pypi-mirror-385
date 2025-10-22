import numpy as np
import pytest
from sklearn.pipeline import Pipeline
from itertools import product

from kio.pipeline_operations import ColumnTypeSetter

VALID_ARGS_TARGET = [['a'],
                     ['b'],
                     ['c'],
                     ['a', 'b'],
                     ['a', 'c'],
                     ['b', 'c'],
                     ['c', 'a'],
                     ['a', 'b', 'c'],]
VALID_ARGS_DTYPE = ['int16',
                    'int32',
                    'int64',
                    'float32',
                    'float64']

INVALID_ARGS_TARGET = ['a',
                       'b',
                       'c',
                       123,
                       [123, 321],
                       True,
                       [True, False],
                       None,
                       [None]]

INVALID_ARGS_DTYPE = [np.int8,
                      np.float16,
                      int,
                      float,
                      1,
                      1.0]


@pytest.mark.parametrize("target,dtype", list(product(VALID_ARGS_TARGET, VALID_ARGS_DTYPE)))
def test_column_typesetter_basic(df, target, dtype):
    typesetter = ColumnTypeSetter(target=target, dtype=dtype)
    result = typesetter.fit_transform(df)
    for tar in target:
        assert result[tar].dtype == np.dtype(dtype)


@pytest.mark.parametrize("target,dtype", list(product(VALID_ARGS_TARGET, VALID_ARGS_DTYPE)))
def test_column_typesetter_pipeline_compatibility(df, target, dtype):
    pipe = Pipeline([
        ('set_type', ColumnTypeSetter(target=target, dtype=dtype))
    ])
    result = pipe.fit_transform(df)
    for tar in target:
        assert result[tar].dtype == np.dtype(dtype)


@pytest.mark.parametrize("dtype", VALID_ARGS_DTYPE)
def test_column_typesetter_no_columns(df, dtype):
    with pytest.raises(ValueError):
        ColumnTypeSetter(target=[], dtype='int16')


@pytest.mark.parametrize("dtype", VALID_ARGS_DTYPE)
def test_column_typesetter_no_columns_pipeline(df, dtype):
    with pytest.raises(ValueError):
        Pipeline([
            ('set_type', ColumnTypeSetter(target=[], dtype=dtype))
        ])


@pytest.mark.parametrize("dtype", VALID_ARGS_DTYPE)
def test_column_typesetter_missing_column(df, dtype):
    typesetter = ColumnTypeSetter(target=['x'], dtype=dtype)  # 'x' doesn't exist
    with pytest.raises(KeyError):
        typesetter.fit_transform(df)


# noinspection PyTypeChecker
@pytest.mark.parametrize("target,dtype", list(product(INVALID_ARGS_TARGET, INVALID_ARGS_DTYPE)))
def test_column_typesetter_wrong_argument_type(target, dtype):
    with pytest.raises(TypeError):
        ColumnTypeSetter(target=target, dtype=dtype)
