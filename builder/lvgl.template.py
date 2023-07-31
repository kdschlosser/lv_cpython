import pathlib
from typing import Union, Any, Optional, List, TYPE_CHECKING # NOQA
import ctypes as _ctypes
import os
import sys
import inspect  # NOQA
import weakref  # NOQA
from collections.abc import Callable  # NOQA

base_path = os.path.dirname(__file__)

if sys.platform.startswith('win'):
    lib_path = os.path.join(base_path, '_lib_lvgl.dll')
elif sys.platform.startswith('darwin'):
    lib_path = os.path.join(base_path, '_lib_lvgl.dynlib')
else:
    lib_path = os.path.join(base_path, '_lib_lvgl.so')

_lib_lvgl = _ctypes.CDLL(lib_path)

del os
del base_path
del lib_path

_MPY_API = False
__version__ = "0.1.1b"


def binding_version():
    return __version__


INT32_MAX = 0x7FFFFFFF
ANIM_REPEAT_INFINITE = 0xFFFF
ANIM_PLAYTIME_INFINITE = 0xFFFFFFFF

BTNMATRIX_BTN_NONE = 0xFFFF

_COORD_TYPE_SHIFT = 29
_COORD_TYPE_SPEC = 1 << _COORD_TYPE_SHIFT


def COORD_SET_SPEC(x):
    return x | _COORD_TYPE_SPEC


SIZE_CONTENT = COORD_SET_SPEC(2001)
COORD_MAX = (1 << _COORD_TYPE_SHIFT) - 1
COORD_MIN = -COORD_MAX


class _DefaultArg:
    pass


DPI_DEF = 130
DRAW_LABEL_NO_TXT_SEL = 0xFFFF

LABEL_WAIT_CHAR_COUNT = 3
LABEL_DOT_NUM = 3
LABEL_POS_LAST = 0xFFFF
LABEL_TEXT_SELECTION_OFF = DRAW_LABEL_NO_TXT_SEL

TEXTAREA_CURSOR_LAST = 0x7FFF

TABLE_CELL_NONE = 0xFFFF

DROPDOWN_POS_LAST = 0xFFFF

CHART_POINT_NONE = INT32_MAX

ZOOM_NONE = 256

STYLE_PROP_FLAG_NONE = 0
STYLE_PROP_FLAG_INHERITABLE = 1 << 0
STYLE_PROP_FLAG_EXT_DRAW_UPDATE = 1 << 1
STYLE_PROP_FLAG_LAYOUT_UPDATE = 1 << 2
STYLE_PROP_FLAG_PARENT_LAYOUT_UPDATE = 1 << 3
STYLE_PROP_FLAG_LAYER_UPDATE = 1 << 4
STYLE_PROP_FLAG_TRANSFORM = 1 << 5
STYLE_PROP_FLAG_ALL = 0x3F
STYLE_SENTINEL_VALUE = 0xAABBCCDD

COLOR_DEPTH = 32
_COLOR_NATIVE_WITH_ALPHA_SIZE = 4

OPA_MIN = 2
OPA_MAX = 253

RADIUS_CIRCLE = 0x7FFF
GRID_CONTENT = COORD_MAX - 101
GRID_TEMPLATE_LAST = COORD_MAX

_PyCPointerType = type(_ctypes.POINTER(_ctypes.c_uint8))
_CArgObject = type(_ctypes.byref(_ctypes.c_uint8()))
_PyCArrayType = type((_ctypes.c_uint8 * 1))
_PyCSimpleType = type(_ctypes.c_uint8)
_PyCFuncPtrType = type(_ctypes.CFUNCTYPE(None))
_PyCStructType = type(_ctypes.Structure)


class _PythonObjectCache(object):

    _py_obj_storage = {}

    def _remove_ref(self, ref):
        address = id(self)
        if address in self._py_obj_storage:
            del self._py_obj_storage[ref]

    def __call__(self):
        address = id(self)

        if address in self._py_obj_storage:
            return self._py_obj_storage[address]()

        else:
            ref = weakref.ref(self, self._remove_ref)
            self._py_obj_storage[address] = ref
            return self


class _ArrayWrapper(object):

    _c_obj = None
    _len = None

    @property
    def __SIZE__(self):
        return _ctypes.sizeof(self._c_obj)

    def __len__(self):
        if self._len is not None:
            return self._len

        return -1

    def __mul__(self, other):
        if not isinstance(other, int):
            raise TypeError(
                'to convert to an array an integer needs to be used'
            )

        if self._len is None:
            self._len = other

        array = _ctypes.cast(
            self._c_obj,
            _ctypes.POINTER(self.__class__ * other)
        ).contents

        if isinstance(self, char_t):
            res = b''
            for i in range(other):
                c = bytes(array[i])
                if c == b'\x00':
                    break
                res += c

            res = res.decode('utf-8')

        elif isinstance(self, uint8_t):
            res = b''
            for i in range(other):
                c = bytes(array[i])
                res += c

        else:
            res = [array[i]() for i in range(other)]

        return res

    def __getitem__(self, item):
        if self._c_obj is not None:
            if isinstance(item, slice):
                start = item.start
                stop = item.stop
                step = item.step

                if start is None:
                    start = 0

                if step is None:
                    step = 1

                if item.stop is None:
                    raise ValueError(
                        'slicing an array MUST have a stop position'
                    )

                array = _ctypes.cast(
                    self._c_obj,
                    _ctypes.POINTER(self.__class__ * stop)
                ).contents

                if isinstance(self, char_t):
                    res = b''
                    for i in range(start, stop, step):
                        c = bytes(array[i])
                        if c == b'\x00':
                            break
                        res += c

                    res = res.decode('utf-8')

                elif isinstance(self, uint8_t):
                    res = b''
                    for i in range(start, stop, step):
                        c = bytes(array[i])
                        res += c

                else:
                    res = [array[i]() for i in range(start, stop, step)]

                return res


