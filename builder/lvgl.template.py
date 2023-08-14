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

__version__ = "0.1.1b"


def binding_version():
    return __version__


class _DefaultArg:
    pass


def _POINTER(obj):
    pointer = _ctypes.POINTER(obj)

    def __hash__(self):
        return hash(_ctypes.addressof(self))

    setattr(pointer, '__hash__', __hash__)

    return pointer


def _pointer(obj):
    pointer = _ctypes.pointer(obj)

    def __hash__(self):
        return hash(_ctypes.addressof(self))

    setattr(pointer, '__hash__', __hash__)

    return pointer


INT32_MAX = 0x7FFFFFFF


def COORD_SET_SPEC(x):
    return x | _COORD_TYPE_SPEC


DISP_ROT_MAX_BUF = 1920 * 1080 * 4

SPAN_SNIPPET_STACK_SIZE = 64

_SWITCH_KNOB_EXT_AREA_CORRECTION = 2

GRADIENT_MAX_STOPS = 32
STYLE_SENTINEL_VALUE = 0xAABBCCDD

BEZIER_VAL_SHIFT = 10
TRIGO_SHIFT = 15
BEZIER_VAL_MAX = 1 << BEZIER_VAL_SHIFT
TRIGO_SIN_MAX = 32768
RAND_MAX = 32767

BTNMATRIX_BTN_NONE = 0xFFFF

DRAW_SW_LAYER_SIMPLE_BUF_SIZE = 64 * 1024
DRAW_SW_DRAW_UNIT_CNT = 1
DRAW_SW_SHADOW_CACHE_SIZE = 1024

SPINBOX_MAX_DIGIT_COUNT = 10

DPI_DEF = 130
RADIUS_CIRCLE = 0x7FFF
OPA_MIN = 2
OPA_MAX = 253
OS_CUSTOM = 255
LAYER_MAX_MEMORY_USAGE = 1024

LED_BRIGHT_MIN = 80
LED_BRIGHT_MAX = 255

FILE_EXPLORER_PATH_MAX_LEN = 128

CHART_POINT_NONE = INT32_MAX

DROPDOWN_POS_LAST = 0xFFFF

NO_TIMER_READY = 0xFFFFFFFF
NO_TASK_READY = NO_TIMER_READY

LABEL_POS_LAST = 0xFFFF
LABEL_WAIT_CHAR_COUNT = 3
LABEL_DOT_NUM = 3
LABEL_TEXT_SELECTION = 1
DRAW_LABEL_NO_TXT_SEL = 0xFFFF
LABEL_TEXT_SELECTION_OFF = DRAW_LABEL_NO_TXT_SEL

IME_PINYIN_K9_CAND_TEXT_NUM = 3
IME_PINYIN_CAND_TEXT_NUM = 6
IME_PINYIN_K9_MAX_INPUT = 7

THEME_DEFAULT_TRANSITION_TIME = 80

TABLE_CELL_NONE = 0XFFFF

_ZOOM_INV_UPSCALE = 5
ZOOM_NONE = 256
IMG_ZOOM_NONE = ZOOM_NONE

IMGFONT_BPP = 9
IMGFONT_PATH_MAX_LEN = 64
IMGFONT_USE_IMG_CACHE_HEADER = 0

COLOR_DEPTH = 32
COLOR_SIZE = COLOR_DEPTH
_COLOR_NATIVE_WITH_ALPHA_SIZE = 4

FOPEN_MAX = 20
FILENAME_MAX = 1024
FS_MAX_PATH_LENGTH = 256
FS_MAX_FN_LENGTH = 64

LVGL_VERSION_MINOR = 0
LVGL_VERSION_MAJOR = 9
LVGL_VERSION_PATCH = 0
LVGL_VERSION_INFO = b"dev"

SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2

_FLEX_COLUMN = 1 << 0
_FLEX_WRAP = 1 << 2
_FLEX_REVERSE = 1 << 3

_COORD_TYPE_SHIFT = 29
_COORD_TYPE_PX = 0 << _COORD_TYPE_SHIFT
_COORD_TYPE_SPEC = 1 << _COORD_TYPE_SHIFT
_COORD_TYPE_MASK = 3 << _COORD_TYPE_SHIFT
_COORD_TYPE_PX_NEG = 3 << _COORD_TYPE_SHIFT

COORD_MAX = (1 << _COORD_TYPE_SHIFT) - 1
COORD_MIN = -COORD_MAX

SIZE_CONTENT = COORD_SET_SPEC(2001)

GRID_CONTENT = COORD_MAX - 101
GRID_TEMPLATE_LAST = COORD_MAX

TXT_LINE_BREAK_LONG_PRE_MIN_LEN = 3
TXT_LINE_BREAK_LONG_LEN = 0
TXT_LINE_BREAK_LONG_POST_MIN_LEN = 3
TXT_BREAK_CHARS = b" ,.;:-_)]}"
TXT_ENC_UTF8 = 1
TXT_ENC = TXT_ENC_UTF8

TEXTAREA_DEF_PWD_SHOW_TIME = 1500
TEXTAREA_CURSOR_LAST = 0x7FFF

ANIM_PLAYTIME_INFINITE = 0xFFFFFFFF
ANIM_REPEAT_INFINITE = 0xFFFF

