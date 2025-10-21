"""
Array of intervals corresponding to IntervalArray of Pandas.
Used for IntervalIndex, which is necessary for Series.value_counts() with 'bins'
argument.

"""

import operator

import numba
import pandas as pd
from numba.core import cgutils, types
from numba.extending import (
    NativeValue,
    box,
    intrinsic,
    make_attribute_wrapper,
    models,
    overload,
    overload_attribute,
    overload_method,
    register_model,
    typeof_impl,
    unbox,
)
from numba.parfors.array_analysis import ArrayAnalysis

import bodo
import bodo.pandas as bd
from bodo.utils.typing import (
    BodoError,
    check_unsupported_args,
    is_list_like_index_type,
    raise_bodo_error,
)


# TODO(ehsan): support Interval values [BE-1243]
class IntervalType(types.Type):
    """
    Type class associated with pandas Interval dtypes (e.g. pd.Interval(1, 3))
    Currently only allows closed="right". TODO: support other forms.
    """

    def __init__(self, dtype):
        # Assuming the LHS and RHS have the same type
        self.dtype = dtype
        super().__init__(name=f"IntervalType({dtype})")


@register_model(IntervalType)
class IntervalScalarModel(models.StructModel):
    def __init__(self, dmm, fe_type):
        # assuming closed="right", TODO: support closed
        members = [
            ("left", fe_type.dtype),
            ("right", fe_type.dtype),
        ]
        models.StructModel.__init__(self, dmm, fe_type, members)

    @property
    def mangling_args(self):
        """
        Avoids long mangled function names in the generated LLVM, which slows down
        compilation time. See [BE-1726]
        https://github.com/numba/numba/blob/8e6fa5690fbe4138abf69263363be85987891e8b/numba/core/funcdesc.py#L67
        https://github.com/numba/numba/blob/8e6fa5690fbe4138abf69263363be85987891e8b/numba/core/itanium_mangler.py#L219
        """
        return self.__class__.__name__, (self._code,)


make_attribute_wrapper(IntervalType, "left", "_left")
make_attribute_wrapper(IntervalType, "right", "_right")


@typeof_impl.register(pd.Interval)
def typeof_interval_scalar(val, c):
    """get Numba type for Interval object. Assuming left/right have the same
    data type, which is enforced in Pandas here:
    https://github.com/pandas-dev/pandas/blob/067749183490feebf0093648122e6a55b43e8c79/pandas/core/arrays/interval.py#L276
    """
    left_type = bodo.typeof(val.left)
    right_type = bodo.typeof(val.right)
    if left_type != right_type:
        raise_bodo_error(
            f"Invalid Interval scalar {val} with different types for left/right values: {left_type} and {right_type}"
        )
    return IntervalType(left_type)


@intrinsic(prefer_literal=True)
def init_interval_scalar(
    typingctx,
    left_t,
    right_t,
):
    """Create a IntervalType with provided data values."""
    assert left_t == right_t

    def codegen(context, builder, sig, args):
        left, right = args
        ts = cgutils.create_struct_proxy(sig.return_type)(context, builder)
        ts.left = left
        ts.right = right
        return ts._getvalue()

    typ = IntervalType(left_t)
    return (
        typ(left_t, right_t),
        codegen,
    )


@overload(pd.Interval, inline="always")
@overload(bd.Interval, inline="always")
def overload_init_interval(left, right, closed="right"):
    """
    Support for the pd.Interval constructor. Note: currently only
    supports the default value of closed="right" because Intervals
    and IntervalArrays do not currently keep track of the closed property.
    """
    unsupported_args = {"closed": closed}
    arg_defaults = {"closed": "right"}
    check_unsupported_args(
        "Interval",
        unsupported_args,
        arg_defaults,
        package_name="pandas",
        module_name="Interval",
    )

    if left != right:
        raise_bodo_error(
            f"Cannot construct pd.Interval from values of different types: {left} and {right}"
        )

    def impl(left, right, closed="right"):  # pragma: no cover
        if right < left:
            raise ValueError("pd.Interval: left side must be >= right side")
        return init_interval_scalar(left, right)

    return impl


@unbox(IntervalType)
def unbox_interval(typ, val, c):
    left_obj = c.pyapi.object_getattr_string(val, "left")
    right_obj = c.pyapi.object_getattr_string(val, "right")

    interval = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    interval.left = c.unbox(typ.dtype, left_obj).value
    interval.right = c.unbox(typ.dtype, right_obj).value

    c.pyapi.decref(left_obj)
    c.pyapi.decref(right_obj)
    is_error = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(interval._getvalue(), is_error=is_error)