class void_t(_ctypes.c_void_p, _PythonObjectCache, _ArrayWrapper):
    _instances = {}

    @classmethod
    def _del_ref(cls, ref):
        for key, value in cls._instances.items()[:]:
            if value[0] == ref:
                del cls._instances[key]
                return

    @classmethod
    def from_buffer_py_obj(cls, source, offset=None):
        if offset is None:
            buf = cls.from_buffer(source)
        else:
            buf = cls.from_buffer(source, offset)

        address = buf.value

        if address in cls._instances:
            return cls._instances[address][0]

        return source

    @classmethod
    def from_buffer_c_obj(cls, source, offset=None):
        if offset is None:
            buf = cls.from_buffer(source)
        else:
            buf = cls.from_buffer(source, offset)

        address = buf.value

        if address in cls._instances:
            return cls._instances[address][1]

        cls._instances[address] = (source, buf)
        return buf


class float_t(_ctypes.c_float, _PythonObjectCache, _ArrayWrapper):
    pass


class string_t(_ctypes.c_wchar_p, _PythonObjectCache, _ArrayWrapper):
    pass


class bool_t(_ctypes.c_bool, _PythonObjectCache, _ArrayWrapper):
    pass


class char_t(_ctypes.c_char, _PythonObjectCache, _ArrayWrapper):
    pass


class mem_pool_t(_ctypes.c_void_p, _PythonObjectCache, _ArrayWrapper):
    pass


class _Structure(_ctypes.Structure, _PythonObjectCache, _ArrayWrapper):
    _instances = {}

    def _weakref_delete(self, _):
        cls = _ctypes.Structure.__getattribute__(self, '__class__')
        instances = _ctypes.Structure.__getattribute__(self, '_instances')
        address = id(self)

        if address in instances[cls]:
            del instances[cls][address]

    def cast(self, type_):
        cls = _ctypes.Structure.__getattribute__(self, '__class__')
        instances = _ctypes.Structure.__getattribute__(self, '_instances')

        if cls not in instances:
            instances[cls] = {}

        address = id(self)

        if address not in instances[cls]:
            weakref_delete = _ctypes.Structure.__getattribute__(
                self,
                '_weakref_delete'
            )
            instances[cls][address] = weakref.ref(self, weakref_delete)

        if isinstance(type_, _PyCPointerType):
            pointer_type = True
            key = type_._type_  # NOQA
        else:
            pointer_type = False
            key = type_
            type_ = _ctypes.POINTER(type_)

        casts = _ctypes.Structure.__getattribute__(self, '__CAST__')
        if key not in casts:
            pointer = _ctypes.pointer(self)
            casts[key] = (_ctypes.cast(pointer, type_), pointer)

        if pointer_type:
            return casts[key]
        else:
            return casts[key][0]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _ctypes.Structure.__setattr__(self, '__CAST__', {})
        _ctypes.Structure.__setattr__(self, '__ARRAYS__', {})

    def _weakref_callback(self, ref):
        storage = _ctypes.Structure.__getattribute__(self, '_callback_storage')
        if ref in storage:
            del storage[ref]

    def _set_callback(self, field_type, func):
        weakref_callback = (
            _ctypes.Structure.__getattribute__(self, '_weakref_callback')
        )
        if inspect.ismethod(func):
            # This has to be done this way because WeakMethod is not hashable so
            # it cannot be stored in a dictionary and the __hash__ method is
            # read only so it can only be added upon class creation. So we
            # dynamically construct the class pointing __hash__ to the
            # methods __hash__
            weakmethod = type(
                'weakmethod', (weakref.WeakMethod,), {'__hash__': func.__hash__}
            )
            ref = weakmethod(func, weakref_callback)
        elif inspect.isfunction(func):
            ref = weakref.ref(func, weakref_callback)
        else:
            raise TypeError

        if not hasattr(self, '_callback_storage'):
            _ctypes.Structure.__setattr__(self, '_callback_storage', {})

        storage = _ctypes.Structure.__getattribute__(self, '_callback_storage')

        if ref not in storage:
            func = field_type(func)
            storage[ref] = func
        else:
            func = storage[ref]

        return func

    def __setattr__(self, key, value):
        fields = _ctypes.Structure.__getattribute__(self, '_fields_')
        for field in fields:
            if len(field) == 2:
                field_name, field_type = field
            else:
                field_name, field_type = field[:-1]

            if field_name != key:
                continue

            if inspect.isfunction(value) or inspect.ismethod(value):
                set_callback = (
                    _ctypes.Structure.__getattribute__(self, '_set_callback')
                )
                value = set_callback(field_type, value)

            elif (
                    isinstance(field_type, _PyCPointerType) and
                    isinstance(type(value), (_PyCStructType, _PyCSimpleType))
            ):
                value = _ctypes.pointer(value)
            else:
                try:
                    arrays = (
                        _ctypes.Structure.__getattribute__(self, '__ARRAYS__')
                    )
                except AttributeError:
                    _ctypes.Structure.__setattr__(self, '__CAST__', {})
                    _ctypes.Structure.__setattr__(self, '__ARRAYS__', {})
                    arrays = (
                        _ctypes.Structure.__getattribute__(self, '__ARRAYS__')
                    )

                if (
                    isinstance(value, (str, bytes, bytearray)) and
                    isinstance(field_type, _PyCPointerType)
                ):
                    if isinstance(value, str):
                        value = value.encode('utf-8')

                    elif isinstance(value, bytearray):
                        value = bytes(value)

                    type_ = field_type._type_  # NOQA
                    if type_ == char_t and not value.endswith(b'\x00'):
                        value += b'\x00'

                    val_len = len(value)
                    value = _struct_convert_to_ctype(value, field_type)
                    # value = (type_ * val_len)(*value)
                    arrays[key] = (val_len, value)
                    # value = _ctypes.cast(value, field_type)
                else:
                    value = _struct_convert_to_ctype(value, field_type)

            break

        _ctypes.Structure.__setattr__(self, key, value)

    # def __getattr__(self, item):
    #     if item in self.__dict__:
    #         return self.__dict__[item]
    #
    #     return _ctypes.Structure.__getattribute__(self, item)

    def __getattribute__(self, item):
        obj = _ctypes.Structure.__getattribute__(self, item)

        fields = _ctypes.Structure.__getattribute__(self, '_fields_')
        try:
            arrays = _ctypes.Structure.__getattribute__(self, '__ARRAYS__')
        except AttributeError:
            _ctypes.Structure.__setattr__(self, '__CAST__', {})
            _ctypes.Structure.__setattr__(self, '__ARRAYS__', {})
            _ctypes.Structure.__setattr__(self, '_callback_storage', {})
            arrays = _ctypes.Structure.__getattribute__(self, '__ARRAYS__')

        for field in fields:
            if len(field) == 2:
                field_name, field_type = field
            else:
                field_name, field_type = field[:-1]

            if item != field_name:
                continue

            if field_name in arrays:
                val_len = arrays[field_name][0]
            else:
                val_len = None

            return _convert_to_py_type(obj, field_type, val_len)

        return obj


