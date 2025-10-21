#!/usr/bin/env python3

import ctypes
from collections.abc import Generator

from typing_extensions import Any, Self

UINT8_MAX = 2**8 - 1
UINT16_MAX = 2**16 - 1
UINT32_MAX = 2**32 - 1
UINT64_MAX = 2**64 - 1
INT8_MIN = -(2**7)
INT16_MIN = -(2**15)
INT32_MIN = -(2**31)
UINT64_MIN = -(2**63)
INT8_MAX = 2**7 - 1
INT16_MAX = 2**15 - 1
INT32_MAX = 2**31 - 1
INT64_MAX = 2**63 - 1


def bytes_to_uint8(b: bytes):
    return (len(b) * ctypes.c_uint8)(*b)


class VLACompatLittleEndianStruct(ctypes.LittleEndianStructure):
    """
    Class to simplify working with variable length arrays.
    The standard `ctypes.LittleEndianStructure` field definitions can
    be extended with an optional `vla_field` class parameter, which
    will be populated when constructed with `vla_from_buffer_copy`.
    """

    vla_field: tuple[str, type[Any]] | None = None
    vla_counted_by: str | None = None

    @classmethod
    def vla_from_buffer_copy(cls, source, offset=0) -> Self:
        """
        Equivalent to `from_buffer_copy`, except if the `vla_field`
        class property is not `None`, it will consume the remainder of
        `source` to populate the trailing variable length array.
        """

        base = cls.from_buffer_copy(source, offset)
        vla_val: list | VLACompatLittleEndianStruct
        if cls.vla_field is None:
            return base

        remainder = source[ctypes.sizeof(cls) :]
        vla_field_name, vla_field_type = cls.vla_field  # type: ignore

        if issubclass(vla_field_type, ctypes.Array):
            array_base: ctypes._PyCSimpleType = vla_field_type._type_  # type: ignore
            if hasattr(array_base, "vla_counted_by"):
                # This is an array of VLA arrays where the sub-arrys define their own length
                vla_val = []
                # Consume all remaining buffer bytes
                while len(remainder) > 0:
                    sub_vla_field_name, sub_vla_field_type = array_base.vla_field  # type: ignore
                    sub_array_base: ctypes._CData = sub_vla_field_type._type_  # type: ignore
                    sub_base = array_base.from_buffer_copy(remainder)
                    sub_base_size = ctypes.sizeof(sub_base)
                    sub_count = getattr(sub_base, array_base.vla_counted_by)
                    if sub_count < 0:
                        # Assume that negative length is an error code and use 0
                        vla_val.append(sub_base)
                        sub_vla_size = 0
                    else:
                        sub_vla_type = sub_count * sub_array_base
                        # Don't use ctypes.sizeof on constructed type, it returns the wrong value
                        sub_vla_size = sub_count * ctypes.sizeof(sub_array_base)
                        sub_vla_val = sub_vla_type.from_buffer_copy(remainder[sub_base_size:])
                        setattr(sub_base, sub_vla_field_name, sub_vla_val)
                        vla_val.append(sub_base)
                    remainder = remainder[sub_base_size + sub_vla_size :]
            else:
                # Determine the number of VLA elements on "source"
                vla_byte_len = (len(source) - offset) - ctypes.sizeof(cls)
                vla_element_size = ctypes.sizeof(array_base)
                if vla_byte_len % vla_element_size != 0:
                    raise TypeError(f"Unaligned VLA buffer for {cls} (len {len(source)})")
                vla_num = vla_byte_len // vla_element_size
                vla_type = vla_num * array_base
                vla_val = vla_type.from_buffer_copy(remainder)

        elif issubclass(vla_field_type, VLACompatLittleEndianStruct):
            vla_val = vla_field_type.vla_from_buffer_copy(remainder)
        else:
            raise RuntimeError(f"Unhandled VLA type {vla_field_type}")

        setattr(base, vla_field_name, vla_val)
        return base

    def iter_fields(self, prefix: str = "") -> Generator[tuple[str, Any], None, None]:
        """
        Yield all fields of the class as `("name", value)`. Fields that are themselves
        instances of `VLACompatLittleEndianStruct` will have their fields yielded
        individually as `("name.subfield", value)`.
        """
        for field_name, _field_type in self._fields_:  # type: ignore
            val = getattr(self, field_name)
            if isinstance(val, VLACompatLittleEndianStruct):
                yield from val.iter_fields(f"{field_name}.")
            else:
                yield (f"{prefix}{field_name}", val)
        if vla_field := self.vla_field:
            val = getattr(self, vla_field[0])
            if isinstance(val, VLACompatLittleEndianStruct):
                yield from val.iter_fields(f"{vla_field[0]}.")
            else:
                yield (f"{prefix}{vla_field[0]}", val)
