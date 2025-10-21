
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import os


if os.environ.get("TVM_FFI_BUILD_DOCS", "0") == "0":
    try:
        # optionally import torch and setup torch related utils
        import torch
    except ImportError:
        torch = None

    try:
        # optionally import numpy
        import numpy
    except ImportError:
        numpy = None

    try:
        # optionally import ml_dtypes
        import ml_dtypes
    except ImportError:
        ml_dtypes = None
else:
    torch = None
    numpy = None
    ml_dtypes = None


_CLASS_DTYPE = None


def _set_class_dtype(cls):
    global _CLASS_DTYPE
    _CLASS_DTYPE = cls


def _create_dtype_from_tuple(cls, code, bits, lanes):
    cdef DLDataType cdtype
    cdtype.code = code
    cdtype.bits = bits
    cdtype.lanes = lanes
    ret = cls.__new__(cls, str(cdtype))
    (<DataType>ret).cdtype = cdtype
    return ret


cdef class DataType:
    """DataType is a wrapper around DLDataType.

    Parameters
    ----------
    dtype_str : str
        The string representation of the data type
    """
    cdef DLDataType cdtype

    def __init__(self, dtype_str):
        cdef ByteArrayArg dtype_str_arg = ByteArrayArg(c_str(dtype_str))
        CHECK_CALL(TVMFFIDataTypeFromString(dtype_str_arg.cptr(), &(self.cdtype)))

    def __reduce__(self):
        cls = type(self)
        return (_create_dtype_from_tuple,
                (cls, self.cdtype.code, self.cdtype.bits, self.cdtype.lanes))

    def __eq__(self, other):
        if not isinstance(other, DataType):
            return False
        return (
            self.cdtype.code == other.cdtype.code
            and self.cdtype.bits == other.cdtype.bits
            and self.cdtype.lanes == other.cdtype.lanes
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def type_code(self):
        return self.cdtype.code

    @property
    def bits(self):
        return self.cdtype.bits

    @property
    def lanes(self):
        return self.cdtype.lanes

    @property
    def itemsize(self):
        """Get the number of bytes of a single element of this data type. When the number of lanes
        is greater than 1, the itemsize is the size of the vector type.

        Returns
        -------
        itemsize : int
            The number of bytes of a single element of this data type
        """
        lanes_as_int = self.cdtype.lanes
        if lanes_as_int < 0:
            raise ValueError("Cannot determine itemsize for scalable vector types")
        return (self.cdtype.bits * self.cdtype.lanes + 7) // 8

    def __str__(self):
        cdef TVMFFIAny temp_any
        cdef TVMFFIByteArray* bytes_ptr
        cdef TVMFFIByteArray bytes

        CHECK_CALL(TVMFFIDataTypeToString(&(self.cdtype), &temp_any))
        if temp_any.type_index == kTVMFFISmallStr:
            bytes = TVMFFISmallBytesGetContentByteArray(&temp_any)
            res = bytearray_to_str(&bytes)
            return res

        bytes_ptr = TVMFFIBytesGetByteArrayPtr(temp_any.v_obj)
        res = bytearray_to_str(bytes_ptr)
        CHECK_CALL(TVMFFIObjectDecRef(temp_any.v_obj))
        return res


cdef inline object make_ret_dtype(TVMFFIAny result):
    cdtype = DataType.__new__(DataType)
    (<DataType>cdtype).cdtype = result.v_dtype
    val = str.__new__(_CLASS_DTYPE, cdtype.__str__())
    val.__tvm_ffi_dtype__ = cdtype
    return val


cdef TORCH_DTYPE_TO_DTYPE = {}
cdef NUMPY_DTYPE_TO_DTYPE = {}
cdef MLDTYPES_DTYPE_TO_DTYPE = {}

if torch is not None:
    TORCH_DTYPE_TO_DTYPE = {
        torch.int8: DLDataType(0, 8, 1),
        torch.short: DLDataType(0, 16, 1),
        torch.int16: DLDataType(0, 16, 1),
        torch.int32: DLDataType(0, 32, 1),
        torch.int: DLDataType(0, 32, 1),
        torch.int64: DLDataType(0, 64, 1),
        torch.long: DLDataType(0, 64, 1),
        torch.uint8: DLDataType(1, 8, 1),
        torch.uint16: DLDataType(1, 16, 1),
        torch.uint32: DLDataType(1, 32, 1),
        torch.uint64: DLDataType(1, 64, 1),
        torch.float16: DLDataType(2, 16, 1),
        torch.half: DLDataType(2, 16, 1),
        torch.float32: DLDataType(2, 32, 1),
        torch.float: DLDataType(2, 32, 1),
        torch.float64: DLDataType(2, 64, 1),
        torch.double: DLDataType(2, 64, 1),
        torch.bfloat16: DLDataType(4, 16, 1),
        torch.bool: DLDataType(6, 8, 1),
        torch.float8_e4m3fn: DLDataType(10, 8, 1),
        torch.float8_e4m3fnuz: DLDataType(11, 8, 1),
        torch.float8_e5m2: DLDataType(12, 8, 1),
        torch.float8_e5m2fnuz: DLDataType(13, 8, 1),
    }
    if hasattr(torch, "float8_e8m0fnu"):
        TORCH_DTYPE_TO_DTYPE[torch.float8_e8m0fnu] = DLDataType(14, 8, 1)
    if hasattr(torch, "float4_e2m1fn_x2"):
        TORCH_DTYPE_TO_DTYPE[torch.float4_e2m1fn_x2] = DLDataType(17, 4, 2)

    def _convert_torch_dtype_to_ffi_dtype(torch_dtype):
        cdef DLDataType cdtype = TORCH_DTYPE_TO_DTYPE[torch_dtype]
        ret = DataType.__new__(DataType, str(cdtype))
        (<DataType>ret).cdtype = cdtype
        return ret
else:
    def _convert_torch_dtype_to_ffi_dtype(torch_dtype):
        raise ValueError("torch not found")

if ml_dtypes is not None:
    MLDTYPES_DTYPE_TO_DTYPE = {
        numpy.dtype(ml_dtypes.int2): DLDataType(0, 2, 1),
        numpy.dtype(ml_dtypes.int4): DLDataType(0, 4, 1),
        numpy.dtype(ml_dtypes.uint2): DLDataType(1, 2, 1),
        numpy.dtype(ml_dtypes.uint4): DLDataType(1, 4, 1),
        numpy.dtype(ml_dtypes.bfloat16): DLDataType(4, 16, 1),
        numpy.dtype(ml_dtypes.float8_e3m4): DLDataType(7, 8, 1),
        numpy.dtype(ml_dtypes.float8_e4m3): DLDataType(8, 8, 1),
        numpy.dtype(ml_dtypes.float8_e4m3b11fnuz): DLDataType(9, 8, 1),
        numpy.dtype(ml_dtypes.float8_e4m3fn): DLDataType(10, 8, 1),
        numpy.dtype(ml_dtypes.float8_e4m3fnuz): DLDataType(11, 8, 1),
        numpy.dtype(ml_dtypes.float8_e5m2): DLDataType(12, 8, 1),
        numpy.dtype(ml_dtypes.float8_e5m2fnuz): DLDataType(13, 8, 1),
        numpy.dtype(ml_dtypes.float8_e8m0fnu): DLDataType(14, 8, 1),
        numpy.dtype(ml_dtypes.float6_e2m3fn): DLDataType(15, 6, 1),
        numpy.dtype(ml_dtypes.float6_e3m2fn): DLDataType(16, 6, 1),
        numpy.dtype(ml_dtypes.float4_e2m1fn): DLDataType(17, 4, 1),
    }

if numpy is not None:
    NUMPY_DTYPE_TO_DTYPE = {
        numpy.dtype(numpy.int8): DLDataType(0, 8, 1),
        numpy.dtype(numpy.int16): DLDataType(0, 16, 1),
        numpy.dtype(numpy.int32): DLDataType(0, 32, 1),
        numpy.dtype(numpy.int64): DLDataType(0, 64, 1),
        numpy.dtype(numpy.uint8): DLDataType(1, 8, 1),
        numpy.dtype(numpy.uint16): DLDataType(1, 16, 1),
        numpy.dtype(numpy.uint32): DLDataType(1, 32, 1),
        numpy.dtype(numpy.uint64): DLDataType(1, 64, 1),
        numpy.dtype(numpy.float16): DLDataType(2, 16, 1),
        numpy.dtype(numpy.float32): DLDataType(2, 32, 1),
        numpy.dtype(numpy.float64): DLDataType(2, 64, 1),
        **MLDTYPES_DTYPE_TO_DTYPE,
    }

    def _convert_numpy_dtype_to_ffi_dtype(numpy_dtype):
        cdef DLDataType cdtype = NUMPY_DTYPE_TO_DTYPE[numpy_dtype]
        ret = DataType.__new__(DataType, str(cdtype))
        (<DataType>ret).cdtype = cdtype
        return ret
else:
    def _convert_torch_dtype_to_ffi_dtype(torch_dtype):
        raise ValueError("numpy not found")