class _Union(_ctypes.Union, _PythonObjectCache, _ArrayWrapper):

    def _weakref_callback(self, ref):
        storage = _ctypes.Union.__getattribute__(self, '_callback_storage')
        if ref in storage:
            del storage[ref]

    def _set_callback(self, field_type, func):
        weakref_callback = _ctypes.Union.__getattribute__(
            self,
            '_weakref_callback'
        )
        if inspect.ismethod(func):
            # This has to be done this way because WeakMethod is not hashable so
            # it cannot be stored in a dictionary and the __hash__ method is
            # read only so it can only be added upon class creation. So we
            # dynamically construct the class pointing __hash__ to the
            # methods __hash__
            weakmethod = type(
                'weakmethod', (weakref.WeakMethod,), {'__hash__': func.__hash__}
            )
            ref = weakmethod(func, weakref_callback)
        elif inspect.isfunction(func):
            ref = weakref.ref(func, weakref_callback)
        else:
            raise TypeError

        if not hasattr(self, '_callback_storage'):
            _ctypes.Union.__setattr__(self, '_callback_storage', {})

        storage = _ctypes.Union.__getattribute__(self, '_callback_storage')

        if ref not in storage:
            func = field_type(func)
            storage[ref] = func
        else:
            func = storage[ref]

        return func

    def __setattr__(self, key, value):
        fields = _ctypes.Union.__getattribute__(self, '_fields_')
        for field_name, field_type in fields:
            if field_name == key:
                if inspect.isfunction(value) or inspect.ismethod(value):
                    set_callback = _ctypes.Union.__getattribute__(
                        self,
                        'set_callback'
                    )
                    value = set_callback(field_type, value)
                elif isinstance(field_type, _PyCPointerType) and isinstance(
                        type(value),
                        (_PyCStructType, _PyCSimpleType)
                ):
                    value = _ctypes.pointer(value)
                else:
                    value = _convert_to_ctype(value, field_type)
                break

        _ctypes.Union.__setattr__(self, key, value)

    def __getattribute__(self, item):
        obj = _ctypes.Union.__getattribute__(self, item)

        if item in ('_special_types_', '__dict__'):
            return obj

        if item in self._special_types_:
            return _convert_to_py_type(obj, self._special_types_[item])

        return _convert_to_py_type(obj)


