import math

import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin


class ColumnDropper(BaseEstimator, TransformerMixin):
    """
    Drop the specified columns from the DataFrame.

    :param target: List of columns to drop
    :type target: list

    """

    def __init__(self, target: list[str]):
        """ Initialize the ColumnDropper object."""
        if not isinstance(target, list) or not all(isinstance(item, str) for item in target):
            raise TypeError("Target should be a list of strings.")
        if not target:
            raise ValueError("Target should not be empty.")
        self.target = target

    def fit(self, target):
        """ Return self."""
        return self

    def transform(self, x: pd.DataFrame) -> pd.DataFrame:
        """
        Drop the specified columns from the DataFrame.

        :param x: The Dataframe to transform
        :type x: pd.DataFrame

        :return: The transformed Dataframe
        :rtype: pd.DataFrame

        """
        if not all(col in x.columns for col in self.target):
            raise KeyError("Target is not contained in the DataFrame.")
        return x.drop(self.target, axis=1)


class ColumnTypeSetter(BaseEstimator, TransformerMixin):
    """
    Set the specified columns to type float in the DataFrame.

    :param target: List of columns to set
    :type target: list

    :param dtype: The datatype the target is to be transformed to
    :type dtype: str

    """

    def __init__(self, target: list[str], dtype: str):
        """ Initialize the ColumnTypeSetter object."""
        self.available_dtype = ['int16', 'int32', 'int64', 'float32', 'float64']
        if not isinstance(target, list) or not all(isinstance(item, str) for item in target):
            raise TypeError("Target should be a list of strings.")
        if not target:
            raise ValueError("Target should not be empty.")
        if not isinstance(dtype, str):
            raise TypeError("dtype should be a string.")
        if dtype not in self.available_dtype:
            raise ValueError(f"dtype should be one of {self.available_dtype}.")
        self.target = target
        self.dtype = dtype

    def fit(self, target):
        """ Return self."""
        return self

    def transform(self, x: pd.DataFrame) -> pd.DataFrame:
        """
        Set the specified columns to type float in the DataFrame.

        :param x: The Dataframe to transform
        :type x: pd.DataFrame

        :return: The transformed Dataframe
        :rtype: pd.DataFrame

        """
        if not all(col in x.columns for col in self.target):
            raise KeyError("Target is not contained in the DataFrame.")
        x[self.target] = x[self.target].astype(dtype=self.dtype)
        return x


class OneHotEncodePd(BaseEstimator, TransformerMixin):
    """
    One-hot encode the specified column.


    :param target: The column to one-hot encode.
    :type target: str

    :param prefix: The prefix to use for the one-hot encoded columns.
    :type prefix: str

    :param sep: The separator to use for the one-hot encoded columns.
    :type sep: str

    :param required_columns: A list of columns that should be present in the DataFrame after one-hot encoding.
    :type required_columns: list

    """

    def __init__(self, target: str, prefix: str, sep: str, required_columns: list[str]):
        """
        Initialize the OneHotEncodePd object.

        """
        if not isinstance(target, str):
            raise TypeError("Target should be a string.")
        if not isinstance(prefix, str):
            raise TypeError("Prefix should be a string.")
        if not isinstance(sep, str):
            raise TypeError("Separator should be a string.")
        if not isinstance(required_columns, list) or not all(isinstance(item, str) for item in required_columns):
            raise TypeError("Required columns should be a list of strings")

        self.target = target
        self.prefix = prefix
        self.sep = sep
        self.required_columns = required_columns

    def fit(self, target):
        """
        Return self.
        """
        return self

    def transform(self, x: pd.DataFrame) -> pd.DataFrame:
        """
        One-hot encode the specified column.

        :param x: The Dataframe to transform
        :type x: pd.DataFrame

        :return: The transformed Dataframe
        :rtype: pd.DataFrame

        """
        if self.target not in x.columns:
            raise KeyError("Target is not contained in the DataFrame.")

        # Perform in-place one-hot encoding
        df_encoded = pd.get_dummies(x, columns=[self.target], prefix=self.prefix,
                                    prefix_sep=self.sep, dtype=float)

        # Replace the original 'Category' column with the one-hot encoded columns
        x[df_encoded.columns] = df_encoded

        # Drop the original 'Category' column
        x.drop(columns=[self.target], inplace=True)

        # Ensure all required columns are present, adding them with 0s if necessary
        for column in self.required_columns:
            if column not in x.columns:
                x[column] = 0.0

        return x