@box(IntervalType)
def box_interval(typ, val, c):
    """box interval scalars into pd.Interval objects"""
    interval_struct = cgutils.create_struct_proxy(typ)(c.context, c.builder, value=val)
    left_obj = c.box(typ.dtype, interval_struct.left)
    right_obj = c.box(typ.dtype, interval_struct.right)
    interval_obj = c.pyapi.unserialize(c.pyapi.serialize_object(pd.Interval))
    args = c.pyapi.tuple_pack((left_obj, right_obj))
    kwargs = c.pyapi.dict_pack([])
    res = c.pyapi.call(interval_obj, args, kwargs)
    c.pyapi.decref(args)
    c.pyapi.decref(kwargs)
    c.pyapi.decref(left_obj)
    c.pyapi.decref(right_obj)
    return res


@overload(operator.eq)
def overload_interval_eq(val1, val2):
    """
    Implementation of interval scalar equality: verify left & right match.
    Based on pandas implementation: https://github.com/pandas-dev/pandas/blob/f598670353311a6fff4e6e1e96074ccf0737e6b7/pandas/core/arrays/interval.py#L818
    TODO: once we support multiple types of "closed", need to check that they are the same.
    """
    if not isinstance(val1, IntervalType) or not isinstance(
        val2, IntervalType
    ):  # pragma: no cover
        return
    if val1.dtype != val2.dtype:  # pragma: no cover
        raise_bodo_error(
            f"Unsupported comparison between interval types {val1} and {val2}"
        )

    def impl(val1, val2):  # pragma: no cover
        return (val1._left == val2._left) & (val1._right == val2._right)

    return impl


@overload(operator.ne)
def overload_interval_ne(val1, val2):
    """
    Implementation of interval scalar inequality: verify either of left & right do not match.
    Based on pandas implementation: https://github.com/pandas-dev/pandas/blob/f598670353311a6fff4e6e1e96074ccf0737e6b7/pandas/core/arrays/interval.py#L818
    TODO: once we support multiple types of "closed", need to check that they are the same.
    """
    if not isinstance(val1, IntervalType) or not isinstance(
        val2, IntervalType
    ):  # pragma: no cover
        return
    if val1.dtype != val2.dtype:  # pragma: no cover
        raise_bodo_error(
            f"Unsupported comparison between interval types {val1} and {val2}"
        )

    def impl(val1, val2):  # pragma: no cover
        return (val1._left != val2._left) | (val1._right != val2._right)

    return impl


@overload(operator.lt)
def overload_interval_lt(val1, val2):
    """
    Implementation of interval scalar less-than comparison: the first left endpoint must be less than the second,
    or they can have the same left endpoint but the first right endpoint must be less than the second.
    Based on pandas implementation: https://github.com/pandas-dev/pandas/blob/f598670353311a6fff4e6e1e96074ccf0737e6b7/pandas/core/arrays/interval.py#L818
    TODO: once we support multiple types of "closed", need to check that they are the same.
    """
    if not isinstance(val1, IntervalType) or not isinstance(
        val2, IntervalType
    ):  # pragma: no cover
        return
    if val1.dtype != val2.dtype:  # pragma: no cover
        raise_bodo_error(
            f"Unsupported comparison between interval types {val1} and {val2}"
        )

    def impl(val1, val2):  # pragma: no cover
        return (val1._left < val2._left) | (
            (val1._left == val2._left) & (val1._right < val2._right)
        )

    return impl


@overload(operator.gt)
def overload_interval_gt(val1, val2):
    """
    Implementation of interval scalar greater-than comparison: the first left endpoint must be greater than the second,
    or they can have the same left endpoint but the first right endpoint must be greater than the second.
    Based on pandas implementation: https://github.com/pandas-dev/pandas/blob/f598670353311a6fff4e6e1e96074ccf0737e6b7/pandas/core/arrays/interval.py#L818
    TODO: once we support multiple types of "closed", need to check that they are the same.
    """
    if not isinstance(val1, IntervalType) or not isinstance(
        val2, IntervalType
    ):  # pragma: no cover
        return
    if val1.dtype != val2.dtype:  # pragma: no cover
        raise_bodo_error(
            f"Unsupported comparison between interval types {val1} and {val2}"
        )

    def impl(val1, val2):  # pragma: no cover
        return (val1._left > val2._left) | (
            (val1._left == val2._left) & (val1._right > val2._right)
        )

    return impl


@overload(operator.le)
def overload_interval_le(val1, val2):
    """
    Implementation of interval scalar less-than-or-equal.
    """

    def impl(val1, val2):  # pragma: no cover
        return (val1 == val2) | (val1 < val2)

    return impl


@overload(operator.ge)
def overload_interval_le(val1, val2):
    """
    Implementation of interval scalar greater-than-or-equal.
    """

    def impl(val1, val2):  # pragma: no cover
        return (val1 == val2) | (val1 > val2)

    return impl