# This is here for the purposes of type hinting. Any returned values from
# a function or from a structure field that is of an "int" type or a "float"
# type will be returned as a python int or float. the typed return values are
# simply to know exactly what kind of an int is being returned so a user is
# able to act accordingly and no go out of bounds if modifying it and passing
# it to a function that takes the same type. If that does get done it would
# cause undefined behavior.
class _IntMixin(object):
    value = None
    _c_obj = None

    def __neg__(self):
        value = self.value
        self.value = -value

    def __add__(self, x):
        val1 = self.value

        if isinstance(x, (int, float)):
            return val1 + x

        val2 = x.value

        return val1 + val2

    def __sub__(self, x):
        val1 = self.value

        if isinstance(x, (int, float)):
            return val1 - x

        val2 = x.value

        return val1 - val2

    def __mul__(self, x):
        val1 = self.value

        if isinstance(x, int) and self._c_obj is not None:
            array = _ctypes.cast(
                self._c_obj,
                _ctypes.POINTER(self.__class__ * x)
            ).contents

            res = []

            for i in range(x):
                res.append(array[i]())

            return res

        if isinstance(x, (int, float)):
            return val1 * x

        val2 = x.value

        return val1 * val2

    def __floordiv__(self, x):
        val1 = self.value

        if isinstance(x, (int, float)):
            return val1 // x

        val2 = x.value

        return val1 // val2

    def __truediv__(self, x):
        val1 = self.value

        if isinstance(x, (int, float)):
            return val1 / x

        val2 = x.value

        return val1 / val2

    def __mod__(self, x):
        val1 = self.value

        if isinstance(x, int):
            return val1 % x

        val2 = x.value

        return val1 % val2

    def __divmod__(self, x: int) -> tuple[int, int]:
        ...

    def __radd__(self, x):
        val1 = self.value

        if isinstance(x, (int, float)):
            x += val1
            return x

        val2 = x.value
        val2 += val1

        x.value = val1
        return x

    def __rsub__(self, x):
        val1 = self.value

        if isinstance(x, (int, float)):
            x -= val1
            return x

        val2 = x.value
        val2 -= val1

        x.value = val1
        return x

    def __rmul__(self, x):
        val1 = self.value

        if isinstance(x, (int, float)):
            x *= val1
            return x

        val2 = x.value
        val2 *= val1

        x.value = val1
        return x

    def __rfloordiv__(self, x):
        val1 = self.value

        if isinstance(x, (int, float)):
            x //= val1
            return x

        val2 = x.value
        val2 //= val1

        x.value = val1
        return x

    def __rtruediv__(self, x):
        val1 = self.value

        if isinstance(x, (int, float)):
            x /= val1
            return x

        val2 = x.value
        val2 /= val1

        x.value = val1
        return x

    def __rmod__(self, x):
        val1 = self.value

        if isinstance(x, int):
            x %= val1
            return x

        val2 = x.value
        val2 %= val1

        x.value = val1
        return x

    def __pow__(self, x):
        import math

        val1 = self.value

        if isinstance(x, (int, float)):
            return math.pow(val1, x)

        val2 = x.value
        return math.pow(val1, val2)

    def __and__(self, n):
        val1 = self.value

        if isinstance(n, int):
            return val1 & n

        val2 = n.value
        return val1 & val2

    def __or__(self, n):
        val1 = self.value

        if isinstance(n, int):
            return val1 | n

        val2 = n.value
        return val1 | val2

    def __xor__(self, n):
        val1 = self.value

        if isinstance(n, int):
            return val1 ^ n

        val2 = n.value
        return val1 ^ val2

    def __lshift__(self, n):
        val1 = self.value

        if isinstance(n, int):
            return val1 << n

        val2 = n.value
        return val1 << val2

    def __rshift__(self, n):
        val1 = self.value

        if isinstance(n, int):
            return val1 >> n

        val2 = n.value
        return val1 >> val2

    def __rand__(self, n):
        val1 = self.value

        if isinstance(n, int):
            n &= val1
            return n

        val2 = n.value
        val2 &= val1
        n.value = val2
        return n

    def __ror__(self, n):
        val1 = self.value

        if isinstance(n, int):
            n |= val1
            return n

        val2 = n.value
        val2 |= val1

        n.value = val2
        return n

    def __rxor__(self, n):
        val1 = self.value

        if isinstance(n, int):
            n ^= val1
            return n

        val2 = n.value
        val2 ^= val1
        n.value = val2
        return n

    def __rlshift__(self, n):
        val1 = self.value

        if isinstance(n, int):
            n <<= val1
            return n

        val2 = n.value
        val2 <<= val1
        n.value = val2
        return n

    def __rrshift__(self, n):
        val1 = self.value

        if isinstance(n, int):
            n >>= val1
            return n

        val2 = n.value
        val2 >>= val1
        n.value = val2
        return n

    def __eq__(self, x):
        val1 = self.value

        if isinstance(x, (int, float)):
            return x == val1

        val2 = x.value
        return val2 == val1

    def __ne__(self, x):
        val1 = self.value

        if isinstance(x, (int, float)):
            return x != val1

        val2 = x.value
        return val2 != val1

    def __lt__(self, x):
        val1 = self.value

        if isinstance(x, (int, float)):
            return val1 < x

        val2 = x.value
        return val1 < val2

    def __le__(self, x):
        val1 = self.value

        if isinstance(x, (int, float)):
            return val1 <= x

        val2 = x.value
        return val1 <= val2

    def __gt__(self, x):
        val1 = self.value

        if isinstance(x, (int, float)):
            return val1 > x

        val2 = x.value
        return val1 > val2

    def __ge__(self, x):
        val1 = self.value

        if isinstance(x, (int, float)):
            return val1 >= x

        val2 = x.value
        return val1 >= val2

    def __float__(self):
        val1 = self.value

        return float(val1)

    def __int__(self) -> int:
        return self.value

    def __bool__(self) -> bool:
        return bool(self.value)


