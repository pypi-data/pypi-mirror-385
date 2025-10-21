"""
Implements BodoSQL array kernels related to VARIANT utilities
"""

from numba.core import types
from numba.extending import overload

import bodo
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.struct_arr_ext import StructType
from bodosql.kernels.array_kernel_utils import gen_vectorized


def is_array(V):  # pragma: no cover
    pass


@overload(is_array)
def overload_is_array(V):
    """Implementation of IS_ARRAY which accepts any type (including variants) and returns true on rows where the value is an array"""
    # TODO(aneesh) this wouldn't actually work for true variant types that have
    # mixed data types internally - this eventually needs to compute whether or
    # not each row is an array when we have a runtime notion of VARIANT.
    out_dtype = bodo.types.boolean_array_type
    in_dtype = V
    is_series = isinstance(V, bodo.hiframes.pd_series_ext.SeriesType)
    if is_series:
        in_dtype = V.data
    result = isinstance(in_dtype, ArrayItemArrayType)
    scalar_text = f"res[i] = {result}"
    return gen_vectorized(
        ["V"],
        [V],
        [True],
        scalar_text,
        out_dtype,
    )


def is_object(V):  # pragma: no cover
    pass


@overload(is_object)
def overload_is_object(V):
    """Implementation of IS_OBJECT which accepts any type (including variants) and returns true on rows where the value is an object"""
    # TODO(aneesh) this wouldn't actually work for true variant types that have
    # mixed data types internally - this eventually needs to compute whether or
    # not each row is an object when we have a runtime notion of VARIANT.
    # TODO(aneesh) most IS_* functions will look very similar, so a future
    # refactor should create a common template method or something.
    out_dtype = bodo.types.boolean_array_type
    in_dtype = V
    is_series = isinstance(V, bodo.hiframes.pd_series_ext.SeriesType)
    if is_series:
        in_dtype = V.data
    result = isinstance(
        in_dtype,
        (
            bodo.types.StructArrayType,
            StructType,
            bodo.types.MapArrayType,
            types.DictType,
        ),
    )
    scalar_text = f"res[i] = {result}"
    return gen_vectorized(
        ["V"],
        [V],
        [True],
        scalar_text,
        out_dtype,
    )