class MultiOneHotEncodePd(BaseEstimator, TransformerMixin):
    """
    One-hot encode the specified column into multiple categorical values.

    :param target: The column to one-hot encode.
    :type target: str

    :param prefix: The prefix to use for the one-hot encoded columns.
    :type prefix: str

    :param sep: The separator to use for the one-hot encoded columns.
    :type sep: str

    :param required_columns: A list of columns that should be present in the DataFrame after one-hot encoding.
    :type required_columns: list

    """

    def __init__(self, target: str, prefix: str, sep: str, required_columns: list[str]):
        """
        Initialize the MultiOneHotEncodePd object.

        """
        if not isinstance(target, str):
            raise TypeError("Target should be a string.")
        if not isinstance(prefix, str):
            raise TypeError("Prefix should be a string.")
        if not isinstance(sep, str):
            raise TypeError("Separator should be a string.")
        if not isinstance(required_columns, list) or not all(isinstance(item, str) for item in required_columns):
            raise TypeError("Required columns should be a list of strings")
        self.target = target
        self.prefix = prefix
        self.sep = sep
        self.required_columns = required_columns

    def fit(self, target):
        """ Return self."""
        return self

    def transform(self, x: pd.DataFrame) -> pd.DataFrame:
        """
        One-hot encode the specified column containing lists of categorical values.

        :param x: The Dataframe to transform
        :type x: pd.DataFrame

        :return: The transformed Dataframe
        :rtype: pd.DataFrame

        """
        # Initialize the one-hot encoded columns with 0s
        for column in self.required_columns:
            x[column] = 0.0

        # Iterate over each row and set the corresponding one-hot encoded columns to 1
        for index, row in x.iterrows():
            for value in row[self.target]:
                column_name = f"{self.prefix}{self.sep}{value}"
                if column_name in x.columns:
                    x.at[index, column_name] = 1.0

        # Drop the original target column
        x.drop(columns=[self.target], inplace=True)

        return x