class uint8_t(_ctypes.c_uint8, _IntMixin, _PythonObjectCache, _ArrayWrapper):
    pass


class uint16_t(_ctypes.c_uint16, _IntMixin, _PythonObjectCache, _ArrayWrapper):
    pass


class uint32_t(_ctypes.c_uint32, _IntMixin, _PythonObjectCache, _ArrayWrapper):
    pass


class uint64_t(_ctypes.c_uint64, _IntMixin, _PythonObjectCache, _ArrayWrapper):
    pass


class int8_t(_ctypes.c_int8, _IntMixin, _PythonObjectCache, _ArrayWrapper):
    pass


class int16_t(_ctypes.c_int16, _IntMixin, _PythonObjectCache, _ArrayWrapper):
    pass


class int32_t(_ctypes.c_int32, _IntMixin, _PythonObjectCache, _ArrayWrapper):
    pass


class int64_t(_ctypes.c_int64, _IntMixin, _PythonObjectCache, _ArrayWrapper):
    pass


class int_t(_ctypes.c_int, _IntMixin, _PythonObjectCache, _ArrayWrapper):
    pass


class size_t(_ctypes.c_size_t, _IntMixin, _PythonObjectCache, _ArrayWrapper):
    pass


if sys.maxsize > 2 ** 32:
    class uintptr_t(_ctypes.c_uint64, _IntMixin):
        pass


    class intptr_t(_ctypes.c_int64, _IntMixin):
        pass

else:
    class uintptr_t(_ctypes.c_uint32, _IntMixin):
        pass


    class intptr_t(_ctypes.c_int32, _IntMixin):
        pass

_type_float_t = Union[float_t, float]
_type_string_t = Union[string_t, str]
_type_bool_t = Union[bool_t, bool]
_type_uint8_t = Union[uint8_t, int]
_type_uint16_t = Union[uint16_t, int]
_type_uint32_t = Union[uint32_t, int]
_type_uint64_t = Union[uint64_t, int]
_type_int8_t = Union[int8_t, int]
_type_int16_t = Union[int16_t, int]
_type_int32_t = Union[int32_t, int]
_type_int64_t = Union[int64_t, int]
_type_int_t = Union[int_t, int]
_type_char_t = Union[char_t, bytes, int]
_type_uintptr_t = Union[uintptr_t, int]
_type_intptr_t = Union[intptr_t, int]
_type_size_t = Union[size_t, int]


# this is kind of a goofy wrapper.
# when setting the types for the functions in the dynamic library this
# gets done using a list. There is a choice to be made where I would place all
# of the python function parameters and iterate over an enumeration of the
# parameters aand use the index to be able to access the type that gets set to
# the c function. The issue there is performance. list iteraation is not the
# fastest thing in the world to do.
#
# second choice since I know the function parameter names is to add those names
# and their associated ctype to the list as attributes. This way I do not have
# to iterate over a list and I am able to collect the type using the parameter
# name
# Here is an example.

# this is where the types get set to the C function
# _lib_lvgl.lv_switch_create.argtypes = CArgList(parent=_ctypes.POINTER(_obj_t))
# _lib_lvgl.lv_switch_create.restype = _ctypes.POINTER(_obj_t)

# and here is the python function
# def switch_create(parent: obj_t) -> obj_t:
#     parent_type = _lib_lvgl.lv_switch_create.argtypes.parent
#
#     if isinstance(parent_type, _PyCPointerType):
#         if not isinstance(parent, _CArgObject):
#             parent = _ctypes.byref(parent)
#
#     res = _lib_lvgl.lv_switch_create(parent)
#
#     while isinstance(type(res), _PyCPointerType):
#         res = res.contents
#
#     try:
#         res = res.value
#     except AttributeError:
#         pass
#
#     return res

# there is additional code but as a truncated version that gives the basic idea
# of what is happening.

class __CArgList(object):

    @classmethod
    def __new__(cls, *args, **kwargs):
        param_names = []
        param_types = []

        for key, value in kwargs.items():
            param_names.append(key)
            param_types.append(value)

        new_cls = type('CArgList', (list,), kwargs)
        return new_cls(param_types)


def _strip_pointer(obj):
    new_obj = obj

    while type(new_obj) == _PyCPointerType:
        if type(new_obj._type_) == _PyCStructType:  # NOQA
            return new_obj._type_  # NOQA

        new_obj = new_obj._type_  # NOQA

    return obj


def _pointer_count(obj):
    count = 0
    while type(obj) == _PyCPointerType:
        count += 1
        if type(obj._type_) == _PyCStructType:  # NOQA
            return count

        obj = obj._type_  # NOQA
    return 0


