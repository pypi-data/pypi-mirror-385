"""A Cleaning DF class that streamlines common cleaning operations on dataframes.

This is usefull to build Pipelines and when extending the class you can add your own
cleaning operations.
This module uses polars for dataframe operations and assumes some standards on the data
"""

from abc import abstractmethod
from collections.abc import Callable
from typing import Any

import polars as pl
from polars.datatypes.classes import FloatType

from winipedia_utils.data.structures.dicts import reverse_dict
from winipedia_utils.oop.mixins.mixin import ABCLoggingMixin


class CleaningDF(ABCLoggingMixin):
    """Inherits from polars.DataFrame and ABCLoggingMixin.

    This will be a base class for importing all kinds of Data to e.g. a database.
    It will be used to import data from different sources an clean it
    Bring the data into the correct format and name the columns correctly.
    And the df takes over and does the rest, like cleaning the data, filling NAs, etc.

    It is good practice to define col names as str constants in the child class.
    E.g.
        COL_NAME_1 = "col_name_1" so they can be reused and are easy to change.

    This class defaults to nan_to_null=True when creating the dataframe for simplicity.

    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the CleaningDF."""
        self.df = pl.DataFrame(*args, nan_to_null=True, **kwargs)
        self.clean()

    @classmethod
    @abstractmethod
    def get_rename_map(cls) -> dict[str, str]:
        """Rename the columns.

        This method must be implemented in the child class.
        This will be done before any other cleaning operations.
        Format: {new_name: old_name, ...}
        ClenaingDF convention is to map the real col names to smth in all maps

        Returns:
            dict[str, str]: Dictionary mapping old column names to new column names
            Format: {new_name: old_name, ...}
        """

    @classmethod
    @abstractmethod
    def get_col_dtype_map(cls) -> dict[str, type[pl.DataType]]:
        """Map the column names to the correct data type.

        This method must be implemented in the child class.

        Returns:
            dict[str, type[pl.DataType]]: Dictionary mapping column names to their types
        """

    @classmethod
    @abstractmethod
    def get_drop_null_subsets(cls) -> tuple[tuple[str, ...], ...]:
        """Drops rows where the subset of columns are all null.

        Drops a row if all columns in the subset are null.
        You can define several subsets to check.
        Each returned tuple is one subset.

        Returns:
            tuple[tuple[str, ...], ...]: Tuple of tuples of column names
        """

    @classmethod
    @abstractmethod
    def get_fill_null_map(cls) -> dict[str, Any]:
        """Fill null values with the specified value.

        This method must be implemented in the child class.

        Returns:
            dict[str, Any]: Dictionary mapping column names to their fill value
        """

    @classmethod
    @abstractmethod
    def get_sort_cols(cls) -> tuple[tuple[str, bool], ...]:
        """Sort the dataframe by the specified columns.

        This method must be implemented in the child class.

        Returns:
            tuple[tuple[str, bool], ...]: Tuple of tuples of column names and
                how to sort, True for descending, False for ascending in polars
        """

    @classmethod
    @abstractmethod
    def get_unique_subsets(cls) -> tuple[tuple[str, ...], ...]:
        """Drop duplicates based on the specified subsets.

        This method must be implemented in the child class.
        E.g.
            (
                (("col1", "col2"), # subset 1
                ("col3", "col4"), # subset 2
            )

        Returns:
            tuple[tuple[tuple[str, bool], ...], ...]: Tuple of tuples of column names
        """

    @classmethod
    @abstractmethod
    def get_no_null_cols(cls) -> tuple[str, ...]:
        """Disallow null values in the specified columns.

        This method must be implemented in the child class.

        Returns:
            tuple[str, ...]: Tuple of column names
        """

    @classmethod
    @abstractmethod
    def get_col_converter_map(
        cls,
    ) -> dict[str, Callable[[pl.Series], pl.Series]]:
        """Convert the column to the specified type.

        This method must be implemented in the child class.
        It takes a polars series and returns a polars series.
        Can be used to e.g. parse dates, or do a specific operation on a column.

        Returns:
            dict[str, Callable[[pl.Series], pl.Series]]: Dictionary mapping column names
                to their conversion function
        """

    @classmethod
    @abstractmethod
    def get_add_on_duplicate_cols(cls) -> tuple[str, ...]:
        """Adds the values of cols together when dupliactes of two rows are found.

        This method must be implemented in the child class.
        duplicates are determined by the get_unique_subsets method.

        Returns:
            tuple[str, ...]: Tuple of column names
        """

    @classmethod
    @abstractmethod
    def get_col_precision_map(cls) -> dict[str, int]:
        """Round the column to the specified precision.

        This method must be implemented in the child class.

        Returns:
            dict[str, int]: Dictionary mapping column names to their precision
        """

    @classmethod
    def get_col_names(cls) -> tuple[str, ...]:
        """Get the column names of the dataframe."""
        return tuple(cls.get_col_dtype_map().keys())

    def clean(self) -> None:
        """Clean the dataframe."""
        self.rename_cols()
        self.drop_cols()
        self.fill_nulls()
        self.convert_cols()
        self.drop_null_subsets()
        self.handle_duplicates()
        self.sort_cols()
        self.check()

    @classmethod
    def raise_on_missing_cols(
        cls,
        map_func: Callable[..., dict[str, Any]],
        col_names: tuple[str, ...] | None = None,
    ) -> None:
        """Raise a KeyError if the columns in the map are not in the dataframe."""
        if col_names is None:
            col_names = cls.get_col_names()
        missing_cols = set(col_names) - set(map_func().keys())
        if missing_cols:
            msg = f"Missing columns in {map_func.__name__}: {missing_cols}"
            raise KeyError(msg)

    def rename_cols(self) -> None:
        """Rename the columns according to the rename map."""
        self.raise_on_missing_cols(self.get_rename_map)
        self.df = self.df.rename(reverse_dict(self.get_rename_map()))

    def drop_cols(self) -> None:
        """Drop columns that are not in the col_dtype_map."""
        self.df = self.df.select(self.get_col_names())

    def fill_nulls(self) -> None:
        """Fill null values with the specified values from the fill null map."""
        self.raise_on_missing_cols(self.get_fill_null_map)
        self.df = self.df.with_columns(
            [
                pl.col(col_name).fill_null(fill_value)
                for col_name, fill_value in self.get_fill_null_map().items()
            ]
        )

    def convert_cols(self) -> None:
        """Apply the conversion functions to the columns."""
        self.raise_on_missing_cols(self.get_col_converter_map)
        self.standard_convert_cols()
        self.custom_convert_cols()

    def standard_convert_cols(self) -> None:
        """Assumes some Data standards and converts cols accordingly.

        E.g. strips strings, rounds floats
        """
        for col_name, dtype in self.get_col_dtype_map().items():
            if dtype == pl.Utf8:
                converter = self.strip_col
            elif dtype == pl.Float64:
                converter = self.round_col
            else:
                continue
            self.df = self.df.with_columns(
                pl.col(col_name).map_batches(converter, return_dtype=dtype)
            )

    def custom_convert_cols(self) -> None:
        """Apply the conversion functions to the columns."""
        self.df = self.df.with_columns(
            [
                pl.col(col_name).map_batches(
                    converter, return_dtype=self.get_col_dtype_map()[col_name]
                )
                for col_name, converter in self.get_col_converter_map().items()
                if converter.__name__ != self.skip_col_converter.__name__
            ]
        )

    @classmethod
    def strip_col(cls, col: pl.Series) -> pl.Series:
        """Strip the column of leading and trailing whitespace."""
        return col.str.strip_chars()

    @classmethod
    def lower_col(cls, col: pl.Series) -> pl.Series:
        """Convert the column to lowercase."""
        return col.str.to_lowercase()

    @classmethod
    def round_col(
        cls,
        col: pl.Series,
        precision: int | None = None,
        *,
        compensate: bool = True,
    ) -> pl.Series:
        """Round the column to the specified precision.

        The precision is defined in the get_col_precision_map method.
        """
        if precision is None:
            precision = cls.get_col_precision_map()[str(col.name)]
        if not compensate:
            return col.round(precision)

        # compensate for rounding errors with kahan sum
        error = 0.0
        values = []
        for value in col.to_list():  # Ensure iteration over Python floats
            corrected = value + error
            rounded = round(corrected, precision)
            error = corrected - rounded
            values.append(rounded)

        return pl.Series(name=col.name, values=values, dtype=col.dtype)

    @classmethod
    def skip_col_converter(cls, _col: pl.Series) -> pl.Series:
        """Conversion is not needed for this column and will be skipped.

        Function should not be invoked if col_name is in get_col_converter_map.
        """
        msg = (
            "skip_col_converter is just a flag to skip conversion for a column "
            "and should not be actually called."
        )
        raise NotImplementedError(msg)

    def drop_null_subsets(self) -> None:
        """Drop rows where the subset of columns are all null.

        If no subsets are defined, drop all rows where all columns are null.
        """
        subsets = self.get_drop_null_subsets()
        if not subsets:
            self.df = self.df.drop_nulls()
            return
        for subset in subsets:
            self.df = self.df.drop_nulls(subset=subset)

    def handle_duplicates(self) -> None:
        """Drop duplicates based on the specified subsets.

        If add_on_duplicate_cols are defined, add the values of the cols together.
        This func adds up the vals of the duplicates and keeps the first row.
        E.g. if you have a df with two rows with the same subset
        and value 1 and 2 in col1 the result will be 3 in col1 for the first row.
        """
        for subset in self.get_unique_subsets():
            for col in self.get_add_on_duplicate_cols():
                self.df = self.df.with_columns(pl.col(col).sum().over(subset))
            self.df = self.df.unique(subset=subset, keep="first")

    def sort_cols(self) -> None:
        """Sort the dataframe by the specified columns."""
        cols, desc = zip(*self.get_sort_cols(), strict=True)
        if not cols:
            return
        self.df = self.df.sort(cols, descending=desc)

    def check(self) -> None:
        """Check the data and some conditions.

        This method is called at the end of the clean method.
        checks e.g. non null values in no_null_cols
        """
        self.check_correct_dtypes()
        self.check_no_null_cols()
        self.check_no_nan()

    def check_correct_dtypes(self) -> None:
        """Check that all columns have the correct dtype."""
        schema = self.df.schema
        col_dtype_map = self.get_col_dtype_map()
        for col, dtype in col_dtype_map.items():
            schema_dtype = schema[col]
            if schema_dtype != dtype:
                msg = f"Expected dtype {dtype} for column {col}, got {schema_dtype}"
                raise TypeError(msg)

    def check_no_null_cols(self) -> None:
        """Check that there are no null values in the no null columns."""
        no_null_cols = self.get_no_null_cols()
        # Use a single select to check all columns at once
        null_flags = self.df.select(
            [pl.col(col).is_null().any() for col in no_null_cols]
        )
        # Iterate over columns and check if any have nulls
        for col in no_null_cols:
            if null_flags[col].item():
                msg = f"Null values found in column: {col}"
                raise ValueError(msg)

    def check_no_nan(self) -> None:
        """Check that there are no nan values in the df."""
        float_cols = [
            col
            for col, dtype in self.get_col_dtype_map().items()
            if issubclass(dtype, FloatType)
        ]
        has_nan = self.df.select(
            pl.any_horizontal(pl.col(float_cols).is_nan().any())
        ).item()
        if has_nan:
            msg = "NaN values found in the dataframe"
            raise ValueError(msg)