@overload_attribute(IntervalType, "left", inline="always")
def overload_interval_scalar_left(interval):
    return lambda interval: interval._left  # pragma: no cover


@overload_attribute(IntervalType, "right", inline="always")
def overload_interval_scalar_right(interval):
    return lambda interval: interval._right  # pragma: no cover


class IntervalArrayType(types.ArrayCompatible):
    """data type corresponding to IntervalArray of Pandas"""

    def __init__(self, arr_type):
        # array type for left and right arrays, which have the same data type
        # see IntervalArray.from_arrays
        # https://github.com/pandas-dev/pandas/blob/c65ed1c40fce55198fcd67c2bef15ab88645c1fa/pandas/core/arrays/interval.py#L277
        self.arr_type = arr_type
        self.dtype = IntervalType(arr_type.dtype)
        super().__init__(name=f"IntervalArrayType({arr_type})")

    @property
    def as_array(self):
        # using types.undefined to avoid Array templates for binary ops
        return types.Array(types.undefined, 1, "C")

    def copy(self):
        return IntervalArrayType(self.arr_type)

    @property
    def mangling_args(self):
        """
        Avoids long mangled function names in the generated LLVM, which slows down
        compilation time. See [BE-1726]
        https://github.com/numba/numba/blob/8e6fa5690fbe4138abf69263363be85987891e8b/numba/core/funcdesc.py#L67
        https://github.com/numba/numba/blob/8e6fa5690fbe4138abf69263363be85987891e8b/numba/core/itanium_mangler.py#L219
        """
        return self.__class__.__name__, (self._code,)


@register_model(IntervalArrayType)
class IntervalArrayModel(models.StructModel):
    def __init__(self, dmm, fe_type):
        # assuming closed="right", TODO: support closed
        members = [
            ("left", fe_type.arr_type),
            ("right", fe_type.arr_type),
        ]
        models.StructModel.__init__(self, dmm, fe_type, members)


make_attribute_wrapper(IntervalArrayType, "left", "_left")
make_attribute_wrapper(IntervalArrayType, "right", "_right")


@typeof_impl.register(pd.arrays.IntervalArray)
def typeof_interval_array(val, c):
    """get Numba type for IntervalArray object. Assuming left/right have the same
    data type, which is enforced in Pandas here:
    https://github.com/pandas-dev/pandas/blob/067749183490feebf0093648122e6a55b43e8c79/pandas/core/arrays/interval.py#L276
    """
    arr_type = bodo.typeof(val._left)
    return IntervalArrayType(arr_type)


@intrinsic
def init_interval_array(typingctx, left, right):
    """Create a IntervalArray with provided left and right arrays."""
    assert left == right, "Interval left/right array types should be the same"

    def codegen(context, builder, signature, args):
        left_val, right_val = args
        # create interval_arr struct and store values
        interval_arr = cgutils.create_struct_proxy(signature.return_type)(
            context, builder
        )
        interval_arr.left = left_val
        interval_arr.right = right_val

        # increase refcount of stored values
        context.nrt.incref(builder, signature.args[0], left_val)
        context.nrt.incref(builder, signature.args[1], right_val)

        return interval_arr._getvalue()

    ret_typ = IntervalArrayType(left)
    sig = ret_typ(left, right)
    return sig, codegen


# array analysis and alias analysis necessary since init_interval_array is inlined in
# Series.value_counts()
def init_interval_array_equiv(self, scope, equiv_set, loc, args, kws):
    """array analysis for init_interval_array()
    output has same shape as input left/right
    """
    assert len(args) == 2 and not kws
    # left/right have the same shape
    all_shapes = []
    for in_arr_var in args:
        in_arr_shape = equiv_set.get_shape(in_arr_var)
        if in_arr_shape is not None:
            all_shapes.append(in_arr_shape[0])

    if len(all_shapes) > 1:
        equiv_set.insert_equiv(*all_shapes)

    left = args[0]
    if equiv_set.has_shape(left):
        return ArrayAnalysis.AnalyzeResult(shape=left, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_interval_arr_ext_init_interval_array = (
    init_interval_array_equiv
)


def alias_ext_init_interval_array(lhs_name, args, alias_map, arg_aliases):
    """output Interval array aliases left/right inputs"""
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map, arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map, arg_aliases)


numba.core.ir_utils.alias_func_extensions[
    ("init_interval_array", "bodo.libs.int_arr_ext")
] = alias_ext_init_interval_array