def _convert_to_py_type(obj, type_=None, pointer_count=None):
    if type_ is not None:
        if isinstance(obj, void_t):
            return void_t.from_buffer_py_obj(obj)

        if type(type(obj)) == _PyCPointerType:
            if pointer_count:
                c_obj = obj

                while pointer_count:
                    pointer_count -= 1
                    try:
                        obj = obj.contents
                    except ValueError:
                        return type_()

                obj = obj()
                obj._c_obj = c_obj
                return obj

            else:
                if type(type_) != _PyCPointerType:
                    c_obj = obj
                    obj = obj.contents()
                    obj._c_obj = c_obj
                    return obj

                c_obj = obj
                while type(type(obj)) == _PyCPointerType:
                    obj = obj.contents

                obj = obj()
                obj._c_obj = c_obj
                return obj

        try:
            res = []
            count = 0
            while True:
                try:
                    item = obj[count]
                except ValueError:
                    return res

                while isinstance(type(item), _PyCPointerType):
                    try:
                        item = item.contents
                    except ValueError:
                        return res

                try:
                    item = item.value
                except AttributeError:
                    pass

                if item:
                    res.append(item)
                else:
                    break

                count += 1

        except TypeError:
            try:
                return obj.value
            except AttributeError:
                try:
                    obj = obj()
                except TypeError:
                    pass

                return obj

        return res

    while isinstance(type(obj), _PyCPointerType):
        try:
            obj = obj.contents
        except ValueError:
            obj = obj._type_()  # NOQA
            return obj

    try:
        obj = obj.value
        return obj
    except AttributeError:
        pass

    obj = obj()
    return obj


_arrays = {}


def _struct_convert_to_ctype(obj, type_):
    if type(type_) == _PyCPointerType:
        pointer_type = True
        type_ = type_._type_  # NOQA
    else:
        pointer_type = False

    if isinstance(obj, (list, tuple)):
        return (type_ * len(obj))(*obj)

    if type(type_) == _PyCFuncPtrType:
        return obj

    if type_ == void_t:
        pass

    if type_ == char_t:
        if pointer_type:
            if isinstance(obj, str):
                obj = obj.encode('utf-8')
                if not obj.endswith(b'\x00'):
                    obj += b'\x00'

            return (char_t * len(obj))(*obj)

        if isinstance(obj, str):
            obj = obj.encode('utf-8')

        return char_t(obj[0])

    if type(type_) == _PyCArrayType:
        return (type_._type_ * len(obj))(*obj)  # NOQA

    if isinstance(obj, bytes) and pointer_type:
        return (type_ * len(obj))(*obj)

    if (
        type(type_) == _PyCSimpleType and
        type(type(obj)) == _PyCSimpleType and
        not isinstance(obj, type_)
    ):
        try:
            return obj.value
        except AttributeError:
            pass

    if type(type_) == _PyCStructType:
        if pointer_type and isinstance(obj, type_):
            return obj

        return obj

    return obj


def _convert_to_ctype(obj, type_):
    if obj is None:
        return None

    if type(type_) == _PyCPointerType:
        pointer_type = True
        type_ = type_._type_  # NOQA
    else:
        pointer_type = False

    if type(type_) == _PyCFuncPtrType:
        return obj

    if type_ == void_t:
        if not pointer_type:
            if isinstance(obj, str):
                obj = obj.encode('utf-8')

                if len(obj) > 1 and not obj.endswith(b'\x00'):
                    obj += b'\x00'

                    obj = (char_t * len(obj))(*obj)
                    return obj
            elif isinstance(obj, bytearray):
                obj = bytes(obj)

            elif isinstance(obj, (_ctypes.Structure, _ctypes.Union)):
                return _ctypes.addressof(obj)

            if type(type(obj)) == _PyCArrayType:
                print(obj)

                return _ctypes.addressof(obj)

            if isinstance(obj, int):
                return obj

            obj = (uint8_t * len(obj))(*obj)
            return obj

        if isinstance(obj, bytes) and pointer_type:
            return (type_ * len(obj))(*obj)

        return obj

    if type_ == char_t:
        if pointer_type:
            if isinstance(obj, str):
                obj = obj.encode('utf-8')
                if not obj.endswith(b'\x00'):
                    obj += b'\x00'

            return (char_t * len(obj))(*obj)
        return char_t(obj[0])

    if type(type_) == _PyCArrayType:
        pass

    if (
        type(type_) == _PyCSimpleType and
        type(type(obj)) == _PyCSimpleType and
        not isinstance(obj, type_)
    ):
        try:
            return obj.value
        except AttributeError:
            pass

    if pointer_type and isinstance(obj, (list, tuple)):
        return (type_ * len(obj))(*obj)

    if type(type_) == _PyCStructType:
        if pointer_type and isinstance(obj, type_):
            return _ctypes.byref(obj)

        return obj

    return obj


def CFUNCTYPE(restype, *argtypes):

    class _CallbackFunction(_ctypes._CFuncPtr):  # NOQA
        _argtypes_ = argtypes
        _restype_ = restype
        _flags_ = _ctypes._FUNCFLAG_CDECL  # NOQA
        _func_ = None

        @classmethod
        def __new__(cls, self, func):
            cls._func_ = func
            return super().__new__(self, cls._callback)

        @classmethod
        def _callback(cls, *args):
            args = list(args)
            py_args = []
            for i, arg in enumerate(args):
                argtype = cls._argtypes_[i]

                if argtype == void_t and isinstance(arg, void_t) and arg:
                    py_arg = arg.value
                else:

                    py_arg = _convert_to_py_type(
                        arg,
                        _strip_pointer(argtype),
                        pointer_count=_pointer_count(argtype)
                    )

                py_args.append(py_arg)

            if cls._restype_ is None:
                cls._func_(*py_args)
                return None

            res = cls._func_(*py_args)

            return _convert_to_ctype(res, cls._restype_)

    return _CallbackFunction


