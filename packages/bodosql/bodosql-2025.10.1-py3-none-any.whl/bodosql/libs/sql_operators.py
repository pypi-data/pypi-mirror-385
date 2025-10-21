"""
Library of BodoSQL operators that don't have a Python equivalent
"""

import numba
import pandas as pd
from numba import generated_jit
from numba.extending import overload, register_jitable

import bodo


def sql_null_equal_column(arg0, arg1):
    """Function that replicates the behavior of MYSQL's <=> operator on at
    least one column input"""
    return (arg0.isna() & arg1.isna()) | (arg0 == arg1).fillna(False)


# TODO: Move to the engine for more efficient inlining?
# Note we are inline for more efficient Series processing
# + to avoid dist diagnostics issues.
@overload(sql_null_equal_column, inline="always")
def overload_sql_null_equal_column(arg0, arg1):
    """Function that replicates the behavior of MYSQL's <=> operator on at
    least one column input"""
    # 2 columns
    if isinstance(arg0, bodo.types.SeriesType) and isinstance(
        arg1, bodo.types.SeriesType
    ):
        return lambda arg0, arg1: (arg0.isna() & arg1.isna()) | (arg0 == arg1).fillna(
            False
        )
    # 1 column and 1 scalar
    elif isinstance(arg0, bodo.types.SeriesType):
        if arg1 == bodo.types.none:
            return lambda arg0, arg1: arg0.isna()
        elif isinstance(arg1, bodo.types.optional):

            def impl(arg0, arg1):
                # Note: This is check is separate to avoid optional type issues
                if arg1 is None:
                    # Note: astype is necessary here to unify the return types.
                    # Ideally all would be non-nullable bools, but this conversion
                    # isn't working properly in Bodo.
                    return arg0.isna().astype("boolean")
                arg1 = bodo.utils.indexing.unoptional(arg1)
                if pd.isna(arg1):
                    return arg0.isna().astype("boolean")
                return (arg0 == arg1).fillna(False)

            return impl
        else:
            return lambda arg0, arg1: (arg0 == arg1).fillna(False)
    elif isinstance(arg1, bodo.types.SeriesType):
        return lambda arg0, arg1: sql_null_equal_column(arg1, arg0)


@numba.njit
def sql_null_equal_scalar(arg0, arg1):
    return sql_null_equal_scalar_impl(arg0, arg1)


@generated_jit(nopython=True)
def sql_null_equal_scalar_impl(arg0, arg1):
    """
    Function that replicates the behavior of MYSQL's <=> operator on scalars,
    properly handling the null/optional cases. Equivalent to =, but returns
    true if both inputs are None/NA. To support values like np.nan, we also
    check NA at runtime.
    """

    if arg0 == bodo.types.none and arg1 == bodo.types.none:
        return lambda arg0, arg1: True
    elif isinstance(arg0, bodo.types.optional) or isinstance(arg1, bodo.types.optional):

        def impl(arg0, arg1):
            if arg0 is not None:
                arg0 = bodo.utils.indexing.unoptional(arg0)
            if arg1 is not None:
                arg1 = bodo.utils.indexing.unoptional(arg1)
            return null_equal_runtime(arg0, arg1)

        return impl
    else:
        return lambda arg0, arg1: null_equal_runtime(arg0, arg1)


@register_jitable
def null_equal_runtime(arg0, arg1):
    if pd.isna(arg0) and pd.isna(arg1):
        return True
    elif pd.isna(arg0) or pd.isna(arg1):
        return False
    else:
        return arg0 == arg1


@register_jitable
def pd_to_datetime_with_format(s, my_format):
    return pd.to_datetime(s, format=my_format)


@register_jitable
def pd_to_date(arg0):
    return pd.to_datetime(arg0).date()