class NormalizeCols(BaseEstimator, TransformerMixin):
    """
    Normalize the specified column to the specified feature range using provided column range.

    :param target: The column to normalize.
    :type target: str

    :param feature_range: The desired range of the transformed data.
    :type feature_range: tuple

    :param column_range: The actual range of the column data.
    :type column_range: tuple

    """

    def __init__(self,
                 column_range: tuple[float, float],
                 target: str,
                 feature_range: tuple[float, float] = (-1.0, 1.0)):
        """
        Initialize the CustomNormalizeCols object.

        """
        self.target = target
        self.feature_range = feature_range
        self.column_range = column_range

    def fit(self, target):
        """ Return self."""
        return self

    def transform(self, x: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize the specified column to the specified feature range using provided column range.

        :param x: The Dataframe to transform
        :type x: pd.DataFrame

        :return: The transformed Dataframe
        :rtype: pd.DataFrame

        """
        df = x.copy()  # don't modify original df
        col_min, col_max = self.column_range
        feature_min, feature_max = self.feature_range

        df[self.target] = df[self.target].apply(
            lambda x: feature_min + (x - col_min) * (feature_max - feature_min) / (col_max - col_min)
            if not pd.isna(x) else pd.NA
        )
        return df


class StandardizeCols(BaseEstimator, TransformerMixin):
    """
    A simple Standardscaler.
    :param target: The target column of the transformation
    :type target: str

    :param mean: The mean of the column data.
    :type mean: float

    :param std: The standard deviation of the column data.
    :type std: float
    """

    def __init__(self, target: str, mean: float, std: float):
        if not isinstance(target, str):
            raise TypeError("Target is supposed to be a string.")
        self.target = target

        if not isinstance(mean, float):
            raise TypeError("Mean is supposed to be a float.")
        self.mean = mean

        if not isinstance(std, float):
            raise TypeError("Standard Deviation is supposed to be a float.")
        self.std = std

    def fit(self, target):
        return self

    def transform(self, x: pd.DataFrame) -> pd.DataFrame:
        df = x.copy()

        if df[self.target].isna().any() or not pd.api.types.is_float_dtype(df[self.target]):
            raise ValueError("The target column contains missing values.")

        df[self.target] = df[self.target].apply(
            lambda x: (x - self.mean) / self.std
            if not pd.isna(x) else pd.NA
        )
        return df


class BoxCoxTransformer(BaseEstimator, TransformerMixin):
    """
    A simple box-cox transformer.
    :param target: The target column of the transformation
    :type target: str

    :param lambda_val: The lambda value for the box-cox transformer.
    :type lambda_val: float
    """

    def __init__(self, target: str, lambda_val: float):
        if not isinstance(target, str):
            raise TypeError("Target is supposed to be a string.")
        self.target = target

        if not isinstance(lambda_val, float):
            raise TypeError("Lambda value is supposed to be a float")
        self.lambda_val = lambda_val

    def fit(self, target):
        return self

    def transform(self, x: pd.DataFrame) -> pd.DataFrame:
        df = x.copy()
        if not pd.api.types.is_float_dtype(df[self.target]):
            raise ValueError(f"The values of {self.target} must float")
        if (df[self.target] <= 0).any():
            raise ValueError(f"All values in column '{self.target}' must be positive for Box-Cox transformation.")
        if df[self.target].isna().any():
            raise ValueError(f"The target column {self.target} contains missing values.")

        if self.lambda_val == 0.0:
            df[self.target] = df[self.target].apply(math.log)
        else:
            df[self.target] = df[self.target].apply(lambda x: (x ** self.lambda_val - 1) / self.lambda_val)

        return df


class NumericOneHotEncodePd(BaseEstimator, TransformerMixin):
    """
    Numeric-hot encode the specified column into multiple categorical values.

    :param targets: The labels of the column containing the labels and the column containing the numeric values.
    :type targets: list[str]

    :param prefix: The prefix to use for the one-hot encoded columns.
    :type prefix: str

    :param sep: The separator to use for the one-hot encoded columns.
    :type sep: str

    :param required_columns: A list of columns that should be present in the DataFrame after one-hot encoding.
    :type required_columns: list

    """

    def __init__(self, targets: list[str], prefix: str, sep: str, required_columns: list[str]):
        """
        Initialize the NumericOneHotEncodePd object.

        """
        if not (
                isinstance(targets, list)
                and len(targets) == 2
                and all(isinstance(item, str) for item in targets)
        ):
            raise TypeError("Targets should be a list of strings")
        if not isinstance(prefix, str):
            raise TypeError("Prefix should be a string.")
        if not isinstance(sep, str):
            raise TypeError("Separator should be a string.")
        if not isinstance(required_columns, list) or not all(isinstance(item, str) for item in required_columns):
            raise TypeError("Required columns should be a list of strings")
        self.targets = targets
        self.prefix = prefix
        self.sep = sep
        self.required_columns = required_columns

    def fit(self, target):
        """ Return self."""
        return self

    def transform(self, x: pd.DataFrame) -> pd.DataFrame:
        """
        Numeric-hot encode the specified columns containing lists of categorical values with numeric values.

        :param x: The Dataframe to transform
        :type x: pd.DataFrame

        :return: The transformed Dataframe
        :rtype: pd.DataFrame

        """
        if x.empty:
            raise ValueError("Dataframe is empty.")
        for target in self.targets:
            if x[target].isna().all():
                raise ValueError(f"{target} is empty.")
        encoded_rows = []

        for _, row in x.iterrows():
            labels = row[self.targets[0]]
            numeric_vals = row[self.targets[1]]
            if not (
                    isinstance(labels, list)
                    and all(isinstance(label, str) for label in labels)
                    and len(labels) > 0
            ):
                raise TypeError("Labels should be a list of strings with at least one entry.")

            if not isinstance(numeric_vals, (list, type(None))):
                raise TypeError("Numeric values should be a list of floats or None.")

            if isinstance(numeric_vals, list):
                if not (
                        all(isinstance(val, float) for val in numeric_vals)
                        and len(numeric_vals) > 0
                ):
                    raise TypeError("Numeric values should be a list of floats with at least one entry or None.")
                if not (
                        len(labels) == len(numeric_vals)
                ):
                    raise ValueError("Label and numeric lists should be the same length")

            if isinstance(numeric_vals, type(None)):
                numeric_vals = [1]

            if not sum(numeric_vals) == 1:
                raise ValueError("Numeric values sum should always be 1")

            encoded = {f"{self.prefix}{self.sep}{label}": float(numeric_val) for label, numeric_val in
                       zip(labels, numeric_vals)}

            encoded_rows.append(encoded)

        encoded_df = pd.DataFrame(encoded_rows).fillna(0)

        x.drop(columns=self.targets, inplace=True)

        result = pd.concat([x, encoded_df], axis=1)

        return result


class FindReplace(BaseEstimator, TransformerMixin):
    def __init__(self, targets: list[str], comp_op: str, comp_val: tuple, other):
        self.target_dtype = None
        self.targets = targets
        if not (
                isinstance(targets, list)
                and all(isinstance(item, str) for item in targets)
        ):
            raise TypeError("Targets should be a list of strings")

        self.ops = {
            "<": lambda s: s < self.comp_val[0],
            ">": lambda s: s > self.comp_val[0],
            "=": lambda s: s == self.comp_val[0],
            "<=": lambda s: s <= self.comp_val[0],
            ">=": lambda s: s >= self.comp_val[0],
            "isna": lambda s: s.isna(),
            "intervalcomp": lambda s: (s >= self.comp_val[0]) & (s <= self.comp_val[1])
        }

        self.comp_op = comp_op
        if not (
                isinstance(comp_op, str)
                and self.comp_op in self.ops.keys()
        ):
            raise ValueError("Cond should be a string and either '<' or '>' or '=' or '<=' or '>='")

        self.comp_val = comp_val
        self.other = other

    def fit(self, target):
        return self

    def transform(self, x):
        df = x.copy()
        for target in self.targets:
            self.target_dtype = df[target].dtype
            if self.other == "mean":
                other = df[target].mean()
            else:
                other = self.other

            df[target] = df[target].mask(self.ops[self.comp_op](df[target]), other)
            df[target] = df[target].astype(self.target_dtype)
        return df