def main_loop():
    if not is_initialized():  # NOQA
        raise RuntimeError('lvgl is not initialized')

    import time

    start = time.time()

    while True:
        stop = time.time()
        diff = int((stop * 1000) - (start * 1000))

        if diff >= 2:
            start = stop
            tick_inc(diff)  # NOQA
            task_handler()  # NOQA


# This next code block overrides the default imnport machinery in Python
# This allows me to inject a non existant module into the import system.
# the "dynamic" module being injected is the display_driver module that runs
# the code to create the SDL window, mouse and keyboard drivers

__SDL_DISPLAY = None

import os  # NOQA

from importlib.abc import (  # NOQA
    Loader as __Loader,
    MetaPathFinder as __MetaPathFinder
)

from importlib.util import (  # NOQA
    spec_from_file_location as __spec_from_file_location
)


class __MyMetaFinder(__MetaPathFinder):

    def find_spec(self, fullname, path, target=None):
        if fullname == 'display_driver':
            return globals()['__spec_from_file_location'](
                fullname,
                f"{fullname}.py",
                loader=globals()['__MyLoader'](fullname),
                submodule_search_locations=None
            )

        if path is None or path == "":
            path = [os.getcwd()]  # top level import --
        if "." in fullname:
            *parents, name = fullname.split(".")
        else:
            name = fullname
        for entry in path:
            if os.path.isdir(os.path.join(entry, name)):
                # this module has child modules
                filename = os.path.join(entry, name, "__init__.py")
                submodule_locations = [os.path.join(entry, name)]
            else:
                filename = os.path.join(entry, f"{name}.py")
                submodule_locations = None
            if not os.path.exists(filename):
                continue

            return globals()['__spec_from_file_location'](
                fullname,
                filename,
                loader=globals()['__MyLoader'](filename),
                submodule_search_locations=submodule_locations
            )

        return None  # we don't know how to import this


class __MyLoader(__Loader):

    def __init__(self, filename):
        self.filename = filename

    def create_module(self, spec):
        return None  # use default module creation semantics

    def exec_module(self, module):
        if self.filename != 'display_driver':
            data = pathlib.Path(self.filename).read_text()
        elif globals()['__SDL_DISPLAY'] is None:
            data = [
                'import lvgl',
                'if not lvgl.is_initialized():',
                '    lvgl.init()',
                '',
                'display = lvgl.sdl_window_create(480, 320)',
                'mouse = lvgl.sdl_mouse_create()',
                'keyboard = lvgl.sdl_keyboard_create()'
            ]

            data = '\n'.join(data)
        else:
            data = ''

        exec(data, vars(module))


sys.meta_path.insert(0, __MyMetaFinder())

del sys


# ****************  INTEGER_TYPES  ****************
['~int_types~']  # NOQA

['~int_typing~']  # NOQA
# ************************************************


# ****************  ENUMERATIONS  ****************
['~enums~']  # NOQA
# ************************************************

OBJ_FLAG_FLEX_IN_NEW_TRACK = OBJ_FLAG_LAYOUT_1  # NOQA