@box(IntervalArrayType)
def box_interval_arr(typ, val, c):
    """
    Box interval array into IntervalArray object of Pandas
    """
    interval_arr = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)

    # box left
    c.context.nrt.incref(c.builder, typ.arr_type, interval_arr.left)
    left_obj = c.pyapi.from_native_value(typ.arr_type, interval_arr.left, c.env_manager)
    # box right
    c.context.nrt.incref(c.builder, typ.arr_type, interval_arr.right)
    right_obj = c.pyapi.from_native_value(
        typ.arr_type, interval_arr.right, c.env_manager
    )

    # call pd.arrays.IntervalArray.from_arrays(left, right)
    mod_name = c.context.insert_const_string(c.builder.module, "pandas")
    pd_class_obj = c.pyapi.import_module(mod_name)
    arrays_mod_obj = c.pyapi.object_getattr_string(pd_class_obj, "arrays")
    interval_array_class_obj = c.pyapi.object_getattr_string(
        arrays_mod_obj, "IntervalArray"
    )
    interval_array_obj = c.pyapi.call_method(
        interval_array_class_obj, "from_arrays", (left_obj, right_obj)
    )

    c.pyapi.decref(left_obj)
    c.pyapi.decref(right_obj)
    c.pyapi.decref(pd_class_obj)
    c.pyapi.decref(arrays_mod_obj)
    c.pyapi.decref(interval_array_class_obj)
    c.context.nrt.decref(c.builder, typ, val)
    return interval_array_obj


@unbox(IntervalArrayType)
def unbox_interval_arr(typ, val, c):
    """
    Unbox IntervalArray object to native value
    """
    # get left array
    left_obj = c.pyapi.object_getattr_string(val, "_left")
    left = c.pyapi.to_native_value(typ.arr_type, left_obj).value
    c.pyapi.decref(left_obj)

    # get right array
    right_obj = c.pyapi.object_getattr_string(val, "_right")
    right = c.pyapi.to_native_value(typ.arr_type, right_obj).value
    c.pyapi.decref(right_obj)

    # create interval array
    interval_arr = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    interval_arr.left = left
    interval_arr.right = right

    is_error = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(interval_arr._getvalue(), is_error=is_error)


@overload(operator.getitem, no_unliteral=True)
def interval_arr_getitem(arr, ind):
    if not isinstance(arr, IntervalArrayType):
        return

    if isinstance(ind, types.Integer):
        # Cannot handle NA for scalar getitem since not type stable
        def impl(arr, ind):  # pragma: no cover
            if ind < 0:
                ind += len(arr)
            lhs = arr._left[ind]
            rhs = arr._right[ind]
            return init_interval_scalar(lhs, rhs)

        return impl

    if is_list_like_index_type(ind) or isinstance(ind, types.SliceType):

        def impl(arr, ind):  # pragma: no cover
            lhs = arr._left[ind]
            rhs = arr._right[ind]
            return init_interval_array(lhs, rhs)

        return impl

    raise_bodo_error(
        f"getitem for IntervalArray with indexing type {ind} not supported."
    )  # pragma: no cover


@overload(operator.setitem, no_unliteral=True)
def interval_arr_setitem(arr, ind, val):
    if not isinstance(arr, IntervalArrayType):
        return

    if val == types.none or isinstance(val, types.optional):  # pragma: no cover
        # None/Optional goes through a separate step.
        return

    # Supported combinations:
    # 1. interval_arr[integer] = interval_scalar
    # 2. interval_arr[slice] = interval_scalar
    # 3. interval_arr[slice] = interval_array
    if (
        isinstance(ind, (types.Integer, types.SliceType))
        and isinstance(val, IntervalType)
    ) or (
        isinstance(ind, types.SliceType)
        and isinstance(val, (IntervalType, IntervalArrayType))
    ):

        def impl(arr, ind, val):  # pragma: no cover
            arr._left[ind] = val._left
            arr._right[ind] = val._right

        return impl

    raise BodoError(
        f"setitem on interval array with index {ind} and value {val} is currently unsupported"
    )  # pragma: no cover


@overload(len, no_unliteral=True)
def overload_interval_arr_len(A):
    if isinstance(A, IntervalArrayType):
        return lambda A: len(A._left)  # pragma: no cover


@overload_attribute(IntervalArrayType, "shape")
def overload_interval_arr_shape(A):
    return lambda A: (len(A._left),)  # pragma: no cover


@overload_attribute(IntervalArrayType, "ndim")
def overload_interval_arr_ndim(A):
    return lambda A: 1  # pragma: no cover


@overload_attribute(IntervalArrayType, "nbytes")
def overload_interval_arr_nbytes(A):
    return lambda A: A._left.nbytes + A._right.nbytes  # pragma: no cover


@overload_method(IntervalArrayType, "copy", no_unliteral=True)
def overload_interval_arr_copy(A):
    return lambda A: bodo.libs.interval_arr_ext.init_interval_array(
        A._left.copy(),
        A._right.copy(),
    )  # pragma: no cover
