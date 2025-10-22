import pytest
import pandas as pd

from kio.pipeline_operations import FindReplace


@pytest.fixture
def findreplace_df():
    df = pd.DataFrame(
        data={
            "A": [10, 20, 30, 40, 50],
            "B": [100, 90, 80, 70, 60],
            "C": ["alpha", "beta", "gamma", "delta", "epsilon"],
            "D": ["a", "b", "c", "d", "e"],
            "E": [1.0, 2.0, pd.NA, 4.0, pd.NA],
            "F": [pd.NA, 9.0, pd.NA, pd.NA, 6.0],
        }
    )

    df['A'] = df['A'].astype('Int64')
    df['B'] = df['B'].astype('Int64')
    df['C'] = df['C'].astype('str')
    df['D'] = df['D'].astype('str')
    df['E'] = df['E'].astype('Float64')
    df['F'] = df['F'].astype('Float64')
    return df


def test_findreplace_basic_num(findreplace_df):
    fr = FindReplace(targets=['A', 'B'],
                     comp_op=">",
                     comp_val=(50,),
                     other=50)
    result = fr.fit_transform(findreplace_df)
    findreplace_df['B'] = [50, 50, 50, 50, 50]
    findreplace_df['B'] = findreplace_df['B'].astype('Int64')
    print(findreplace_df)
    print(result)
    pd.testing.assert_frame_equal(result, findreplace_df)


def test_findreplace_basic_mean(findreplace_df):
    fr = FindReplace(targets=['E', 'F'],
                     comp_op="isna",
                     comp_val=(pd.NA,),
                     other='mean')
    result = fr.fit_transform(findreplace_df)
    findreplace_df['E'] = [1.0, 2.0, 2.333333, 4.0, 2.333333]
    findreplace_df['F'] = [7.5, 9.0, 7.5, 7.5, 6.0]
    findreplace_df['E'] = findreplace_df['E'].astype('Float64')
    findreplace_df['F'] = findreplace_df['F'].astype('Float64')
    print(findreplace_df)
    print(result)
    pd.testing.assert_frame_equal(result, findreplace_df)


def test_findreplace_basic_str(findreplace_df):
    fr = FindReplace(targets=['C', 'D'],
                     comp_op="=",
                     comp_val=("beta",),
                     other="sigma")
    result = fr.fit_transform(findreplace_df)
    findreplace_df['C'] = ['alpha', 'sigma', 'gamma', 'delta', 'epsilon']
    print(findreplace_df)
    print(result)
    pd.testing.assert_frame_equal(result, findreplace_df)


def test_findreplace_basic_interval(findreplace_df):
    fr = FindReplace(targets=['A', 'B'],
                     comp_op="intervalcomp",
                     comp_val=(30, 60),
                     other=50)
    result = fr.fit_transform(findreplace_df)
    findreplace_df['A'] = [10, 20, 50, 50, 50]
    findreplace_df['B'] = [100, 90, 80, 70, 50]
    findreplace_df['A'] = findreplace_df['A'].astype('Int64')
    findreplace_df['B'] = findreplace_df['B'].astype('Int64')
    print(findreplace_df)
    print(result)
    pd.testing.assert_frame_equal(result, findreplace_df)