class __fs_driver(object):
    import errno

    _err_mapping = {
        errno.EPERM: FS_RES_NOT_IMP,  # NOQA
        errno.ENOENT: FS_RES_NOT_EX,  # NOQA
        errno.EINTR: FS_RES_HW_ERR,  # NOQA
        errno.EIO: FS_RES_HW_ERR,  # NOQA
        errno.ENXIO: FS_RES_HW_ERR,  # NOQA
        errno.E2BIG: FS_RES_INV_PARAM,  # NOQA
        errno.EBADF: FS_RES_FS_ERR,  # NOQA
        errno.EAGAIN: FS_RES_BUSY,  # NOQA
        errno.ENOMEM: FS_RES_OUT_OF_MEM,  # NOQA
        errno.EACCES: FS_RES_DENIED,  # NOQA
        errno.EFAULT: FS_RES_HW_ERR,  # NOQA
        errno.EBUSY: FS_RES_BUSY,  # NOQA
        errno.EEXIST: FS_RES_FS_ERR,  # NOQA
        errno.ENODEV: FS_RES_HW_ERR,  # NOQA
        errno.ENOTDIR: FS_RES_FS_ERR,  # NOQA
        errno.EISDIR: FS_RES_FS_ERR,  # NOQA
        errno.EINVAL: FS_RES_INV_PARAM,  # NOQA
        errno.EMFILE: FS_RES_BUSY,  # NOQA
        errno.ENOSPC: FS_RES_FULL,  # NOQA
        errno.ESPIPE: FS_RES_FS_ERR,  # NOQA
        errno.EROFS: FS_RES_NOT_IMP,  # NOQA
        errno.ENOSYS: FS_RES_NOT_IMP  # NOQA
    }

    del errno

    def __init__(self):
        import sys

        sys.modules['fs_driver'] = self
        self.__open_files = {}

    def __fs_open_cb(self, _, path, mode):
        if mode == FS_MODE_WR:  # NOQA
            p_mode = 'wb'
        elif mode == FS_MODE_RD:  # NOQA
            p_mode = 'rb'
        elif mode == FS_MODE_WR | FS_MODE_RD:  # NOQA
            p_mode = 'rb+'
        else:
            print(
                f"fs_open_cb - open mode error, {mode} is invalid mode"
            )
            return FS_RES_NOT_IMP  # NOQA

        path = path * 255

        try:
            f = open(path, p_mode)
        except OSError as e:
            errno = self._err_mapping.get(e.errno, FS_RES_UNKNOWN)  # NOQA
            print(f"ERROR: fs_open_callback - '{path}' - {errno} - {e.errno}")
            return errno

        fileno = f.fileno()

        res = dict(
            file=f,
            path=path,
            )
        self.__open_files[fileno] = res

        return fileno

    def __fs_close_cb(self, fs_drv, fs_file):  # NOQA
        fileno = fs_file

        if fileno in self.__open_files:
            cont = self.__open_files.pop(fileno)

            try:
                cont['file'].close()
            except OSError as e:
                path = cont['path']
                errno = self._err_mapping.get(e.errno, FS_RES_UNKNOWN)  # NOQA
                print(
                    f"ERROR: fs_close_cb - '{path}' - {errno} - {e.errno}"
                )
                return errno

        return FS_RES_OK  # NOQA

    def __fs_read_cb(
            self,
            fs_drv,  # NOQA
            fs_file,
            buf,
            num_bytes_to_read,
            num_bytes_read  # NOQA
    ):

        fileno = fs_file

        if fileno in self.__open_files:
            cont = self.__open_files[fileno]
            try:
                data = cont['file'].read(num_bytes_to_read)

                if not isinstance(data, bytes):
                    data = data.decode('utf-8')

                _ctypes.memmove(_ctypes.addressof(buf), data, len(data))
                num_bytes_read = len(data)  # NOQA

            except OSError as e:
                path = cont['path']
                errno = self._err_mapping.get(e.errno, FS_RES_UNKNOWN)  # NOQA
                print(
                    f"ERROR: fs_read_cb - '{path}' - {errno} - {e.errno}"
                )
                return errno

        return FS_RES_OK  # NOQA

    def __fs_seek_cb(self, fs_drv, fs_file, pos, whence):  # NOQA
        fileno = fs_file

        if fileno in self.__open_files:
            cont = self.__open_files[fileno]

            try:
                cont['file'].seek(pos, whence)
            except OSError as e:
                path = cont['path']
                errno = self._err_mapping.get(e.errno, FS_RES_UNKNOWN)  # NOQA
                print(
                    f"ERROR: fs_seek_cb - '{path}' - {errno} - {e.errno}"
                )
                return errno

        return FS_RES_OK  # NOQA

    def __fs_tell_cb(self, fs_drv, fs_file, pos):  # NOQA
        fileno = fs_file

        if fileno in self.__open_files:
            cont = self.__open_files[fileno]

            try:
                tpos = cont['file'].tell()
                pos = tpos  # NOQA
            except OSError as e:
                path = cont['path']
                errno = self._err_mapping.get(e.errno, FS_RES_UNKNOWN)  # NOQA
                print(
                    f"ERROR: fs_tell_cb - '{path}' - {errno} - {e.errno}"
                )
                return errno

        return FS_RES_OK  # NOQA

    def __fs_write_cb(self, fs_drv, fs_file, buf, btw, bw):  # NOQA
        fileno = fs_file

        if fileno in self.__open_files:
            cont = self.__open_files[fileno]

            try:
                num_bytes = cont['file'].write(buf[:btw])
                bw[0] = bw._type_(num_bytes)  # NOQA
            except OSError as e:
                path = cont['path']
                errno = self._err_mapping.get(e.errno, FS_RES_UNKNOWN)  # NOQA
                print(
                    f"ERROR: fs_write_cb - '{path}' - {errno} - {e.errno}"
                )
                return errno

        return FS_RES_OK  # NOQA

    def fs_register(self, fs_drv, letter, cache_size=500):

        fs_drv_init(fs_drv)  # NOQA
        fs_drv.letter = letter
        fs_drv.open_cb = self.__fs_open_cb
        fs_drv.read_cb = self.__fs_read_cb
        fs_drv.write_cb = self.__fs_write_cb
        fs_drv.seek_cb = self.__fs_seek_cb
        fs_drv.tell_cb = self.__fs_tell_cb
        fs_drv.close_cb = self.__fs_close_cb

        if cache_size >= 0:
            fs_drv.cache_size = cache_size

        fs_drv_register(fs_drv)  # NOQA


__fs_driver()


# ***************  STRUCTS/UNIONS  ***************
['~structs~']  # NOQA
# ************************************************


# ******************  TYPEDEFS  ******************
['~typedefs~']  # NOQA
# ************************************************

['~func_pointers~']  # NOQA

# ***************  STRUCT FIELDS  ****************
['~struct_fields~']  # NOQA
# ************************************************

# ************ FUNCTION TYPE DECLS ***************
# pointer_decls
# ************************************************

# *****************  FUNCTIONS  ******************
# func_restypes

['~py_types~']  # NOQA

['~functions~']  # NOQA
# ************************************************

['~py_struct_sizes~']  # NOQA

# ************************************************