CALENDAR_DEFAULT_MONTH_NAMES = (
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December")
USE_CALENDAR_HEADER_ARROW = 1
CALENDAR_DEFAULT_DAY_NAMES = ("Su", "Mo", "Tu", "We", "Th", "Fr", "Sa")
CALENDAR_WEEK_STARTS_MONDAY = 0

STYLE_PROP_META_INITIAL = 0x4000
STYLE_PROP_META_INHERIT = 0x8000
STYLE_PROP_META_MASK = STYLE_PROP_META_INHERIT | STYLE_PROP_META_INITIAL
STYLE_PROP_FLAG_NONE = 0
STYLE_PROP_FLAG_INHERITABLE = 1 << 0
STYLE_PROP_FLAG_EXT_DRAW_UPDATE = 1 << 1
STYLE_PROP_FLAG_LAYOUT_UPDATE = 1 << 2
STYLE_PROP_FLAG_PARENT_LAYOUT_UPDATE = 1 << 3
STYLE_PROP_FLAG_LAYER_UPDATE = 1 << 4
STYLE_PROP_FLAG_TRANSFORM = 1 << 5
STYLE_PROP_FLAG_ALL = 0x3F

BIDI_LRO = b"\xE2\x80\xAD"
BIDI_RLO = b"\xE2\x80\xAE"

SYMBOL_AUDIO = b"\xEF\x80\x81"
SYMBOL_BACKSPACE = b"\xEF\x95\x9A"
SYMBOL_BARS = b"\xEF\x83\x89"
SYMBOL_BATTERY_1 = b"\xEF\x89\x83"
SYMBOL_BATTERY_2 = b"\xEF\x89\x82"
SYMBOL_BATTERY_3 = b"\xEF\x89\x81"
SYMBOL_BATTERY_EMPTY = b"\xEF\x89\x84"
SYMBOL_BATTERY_FULL = b"\xEF\x89\x80"
SYMBOL_BELL = b"\xEF\x83\xB3"
SYMBOL_BLUETOOTH = b"\xEF\x8a\x93"
SYMBOL_BULLET = b"\xE2\x80\xA2"
SYMBOL_CALL = b"\xEF\x82\x95"
SYMBOL_CHARGE = b"\xEF\x83\xA7"
SYMBOL_CLOSE = b"\xEF\x80\x8D"
SYMBOL_COPY = b"\xEF\x83\x85"
SYMBOL_CUT = b"\xEF\x83\x84"
SYMBOL_DIRECTORY = b"\xEF\x81\xBB"
SYMBOL_DOWN = b"\xEF\x81\xB8"
SYMBOL_DOWNLOAD = b"\xEF\x80\x99"
SYMBOL_DRIVE = b"\xEF\x80\x9C"
SYMBOL_DUMMY = b"\xEF\xA3\xBF"
SYMBOL_EDIT = b"\xEF\x8C\x84"
SYMBOL_EJECT = b"\xEF\x81\x92"
SYMBOL_ENVELOPE = b"\xEF\x83\xA0"
SYMBOL_EYE_CLOSE = b"\xEF\x81\xB0"
SYMBOL_EYE_OPEN = b"\xEF\x81\xAE"
SYMBOL_FILE = b"\xEF\x85\x9B"
SYMBOL_GPS = b"\xEF\x84\xA4"
SYMBOL_HOME = b"\xEF\x80\x95"
SYMBOL_IMAGE = b"\xEF\x80\xBE"
SYMBOL_KEYBOARD = b"\xEF\x84\x9C"
SYMBOL_LEFT = b"\xEF\x81\x93"
SYMBOL_LOOP = b"\xEF\x81\xB9"
SYMBOL_LIST = b"\xEF\x80\x8B"
SYMBOL_MINUS = b"\xEF\x81\xA8"
SYMBOL_MUTE = b"\xEF\x80\xA6"
SYMBOL_NEW_LINE = b"\xEF\xA2\xA2"
SYMBOL_NEXT = b"\xEF\x81\x91"
SYMBOL_OK = b"\xEF\x80\x8C"
SYMBOL_PASTE = b"\xEF\x83\xAA"
SYMBOL_PAUSE = b"\xEF\x81\x8C"
SYMBOL_PLAY = b"\xEF\x81\x8B"
SYMBOL_PLUS = b"\xEF\x81\xA7"
SYMBOL_POWER = b"\xEF\x80\x91"
SYMBOL_PREV = b"\xEF\x81\x88"
SYMBOL_REFRESH = b"\xEF\x80\xA1"
SYMBOL_RIGHT = b"\xEF\x81\x94"
SYMBOL_SAVE = b"\xEF\x83\x87"
SYMBOL_SD_CARD = b"\xEF\x9F\x82"
SYMBOL_SETTINGS = b"\xEF\x80\x93"
SYMBOL_SHUFFLE = b"\xEF\x81\xB4"
SYMBOL_STOP = b"\xEF\x81\x8D"
SYMBOL_TINT = b"\xEF\x81\x83"
SYMBOL_TRASH = b"\xEF\x8B\xAD"
SYMBOL_UP = b"\xEF\x81\xB7"
SYMBOL_UPLOAD = b"\xEF\x82\x93"
SYMBOL_USB = b"\xEF\x8a\x87"
SYMBOL_VIDEO = b"\xEF\x80\x88"
SYMBOL_VOLUME_MAX = b"\xEF\x80\xA8"
SYMBOL_VOLUME_MID = b"\xEF\x80\xA7"
SYMBOL_WARNING = b"\xEF\x81\xB1"
SYMBOL_WIFI = b"\xEF\x87\xAB"


_PyCPointerType = type(_POINTER(_ctypes.c_uint8))
_CArgObject = type(_ctypes.byref(_ctypes.c_uint8()))
_PyCArrayType = type((_ctypes.c_uint8 * 1))
_PyCSimpleType = type(_ctypes.c_uint8)
_PyCFuncPtrType = type(_ctypes.CFUNCTYPE(None))
_PyCStructType = type(_ctypes.Structure)


class __PyObjectStore(object):
    __objects__ = {}
    __obj__ = None

    def __getitem__(self, item):
        if self.__obj__ is not None:
            value = self.__obj__[item]
            return value

        raise TypeError('this is not an array so it cannot be indexed')

    @classmethod
    def as_array(cls, size):
        return cls * size

    @property
    def __address__(self):
        return _ctypes.addressof(self)

    @classmethod
    def __weakref_remove__(cls, ref):
        for key, value in list(cls.__objects__[cls].items()):
            if value == ref:
                del cls.__objects__[cls][key]
                return

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls not in cls.__objects__:
            cls.__objects__[cls] = {}

        if '__object__' in kwargs:
            obj = kwargs.pop('__object__')

            try:
                address = _ctypes.addressof(obj)

                if address not in cls.__objects__[cls]:
                    cls.__objects__[cls][address] = (
                        weakref.ref(obj, cls.__weakref_remove__)
                    )

                return cls.__objects__[cls][address]()
            except:
                pass

        obj = super().__new__(cls, *args, **kwargs)
        address = obj.__address__
        cls.__objects__[cls][address] = weakref.ref(obj, cls.__weakref_remove__)
        return obj


# This is here for the purposes of type hinting. Any returned values from
# a function or from a structure field that is of an "int" type or a "float"
# type will be returned as a python int or float. the typed return values are
# simply to know exactly what kind of an int is being returned so a user is
# able to act accordingly and no go out of bounds if modifying it and passing
# it to a function that takes the same type. If that does get done it would
# cause undefined behavior.
class __IntMixin(object):
    value = None
    _c_obj = None

    def __format__(self, format_spec):
        return int.__format__(self.value, format_spec)

    def __neg__(self):
        value = self.value
        self.value = -value
        return self

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
                _POINTER(self.__class__ * x)
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
        if not isinstance(x, (int, float, type(self))):
            return False

        val1 = self.value

        if isinstance(x, (int, float)):
            return x == val1

        val2 = x.value
        return val2 == val1

    def __ne__(self, x):
        if not isinstance(x, (int, float, type(self))):
            return False

        val1 = self.value

        if isinstance(x, (int, float)):
            return x != val1

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


# ***************  primitives  ***************
['~primitives~']  # NOQA
# ********************************************


class mem_pool_t(void_t):  # NOQA
    pass


class _Structure(_ctypes.Structure, __PyObjectStore):

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls not in cls.__objects__:
            cls.__objects__[cls] = {}

        if '__object__' in kwargs:
            obj = kwargs.pop('__object__')

            if type(type(obj)) == _PyCPointerType:
                try:
                    obj = obj.contents
                except ValueError:
                    pass
            try:
                address = _ctypes.addressof(obj)

                print(cls.__name__, address)
                if address not in cls.__objects__[cls]:
                    cls.__objects__[cls][address] = (
                        weakref.ref(obj, cls.__weakref_remove__)
                    )

                return cls.__objects__[cls][address]()
            except:
                pass

        obj = super().__new__(cls, *args, **kwargs)
        address = obj.__address__
        cls.__objects__[cls][address] = weakref.ref(obj, cls.__weakref_remove__)
        return obj

    def __hash__(self):
        return hash(_ctypes.addressof(self))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _ctypes.Structure.__setattr__(self, '__references__', {})

    def __convert_to_ctype__(self, obj, type_):
        if isinstance(obj, list):
            ref_obj = tuple(obj)
        else:
            ref_obj = obj

        if ref_obj in self.__references__:
            return self.__references__[ref_obj]

        pointer_count = _pointer_count(type_)
        type_ = _strip_pointer(type_)

        if isinstance(obj, (list, tuple)):
            if not pointer_count:
                raise TypeError('this field is not for an array')

            if pointer_count == 2:
                second_dim = 0
                for item in obj:
                    if isinstance(item, (list, tuple)):
                        second_dim = max(len(item), second_dim)
                    else:
                        break

                if second_dim:
                    array = ((type_ * second_dim) * len(obj))()
                    for i, item1 in enumerate(obj):
                        for j, item2 in enumerate(item1):
                            array[i][j] = item2

                else:
                    array = type_ * len(obj)
                    array = array(*obj)
            else:
                array = type_ * len(obj)
                array = array()
                for i, item in enumerate(obj):
                    array[i] = item

            self.__references__[ref_obj] = array
            return array

        if type_ == void_t:
            void_t.from_address()
            pass

        if type(type_) == _PyCArrayType:
            value = type_(*obj)  # NOQA

        if isinstance(obj, str):
            new_obj = obj.encode('utf-8')

            if pointer_count:
                if new_obj.endswith(b'\x00'):
                    new_obj += b'\x00'

                array = type_ * len(new_obj)
                value = array.from_buffer_copy(new_obj, 0)

            elif type_ == void_t:
                value = type_.from_buffer_copy(new_obj[0])
            else:
                value = type_(new_obj[0])

            self.__references__[obj] = value
            return value

        if isinstance(obj, bytes) and pointer_count:
            if type_ == void_t:
                value = void_t.from_buffer_copy(obj, 0)
            else:
                value = (type_ * len(obj))(*obj)

            self.__references__[obj] = value
            return value

        if isinstance(obj, bytearray) and pointer_count:
            if type_ == void_t:
                value = void_t.from_buffer(obj)
            else:
                type_ = type_ * len(obj)
                value = type_.from_buffer(obj)

            self.__references__[obj] = value
            return value

        if type_ == void_t:
            try:
                value = void_t.from_address(_ctypes.addressof(obj))
            except:
                try:
                    value = void_t.from_address(value)
                except:
                    raise TypeError

            self.__references__[obj] = value
            return value

        if pointer_count:
            try:
                value = _pointer(obj)
            except:
                value = _pointer(type_(obj))

            self.__references__[obj] = value
            return value

        if (
            type(type_) == _PyCSimpleType and
            type(type(obj)) == _PyCSimpleType and
            not isinstance(obj, type_)
        ):
            try:
                value = obj.value
                self.__references__[obj] = value
                return value
            except AttributeError:
                pass

        return obj

    def __setattr__(self, key, value):
        convert_to_ctype = (
            _ctypes.Structure.__getattribute__(self, '__convert_to_ctype__')
        )

        try:
            if value not in self.__references__:
                pass
        except TypeError:
            print(type(value))
        print('FIELD_STOP:')
        fields = _ctypes.Structure.__getattribute__(self, '_fields_')
        for field in fields:
            if len(field) == 2:
                field_name, field_type = field
            else:
                field_name, field_type = field[:-1]

            if field_name != key:
                continue

            if field_name == 'stops':
                print('FIELD_STOP:', field_type)

        if isinstance(value, (list, tuple)) or value not in self.__references__:
            fields = _ctypes.Structure.__getattribute__(self, '_fields_')
            for field in fields:
                if len(field) == 2:
                    field_name, field_type = field
                else:
                    field_name, field_type = field[:-1]

                if field_name != key:
                    continue

                if field_name == 'stops':
                    print('FIELD_STOP:', field_type)

                if inspect.isfunction(value) or inspect.ismethod(value):
                    cb_func = field_type(value)
                    self.__references__[value] = cb_func
                    value = cb_func
                else:
                    value = convert_to_ctype(value, field_type)
                break

        _ctypes.Structure.__setattr__(self, key, value)

    def __getattribute__(self, item):
        try:
            references = (
                _ctypes.Structure.__getattribute__(self, '__references__')
            )
        except AttributeError:
            _ctypes.Structure.__setattr__(self, '__references__', {})
            references = (
                _ctypes.Structure.__getattribute__(self, '__references__')
            )

        obj = _ctypes.Structure.__getattribute__(self, item)

        if item.startswith('__') and item.endswith('__'):
            return obj

        for k, v in references.items():
            if v == obj:
                return k

        fields = _ctypes.Structure.__getattribute__(self, '_fields_')

        for field in fields:
            if len(field) == 2:
                field_name, field_type = field
            else:
                field_name, field_type = field[:-1]

            if item != field_name:
                continue

            print('test:', obj, field_type)
            return _convert_to_py_type(obj, field_type)

        return obj


class _Union(_ctypes.Union, __PyObjectStore):

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
                    value = _pointer(value)
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


class _lru_item_t(_Structure):
    pass


lru_item_t = _lru_item_t


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
# _lib_lvgl.lv_switch_create.argtypes = CArgList(parent=_POINTER(_obj_t))
# _lib_lvgl.lv_switch_create.restype = _POINTER(_obj_t)

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

    return new_obj


def _pointer_count(obj):
    count = 0
    while type(obj) == _PyCPointerType:
        count += 1
        if type(obj._type_) == _PyCStructType:  # NOQA
            return count

        obj = obj._type_  # NOQA
    return count


def _convert_to_py_type(obj, type_=None, pointer_count=None):
    if pointer_count:
        if type_ == void_t:
            return obj

        print(obj, type_)
        tmp_obj = type_(__object__=obj)
        setattr(tmp_obj, '__obj__', obj)
        return tmp_obj

    try:
        return obj.value
    except:
        pass

    try:
        obj = type(obj)(__object__=obj)
    except:
        pass

    return obj


def _convert_to_ctype(obj, type_):
    if obj is None:
        return None

    p_count = _pointer_count(type_)
    type_ = _strip_pointer(type_)

    if isinstance(obj, bytearray):
        type_ = type_ * len(obj)
        return type_.from_buffer(obj)

    if isinstance(obj, str):
        obj = obj.encode('utf-8')

        if not obj.endswith(b'\x00'):
            obj += b'\x00'

        type_ = type_ * len(obj)
        return type_(*obj)

    if isinstance(obj, bytes):
        type_ = type_ * len(obj)
        return type_(*obj)

    if isinstance(obj, (list, tuple)):
        type_ = type_ * len(obj)
        return type_(*obj)

    if not isinstance(obj, type_):
        if isinstance(obj, (_Structure, _Union)):
            if (p_count and type_ == void_t) or type_ == void_t:
                return _ctypes.byref(obj)

            pointer = _ctypes.cast(_pointer(obj), _POINTER(type_))
            if p_count:
                return pointer

            return pointer.contents

        if p_count:
            try:
                obj = type_(obj)
            except:
                obj = _ctypes.cast(_pointer(obj), _POINTER(type_)).contents

            return _ctypes.byref(obj)

    if p_count:
        return _ctypes.byref(obj)

    try:
        return obj.value
    except:
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

            print(cls._func_, args)
            args = list(args)
            py_args = []
            for i, arg in enumerate(args):
                argtype = cls._argtypes_[i]

                if argtype == void_t and isinstance(arg, void_t) and arg:  # NOQA
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


lru_free_t = CFUNCTYPE(None, void_t)  # NOQA


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

        count = 0
        chars = ''

        while True:
            char = path[count].value

            if char == b'\x00':
                break

            chars += char.decode('utf-8')
            count += 1

        path = chars

        print(repr(path))

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

        print('__fs_read_cb', fs_file, num_bytes_to_read, num_bytes_read)

        fileno = fs_file

        if fileno in self.__open_files:
            cont = self.__open_files[fileno]
            try:
                data = cont['file'].read(num_bytes_to_read)

                if not isinstance(data, bytes):
                    data = data.decode('utf-8')

                _ctypes.memmove(buf, data, len(data))

                output = bytearray(len(data))
                tmp = _ctypes.cast(buf, _POINTER(uint8_t * len(data))).contents
                for i in range(len(data)):
                    output[i] = tmp[i].value
                print(output)


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


spinbox_set_pos = spinbox_set_cursor_pos  # NOQA

STYLE_CONST_PROPS_END = {
    'prop_ptr': style_const_prop_id_inv,  # NOQA
    'value': {'num': 0}
}


def STYLE_CONST_BORDER_COLOR(val):
    return {
        'prop_ptr': _style_const_prop_id_BORDER_COLOR,  # NOQA
        'value': {'color': val}
    }


def OPA_MIX3(a1, a2, a3):
    return (int32_t(a1).value * a2 * a3) >> 16  # NOQA


def STYLE_CONST_ARC_ROUNDED(val):
    return {
        'prop_ptr': _style_const_prop_id_ARC_ROUNDED,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_HEIGHT(val):
    return {
        'prop_ptr': _style_const_prop_id_HEIGHT,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_TEXT_LETTER_SPACE(val):
    return {
        'prop_ptr': _style_const_prop_id_TEXT_LETTER_SPACE,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def _DPX_CALC(dpi, n):
    if n == 0:
        return 0
    return MAX(((dpi * n + 80) / 160), 1)


def ANIM_SET_EASE_IN_CUBIC(a):
    return _PARA(a, 0.32, 0, 0.67, 0)


def SMAX_OF(t):
    return ((0x1 << ((_ctypes.sizeof(t) * 8) - 1)) - 1) | (
                0x7 << ((_ctypes.sizeof(t) * 8) - 4))


def COORD_IS_SPEC(x):
    return _COORD_TYPE(x) == _COORD_TYPE_SPEC


def CANVAS_BUF_SIZE_TRUE_COLOR_CHROMA_KEYED(w, h):
    return IMG_BUF_SIZE_TRUE_COLOR_CHROMA_KEYED(w, h)


def STYLE_CONST_GRID_ROW_DSC_ARRAY(val):
    return {
        'prop_ptr': STYLE_GRID_ROW_DSC_ARRAY,  # NOQA
        'value': {'ptr': _ctypes.cast(_pointer(val), void_t)}  # NOQA
    }


def STYLE_CONST_OUTLINE_WIDTH(val):
    return {
        'prop_ptr': _style_const_prop_id_OUTLINE_WIDTH,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def ANIM_SET_EASE_IN_OUT_BACK(a):
    return _PARA(a, 0.68, - 0.6, 0.32, 1.6)


def _LL_READ(list, i):  # NOQA
    i = _ll_get_head(list)  # NOQA

    while i is not None:
        i = _ll_get_next(list, i)  # NOQA


def _CONCAT(x, y):
    return x + y


def STYLE_CONST_BG_IMG_OPA(val):
    return {
        'prop_ptr': _style_const_prop_id_BG_IMG_OPA,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def IS_SIGNED(t):
    return t(-1).value < t(0).value


def STYLE_CONST_BG_GRAD(val):
    return {'prop_ptr': _style_const_prop_id_BG_GRAD, 'value': {'ptr': val}}  # NOQA


def ANIM_SET_EASE_OUT_CUBIC(a):
    return _PARA(a, 0.33, 1, 0.68, 1)


def STYLE_CONST_MAX_WIDTH(val):
    return {
        'prop_ptr': _style_const_prop_id_MAX_WIDTH,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_ANIM_TIME(val):
    return {
        'prop_ptr': _style_const_prop_id_ANIM_TIME,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def ANIM_SET_EASE_IN_OUT_CUBIC(a):
    return _PARA(a, 0.65, 0, 0.35, 1)


def UDIV255(x):
    return (x * 0x8081) >> 0x17


def STYLE_CONST_BORDER_POST(val):
    return {
        'prop_ptr': _style_const_prop_id_BORDER_POST,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_TRANSFORM_WIDTH(val):
    return {
        'prop_ptr': _style_const_prop_id_TRANSFORM_WIDTH,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_ANIM(val):
    return {'prop_ptr': _style_const_prop_id_ANIM, 'value': {'ptr': val}}  # NOQA


def STYLE_CONST_BG_DITHER_MODE(val):
    return {
        'prop_ptr': _style_const_prop_id_BG_DITHER_MODE,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_SHADOW_SPREAD(val):
    return {
        'prop_ptr': _style_const_prop_id_SHADOW_SPREAD,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_MARGIN_BOTTOM(val):
    return {
        'prop_ptr': _style_const_prop_id_MARGIN_BOTTOM,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_TEXT_FONT(val):
    return {'prop_ptr': _style_const_prop_id_TEXT_FONT, 'value': {'ptr': val}}  # NOQA


def MAX3(a, b, c):
    return MAX(MAX(a, b), c)


def STYLE_CONST_SHADOW_OPA(val):
    return {
        'prop_ptr': _style_const_prop_id_SHADOW_OPA,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def CANVAS_BUF_SIZE_INDEXED_8BIT(w, h):
    return IMG_BUF_SIZE_INDEXED_8BIT(w, h)


def STYLE_CONST_PAD_ROW(val):
    return {
        'prop_ptr': _style_const_prop_id_PAD_ROW,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_PAD_COLUMN(val):
    return {
        'prop_ptr': _style_const_prop_id_PAD_COLUMN,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def _CONCAT3(x, y, z):
    return x + y + z


def STYLE_CONST_BORDER_WIDTH(val):
    return {
        'prop_ptr': _style_const_prop_id_BORDER_WIDTH,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def DPX(n):
    return _DPX_CALC(disp_get_dpi(None), n)  # NOQA


def STYLE_CONST_GRID_Y_ALIGN(val):
    return {'prop_ptr': STYLE_GRID_Y_ALIGN, 'value': {'num': grid_align_t(val)}}  # NOQA


def STYLE_CONST_MARGIN_TOP(val):
    return {
        'prop_ptr': _style_const_prop_id_MARGIN_TOP,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_TRANSITION(val):
    return {'prop_ptr': _style_const_prop_id_TRANSITION, 'value': {'ptr': val}}  # NOQA


def STYLE_CONST_BG_COLOR(val):
    return {'prop_ptr': _style_const_prop_id_BG_COLOR, 'value': {'color': val}}  # NOQA


def STYLE_CONST_BG_IMG_RECOLOR(val):
    return {
        'prop_ptr': _style_const_prop_id_BG_IMG_RECOLOR,  # NOQA
        'value': {'color': val}
    }


def CANVAS_BUF_SIZE_TRUE_COLOR(w, h):
    return IMG_BUF_SIZE_TRUE_COLOR(w, h)


def STYLE_CONST_LINE_COLOR(val):
    return {
        'prop_ptr': _style_const_prop_id_LINE_COLOR,  # NOQA
        'value': {'color': val}
    }


def IMG_BUF_SIZE_ALPHA_4BIT(w, h):
    return ((w + 1) // 2) * h


def CANVAS_BUF_SIZE_INDEXED_2BIT(w, h):
    return IMG_BUF_SIZE_INDEXED_2BIT(w, h)


def STYLE_CONST_TRANSFORM_PIVOT_X(val):
    return {
        'prop_ptr': _style_const_prop_id_TRANSFORM_PIVOT_X,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def BEZIER_VAL_FLOAT(f):
    return int32_t(f * BEZIER_VAL_MAX)  # NOQA


def COLOR_FORMAT_IS_INDEXED(cf):
    return COLOR_FORMAT_I1 <= cf <= COLOR_FORMAT_I8  # NOQA


def CANVAS_BUF_SIZE_ALPHA_4BIT(w, h):
    return IMG_BUF_SIZE_ALPHA_4BIT(w, h)


def HOR_RES():
    return disp_get_hor_res(disp_get_default())  # NOQA


def STYLE_CONST_LAYOUT(val):
    return {
        'prop_ptr': _style_const_prop_id_LAYOUT,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_BG_IMG_TILED(val):
    return {
        'prop_ptr': _style_const_prop_id_BG_IMG_TILED,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def _COORD_TYPE(x):
    return x & _COORD_TYPE_MASK


def STYLE_CONST_ALIGN(val):
    return {
        'prop_ptr': _style_const_prop_id_ALIGN,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def CANVAS_BUF_SIZE_ALPHA_2BIT(w, h):
    return IMG_BUF_SIZE_ALPHA_2BIT(w, h)


def STYLE_CONST_IMG_RECOLOR(val):
    return {
        'prop_ptr': _style_const_prop_id_IMG_RECOLOR,  # NOQA
        'value': {'color': val}
    }


def STYLE_CONST_GRID_COLUMN_ALIGN(val):
    return {
        'prop_ptr': STYLE_GRID_COLUMN_ALIGN,  # NOQA
        'value': {'num': grid_align_t(val)}  # NOQA
    }


def STYLE_CONST_FLEX_CROSS_PLACE(val):
    return {
        'prop_ptr': STYLE_FLEX_CROSS_PLACE,  # NOQA
        'value': {'num': flex_flow_t(val)}  # NOQA
    }


def CANVAS_BUF_SIZE_ALPHA_8BIT(w, h):
    return IMG_BUF_SIZE_ALPHA_8BIT(w, h)


def STYLE_CONST_GRID_ROW_ALIGN(val):
    return {
        'prop_ptr': STYLE_GRID_ROW_ALIGN,  # NOQA
        'value': {'num': grid_align_t(val)}  # NOQA
    }


def STYLE_CONST_GRID_CELL_COLUMN_SPAN(val):
    return {
        'prop_ptr': STYLE_GRID_CELL_COLUMN_SPAN,  # NOQA
        'value': {'num': coord_t(val)}  # NOQA
    }


def IMG_BUF_SIZE_INDEXED_4BIT(w, h):
    return IMG_BUF_SIZE_ALPHA_4BIT(w, h) + 4 * 16


def STYLE_CONST_SHADOW_COLOR(val):
    return {
        'prop_ptr': _style_const_prop_id_SHADOW_COLOR,  # NOQA
        'value': {'color': val}
    }


def _PARA(a, x1, y1, x2, y2):
    a.parameter.bezier3 = _anim_bezier3_para_t(  # NOQA
        BEZIER_VAL_FLOAT(x1),
        BEZIER_VAL_FLOAT(y1),
        BEZIER_VAL_FLOAT(x2),
        BEZIER_VAL_FLOAT(y2)
    )
    return a


def ANIM_SET_EASE_OUT_CIRC(a):
    return _PARA(a, 0, 0.55, 0.45, 1)


def STYLE_CONST_IMG_OPA(val):
    return {
        'prop_ptr': _style_const_prop_id_IMG_OPA,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def ANIM_SET_EASE_IN_OUT_SINE(a):
    return _PARA(a, 0.37, 0, 0.63, 1)


def UMAX_OF(t):
    return (
        ((0x1 << ((_ctypes.sizeof(t) * 8) - 1)) - 1) |
        (0xF << ((_ctypes.sizeof(t) * 8) - 4))
    )


def STYLE_CONST_OUTLINE_COLOR(val):
    return {
        'prop_ptr': _style_const_prop_id_OUTLINE_COLOR,  # NOQA
        'value': {'color': val}
    }


def OPA_MIX2(a1, a2):
    return (int32_t(a1).value * a2) >> 8  # NOQA


def STYLE_CONST_BG_OPA(val):
    return {
        'prop_ptr': _style_const_prop_id_BG_OPA,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_TEXT_COLOR(val):
    return {
        'prop_ptr': _style_const_prop_id_TEXT_COLOR,  # NOQA
        'value': {'color': val}
    }


def STYLE_CONST_TRANSFORM_ZOOM(val):
    return {
        'prop_ptr': _style_const_prop_id_TRANSFORM_ZOOM,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_ARC_WIDTH(val):
    return {
        'prop_ptr': _style_const_prop_id_ARC_WIDTH,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def ANIM_SET_EASE_OUT_EXPO(a):
    return _PARA(a, 0.16, 1, 0.3, 1)


def STYLE_CONST_MIN_HEIGHT(val):
    return {
        'prop_ptr': _style_const_prop_id_MIN_HEIGHT,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_SHADOW_WIDTH(val):
    return {
        'prop_ptr': _style_const_prop_id_SHADOW_WIDTH,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_RADIUS(val):
    return {
        'prop_ptr': _style_const_prop_id_RADIUS,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def IMG_BUF_SIZE_ALPHA_2BIT(w, h):
    return ((w + 3) // 4) * h


def STYLE_CONST_TRANSLATE_X(val):
    return {
        'prop_ptr': _style_const_prop_id_TRANSLATE_X,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_TEXT_ALIGN(val):
    return {
        'prop_ptr': _style_const_prop_id_TEXT_ALIGN,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def ANIM_SET_EASE_IN_QUINT(a):
    return _PARA(a, 0.64, 0, 0.78, 0)


def STYLE_CONST_TRANSFORM_ANGLE(val):
    return {
        'prop_ptr': _style_const_prop_id_TRANSFORM_ANGLE,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_TEXT_OPA(val):
    return {
        'prop_ptr': _style_const_prop_id_TEXT_OPA,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_BG_IMG_SRC(val):
    return {'prop_ptr': _style_const_prop_id_BG_IMG_SRC, 'value': {'ptr': val}}  # NOQA


def STYLE_CONST_TRANSFORM_HEIGHT(val):
    return {
        'prop_ptr': _style_const_prop_id_TRANSFORM_HEIGHT,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def ANIM_SET_EASE_IN_BACK(a):
    return _PARA(a, 0.36, 0, 0.66, -0.56)


def STYLE_CONST_PAD_TOP(val):
    return {
        'prop_ptr': _style_const_prop_id_PAD_TOP,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def CANVAS_BUF_SIZE_ALPHA_1BIT(w, h):
    return IMG_BUF_SIZE_ALPHA_1BIT(w, h)


def PCT(x):
    if x < 0:
        return COORD_SET_SPEC(1000 - x)
    return COORD_SET_SPEC(x)


def STYLE_CONST_ARC_OPA(val):
    return {
        'prop_ptr': _style_const_prop_id_ARC_OPA,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_LINE_OPA(val):
    return {
        'prop_ptr': _style_const_prop_id_LINE_OPA,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def CANVAS_BUF_SIZE_INDEXED_1BIT(w, h):
    return IMG_BUF_SIZE_INDEXED_1BIT(w, h)


def CLAMP(min, val, max):  # NOQA
    return MAX(min, MIN(val, max))


def STYLE_CONST_ARC_IMG_SRC(val):
    return {'prop_ptr': _style_const_prop_id_ARC_IMG_SRC, 'value': {'ptr': val}}  # NOQA


def STYLE_CONST_PAD_RIGHT(val):
    return {
        'prop_ptr': _style_const_prop_id_PAD_RIGHT,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def ANIM_SET_EASE_IN_OUT_QUAD(a):
    return _PARA(a, 0.45, 0, 0.55, 1)


def STYLE_CONST_LINE_ROUNDED(val):
    return {
        'prop_ptr': _style_const_prop_id_LINE_ROUNDED,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def _LL_READ_BACK(list, i):  # NOQA
    i = _ll_get_tail(list)  # NOQA

    while i is not None:
        i = _ll_get_prev(list, i)  # NOQA


def VERSION_CHECK(x, y, z):
    return (
        x == LVGL_VERSION_MAJOR and
        (
            y < LVGL_VERSION_MINOR or
            (y == LVGL_VERSION_MINOR and z <= LVGL_VERSION_PATCH)
        )
    )


def kill_dependency(y):
    return y


def STYLE_CONST_X(val):
    return {'prop_ptr': _style_const_prop_id_X, 'value': {'num': int32_t(val)}}  # NOQA


def IMG_BUF_SIZE_INDEXED_2BIT(w, h):
    return IMG_BUF_SIZE_ALPHA_2BIT(w, h) + 4 * 4


def ANIM_SET_EASE_IN_EXPO(a):
    return _PARA(a, 0.7, 0, 0.84, 0)


def ANIM_SET_EASE_IN_OUT_QUINT(a):
    return _PARA(a, 0.83, 0, 0.17, 1)


def STYLE_CONST_CLIP_CORNER(val):
    return {
        'prop_ptr': _style_const_prop_id_CLIP_CORNER,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def CONCAT(x, y):
    return _CONCAT(x, y)


def STYLE_CONST_BORDER_OPA(val):
    return {
        'prop_ptr': _style_const_prop_id_BORDER_OPA,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_GRID_X_ALIGN(val):
    return {'prop_ptr': STYLE_GRID_X_ALIGN, 'value': {'num': grid_align_t(val)}}  # NOQA


def CANVAS_BUF_SIZE_INDEXED_4BIT(w, h):
    return IMG_BUF_SIZE_INDEXED_4BIT(w, h)


def VER_RES():
    return disp_get_ver_res(disp_get_default())  # NOQA


def MAX4(a, b, c, d):
    return MAX(MAX(a, b), MAX(c, d))


def STYLE_CONST_TRANSFORM_PIVOT_Y(val):
    return {
        'prop_ptr': _style_const_prop_id_TRANSFORM_PIVOT_Y,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def IMG_BUF_SIZE_TRUE_COLOR_CHROMA_KEYED(w, h):
    return (COLOR_DEPTH // 8) * w * h


def STYLE_CONST_BG_IMG_RECOLOR_OPA(val):
    return {
        'prop_ptr': _style_const_prop_id_BG_IMG_RECOLOR_OPA,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def IMG_BUF_SIZE_ALPHA_8BIT(w, h):
    return w * h


def IMG_BUF_SIZE_ALPHA_1BIT(w, h):
    return ((w + 7) // 8) * h


def STYLE_CONST_MIN_WIDTH(val):
    return {
        'prop_ptr': _style_const_prop_id_MIN_WIDTH,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def COORD_IS_PCT(x):
    return COORD_IS_SPEC(x) and _COORD_PLAIN(x) <= 2000


def ANIM_SET_EASE_IN_QUART(a):
    return _PARA(a, 0.5, 0, 0.75, 0)


def STYLE_CONST_WIDTH(val):
    return {
        'prop_ptr': _style_const_prop_id_WIDTH,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_BG_GRAD_COLOR(val):
    return {
        'prop_ptr': _style_const_prop_id_BG_GRAD_COLOR,  # NOQA
        'value': {'color': val}
    }


def IMG_BUF_SIZE_INDEXED_1BIT(w, h):
    return IMG_BUF_SIZE_ALPHA_1BIT(w, h) + 4 * 2


def STYLE_CONST_LINE_DASH_WIDTH(val):
    return {
        'prop_ptr': _style_const_prop_id_LINE_DASH_WIDTH,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def ANIM_SET_EASE_OUT_BACK(a):
    return _PARA(a, 0.34, 1.56, 0.64, 1)


def STYLE_CONST_BORDER_SIDE(val):
    return {
        'prop_ptr': _style_const_prop_id_BORDER_SIDE,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def MIN(a, b):
    if a < b:
        return a
    return b


def ANIM_SET_EASE_OUT_QUINT(a):
    return _PARA(a, 0.22, 1, 0.36, 1)


def STYLE_CONST_TEXT_LINE_SPACE(val):
    return {
        'prop_ptr': _style_const_prop_id_TEXT_LINE_SPACE,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_BG_MAIN_STOP(val):
    return {
        'prop_ptr': _style_const_prop_id_BG_MAIN_STOP,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_Y(val):
    return {'prop_ptr': _style_const_prop_id_Y, 'value': {'num': int32_t(val)}}  # NOQA


def MAX(a, b):
    if a > b:
        return a
    return b


def CONCAT3(x, y, z):
    return _CONCAT3(x, y, z)


def STYLE_CONST_TRANSLATE_Y(val):
    return {
        'prop_ptr': _style_const_prop_id_TRANSLATE_Y,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def ANIM_SET_EASE_IN_QUAD(a):
    return _PARA(a, 0.11, 0, 0.5, 0)


def STYLE_CONST_BLEND_MODE(val):
    return {
        'prop_ptr': _style_const_prop_id_BLEND_MODE,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_MARGIN_LEFT(val):
    return {
        'prop_ptr': _style_const_prop_id_MARGIN_LEFT,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def IMG_BUF_SIZE_INDEXED_8BIT(w, h):
    return IMG_BUF_SIZE_ALPHA_8BIT(w, h) + 4 * 256


def STYLE_CONST_ANIM_SPEED(val):
    return {
        'prop_ptr': _style_const_prop_id_ANIM_SPEED,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_GRID_COLUMN_DSC_ARRAY(val):
    return {
        'prop_ptr': STYLE_GRID_COLUMN_DSC_ARRAY,  # NOQA
        'value': {'ptr': _ctypes.cast(_pointer(val), void_t)}  # NOQA
    }


def COORD_GET_PCT(x):
    if _COORD_PLAIN(x) > 1000:
        return 1000 - _COORD_PLAIN(x)
    return _COORD_PLAIN(x)


def ANIM_SET_EASE_IN_SINE(a):
    return _PARA(a, 0.12, 0, 0.39, 0)


def GRID_FR(x):
    return COORD_MAX - 100 + x


def STYLE_CONST_BG_GRAD_DIR(val):
    return {
        'prop_ptr': _style_const_prop_id_BG_GRAD_DIR,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def IMG_BUF_SIZE_TRUE_COLOR(w, h):
    return (COLOR_DEPTH // 8) * w * h


def STYLE_CONST_SHADOW_OFS_Y(val):
    return {
        'prop_ptr': _style_const_prop_id_SHADOW_OFS_Y,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_ARC_COLOR(val):
    return {'prop_ptr': _style_const_prop_id_ARC_COLOR, 'value': {'color': val}}  # NOQA


def STYLE_CONST_SHADOW_OFS_X(val):
    return {
        'prop_ptr': _style_const_prop_id_SHADOW_OFS_X,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def COORD_SET_SPEC(x):
    return x | _COORD_TYPE_SPEC


def STYLE_CONST_GRID_CELL_ROW_POS(val):
    return {'prop_ptr': STYLE_GRID_CELL_ROW_POS, 'value': {'num': coord_t(val)}}  # NOQA


def STYLE_CONST_LINE_DASH_GAP(val):
    return {
        'prop_ptr': _style_const_prop_id_LINE_DASH_GAP,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def ANIM_SET_EASE_IN_OUT_CIRC(a):
    return _PARA(a, 0.85, 0, 0.15, 1)


def STYLE_CONST_GRID_CELL_COLUMN_POS(val):
    return {
        'prop_ptr': STYLE_GRID_CELL_COLUMN_POS,  # NOQA
        'value': {'num': coord_t(val)}  # NOQA
    }


def STYLE_CONST_BASE_DIR(val):
    return {
        'prop_ptr': _style_const_prop_id_BASE_DIR,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def ANIM_SET_EASE_IN_OUT_QUART(a):
    return _PARA(a, 0.76, 0, 0.24, 1)


def ANIM_SET_EASE_OUT_QUAD(a):
    return _PARA(a, 0.5, 1, 0.89, 1)


def MAX_OF(t):
    if IS_SIGNED(t):
        return SMAX_OF(t)

    return UMAX_OF(t)


def ANIM_SET_EASE_IN_CIRC(a):
    return _PARA(a, 0.55, 0, 1, 0.45)


def STYLE_CONST_COLOR_FILTER_OPA(val):
    return {
        'prop_ptr': _style_const_prop_id_COLOR_FILTER_OPA,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_OUTLINE_OPA(val):
    return {
        'prop_ptr': _style_const_prop_id_OUTLINE_OPA,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_FLEX_FLOW(val):
    return {'prop_ptr': STYLE_FLEX_FLOW, 'value': {'num': flex_flow_t(val)}}  # NOQA


def MIN3(a, b, c):
    return MIN(MIN(a, b), c)


def STYLE_CONST_MARGIN_RIGHT(val):
    return {
        'prop_ptr': _style_const_prop_id_MARGIN_RIGHT,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def IMG_BUF_SIZE_TRUE_COLOR_ALPHA(w, h):
    return _COLOR_NATIVE_WITH_ALPHA_SIZE * w * h


def COORD_IS_PX(x):
    return _COORD_TYPE(x) == _COORD_TYPE_PX or _COORD_TYPE(
        x
        ) == _COORD_TYPE_PX_NEG


def STYLE_CONST_IMG_RECOLOR_OPA(val):
    return {
        'prop_ptr': _style_const_prop_id_IMG_RECOLOR_OPA,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def COLOR_MAKE(r8, g8, b8):
    return b8, g8, r8


def _COORD_PLAIN(x):
    return x & ~_COORD_TYPE_MASK


def STYLE_CONST_FLEX_MAIN_PLACE(val):
    return {
        'prop_ptr': STYLE_FLEX_MAIN_PLACE,  # NOQA
        'value': {'num': flex_flow_t(val)}  # NOQA
    }


def STYLE_CONST_OUTLINE_PAD(val):
    return {
        'prop_ptr': _style_const_prop_id_OUTLINE_PAD,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def ANIM_SET_EASE_OUT_QUART(a):
    return _PARA(a, 0.25, 1, 0.5, 1)


def STYLE_CONST_PAD_BOTTOM(val):
    return {
        'prop_ptr': _style_const_prop_id_PAD_BOTTOM,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def ANIM_SET_EASE_IN_OUT_EXPO(a):
    return _PARA(a, 0.87, 0, 0.13, 1)


def MIN4(a, b, c, d):
    return MIN(MIN(a, b), MIN(c, d))


def STYLE_CONST_GRID_CELL_ROW_SPAN(val):
    return {'prop_ptr': STYLE_GRID_CELL_ROWSPAN, 'value': {'num': coord_t(val)}}  # NOQA


def STYLE_CONST_LINE_WIDTH(val):
    return {
        'prop_ptr': _style_const_prop_id_LINE_WIDTH,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_BG_GRAD_STOP(val):
    return {
        'prop_ptr': _style_const_prop_id_BG_GRAD_STOP,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def ABS(x):
    if x > 0:
        return x
    return -x


def STYLE_CONST_MAX_HEIGHT(val):
    return {
        'prop_ptr': _style_const_prop_id_MAX_HEIGHT,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_COLOR_FILTER_DSC(val):
    return {
        'prop_ptr': _style_const_prop_id_COLOR_FILTER_DSC,  # NOQA
        'value': {'ptr': val}
    }


def STYLE_PROP_ID_MASK(prop):
    return style_prop_t(prop & ~STYLE_PROP_META_MASK)  # NOQA


def STYLE_CONST_OPA(val):
    return {
        'prop_ptr': _style_const_prop_id_OPA,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def CANVAS_BUF_SIZE_TRUE_COLOR_ALPHA(w, h):
    return IMG_BUF_SIZE_TRUE_COLOR_ALPHA(w, h)


def STYLE_CONST_PAD_LEFT(val):
    return {
        'prop_ptr': _style_const_prop_id_PAD_LEFT,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


def STYLE_CONST_FLEX_TRACK_PLACE(val):
    return {
        'prop_ptr': STYLE_FLEX_TRACK_PLACE,  # NOQA
        'value': {'num': flex_flow_t(val)}  # NOQA
    }


def ANIM_SET_EASE_OUT_SINE(a):
    return _PARA(a, 0.61, 1, 0.88, 1)


def STYLE_CONST_TEXT_DECOR(val):
    return {
        'prop_ptr': _style_const_prop_id_TEXT_DECOR,  # NOQA
        'value': {'num': int32_t(val)}  # NOQA
    }


KEYBOARD_CTRL_BTN_FLAGS = (
    BTNMATRIX_CTRL_NO_REPEAT |  # NOQA
    BTNMATRIX_CTRL_CLICK_TRIG |   # NOQA
    BTNMATRIX_CTRL_CHECKED  # NOQA
)

INDEV_STATE_PR = INDEV_STATE_PRESSED  # NOQA
INDEV_STATE_REL = INDEV_STATE_RELEASED  # NOQA

BIDI_BASE_DIR_DEF = BASE_DIR_AUTO  # NOQA
FONT_DEFAULT = font_montserrat_14  # NOQA

COLOR_CHROMA_KEY = color_hex(0x00ff00)  # NOQA

OBJ_FLAG_SNAPABLE = OBJ_FLAG_SNAPPABLE  # NOQA
OBJ_FLAG_FLEX_IN_NEW_TRACK = OBJ_FLAG_LAYOUT_1  # NOQA