try:
    import _lib_lvgl  # NOQA
except ImportError:
    import sys

    sys.path.insert(0, 'build')

    import _lib_lvgl  # NOQA

from typing import Union, Any, Callable, Optional, List  # NOQA


def _get_py_obj(c_obj, c_type):
    if c_type == 'None':
        return None

    if c_obj == _lib_lvgl.ffi.NULL:
        return None

    if c_type.lower().startswith('list'):
        c_type = c_type.split('[')[-1][:-1]
        cls = type(c_type + '[]', (_Array,), {'_c_obj': c_type})
        instance = cls()
        instance._obj = c_obj

        return instance

    glob = globals()

    if c_type in glob:
        cls = glob[c_type]
        if issubclass(cls, _StructUnion):
            instance = cls()
            instance._obj = c_obj  # NOQA
            return instance

        cls = type(c_type, (cls,), {'_obj': c_obj, '_c_type': c_type + ' *'})
        res = cls(c_obj)

        return res

    if isinstance(c_obj, bool):
        return _convert_basic_type(c_obj, c_type)

    if isinstance(c_obj, (int, float)):
        return _convert_basic_type(c_obj, c_type)

    if isinstance(c_obj, bytes) and c_type == 'char':
        return _convert_basic_type(c_obj, c_type)

    if c_type is None:
        try:
            c_type = _get_c_type(c_obj)
        except:  # NOQA
            return c_obj

    try:
        _ = c_obj[0]

        cls = type(c_type, (_Array,), {'_c_type': c_type})
        array = cls()
        array._obj = c_obj  # NOQA
        return array
    except:  # NOQA
        pass

    return c_obj


def _get_c_obj(py_obj):
    if py_obj is None:
        return _lib_lvgl.ffi.NULL

    try:
        return py_obj._obj  # NOQA
    except AttributeError:
        pass

    if isinstance(py_obj, (int, float)):
        return py_obj
    if isinstance(py_obj, str):
        return py_obj.encode('utf-8')

    if isinstance(py_obj, tuple):
        py_obj = list(py_obj)

    if isinstance(py_obj, list):
        return [py_obj]

    return py_obj


def _get_c_type(c_obj):
    cdata = str(_lib_lvgl.ffi.typeof(c_obj)).replace("'", '')
    c_type = ''

    for itm in cdata.split(' '):
        if '*' in itm:
            break

        c_type = itm

    c_type = c_type.replace('>', '')

    return c_type.replace('struct', '').replace('union', '').strip()


class _CBStore(dict):
    pass


class va_list(list):
    pass


class _DefaultArg:
    pass


class _Array(list):
    _c_type = ''

    def as_buffer(self, c_type, size=None):
        if size is None:
            cast = _lib_lvgl.ffi.cast(c_type + '[]', self._obj)
        else:
            cast = _lib_lvgl.ffi.cast(c_type + '[{}]'.format(size), self._obj)
        return _lib_lvgl.ffi.buffer(cast)[:]

    @property
    def _obj(self):
        if self.__obj is None:
            c_array = []
            dim = self._dim

            for item in self._array:
                c_array.append(_get_c_obj(item))
                if isinstance(item, _Array):
                    dim += item._dim

            if '[' in self.__class__.__name__:
                size = self.__class__.__name__.split('[')[-1]
                size = size.split(']')[0]
                if size and size.isdigit():
                    dim = dim.split(']', 1)[-1]
                    dim = '[{0}]'.format(size) + dim

                    if c_array:
                        self.__obj = _lib_lvgl.ffi.new(
                            self._c_type + dim,
                            [c_array]
                        )
                    else:
                        self.__obj = _lib_lvgl.ffi.new(
                            self._c_type + dim
                        )
                    return self.__obj

            c_type = self._c_type + dim
            self.__obj = _lib_lvgl.ffi.new(
                c_type,
                [c_array]
            )

        return self.__obj

    @_obj.setter
    def _obj(self, c_obj):
        array = []

        count = 0
        dim = ''

        while True:
            c_item = c_obj[count]
            py_item = _get_py_obj(c_item, self._c_type)

            if py_item is None:
                break

            if isinstance(py_item, _Array) and not dim:
                dim += py_item._dim

            array.append(py_item)
            count += 1

        self.__class__.__name__ = '{0}[{1}]{2}'.format(self._c_type, count, dim)

        self._array = array
        self.__obj = c_obj

    @property
    def _dim(self):
        size = len(self)
        if size == 0:
            return '[]'
        else:
            return '[{0}]'.format(size)

    def __init__(self):
        self.__obj = None
        self._array = []
        list.__init__(self)

    def __len__(self):
        return len(self._array)

    def __iter__(self):
        return iter(self._array)

    def __getitem__(self, item):
        return self._array[item]

    def __setitem__(self, key, value):
        self.__check_locked()

        self._array[key] = value

    @property
    def is_locked(self):
        return self.__obj is not None

    def __check_locked(self):
        if self.__obj is not None:
            raise RuntimeError(
                'This array "{0}" has been recieved from LVGL or '
                'sent to LVGL and has been locked\n'
                'you can make copy using `array.copy()` '
                'to add/change/remove items from the array.'.format(
                    self.__class__.__name__
                )
            )

    def add_dimension(self) -> "_Array":
        self.__check_locked()

        cls = type(self._c_type + '[]', (_Array,), {'_c_type': self._c_type})
        instance = cls()
        self._array.append(instance)
        return instance

    def clear(self) -> None:
        self.__check_locked()
        self._array.clear()

    def copy(self) -> "_Array":
        """
        This is a shallow copy
        """
        cls = type(
            self.__class__.__name__,
            (_Array,),
            {'_c_type': self._c_type}
        )

        instance = cls()

        if self.__class__.__name__.count('[') > 1:
            for item in self._array:
                instance.append(item.copy())

        else:
            instance._array = list(self)[:]

        return instance

    def pop(self, index: int = 0) -> Any:
        self.__check_locked()

        return self._array.pop(index)

    def index(
            self,
            value: Any,
            start: Optional[int] = None,
            stop: Optional[int] = None
    ) -> int:
        if None not in (start, stop):
            return self._array.index(value, start, stop)

        if start is not None:
            return self._array.index(value, start)

        return self._array.index(value)

    def count(self, obj: Any) -> int:
        return self._array.count(obj)

    def insert(self, index: int, obj: Any) -> None:
        self.__check_locked()

        self._array.insert(index, obj)

    def remove(self, value: Any) -> None:
        self.__check_locked()

        self._array.remove(value)

    def reverse(self) -> None:
        self.__check_locked()

        self._array.reverse()

    def sort(
            self,
            *,
            key: Optional[Callable[[Any], Any]] = None,
            reverse: Optional[bool] = False
    ) -> None:
        self.__check_locked()

        if key is not None:
            self._array.sort(key=key, reverse=reverse)

        self._array.sort(reverse=reverse)

    def __delitem__(self, i: Union[int, slice]) -> None:
        self.__check_locked()

        del self._array[i]

    def __add__(self, x: Union["_Array", list]) -> "_Array":
        instance = self.copy()

        for item in x:
            instance.append(item)

        return instance

    def __iadd__(self, x: Union["_Array", list]) -> "_Array":
        self.__check_locked()

        for item in x:
            self.append(item)

        return self

    def __mul__(self, n: int) -> "_Array":
        instance = self.copy()

        instance._array = instance._array * n
        return instance

    def __rmul__(self, n: int) -> "_Array":
        return self.__mul__(n)

    def __imul__(self, n: int) -> "_Array":
        self.__check_locked()
        self._array *= n
        return self

    def __contains__(self, obj: Any) -> bool:
        return obj in self._array

    def __reversed__(self) -> "_Array":
        self.__check_locked()
        self._array.__reversed__()
        return self

    def __gt__(self, x: "_Array") -> bool:
        return self._array > x._array

    def __ge__(self, x: "_Array") -> bool:
        return self._array >= x._array

    def __lt__(self, x: "_Array") -> bool:
        return self._array < x._array

    def __le__(self, x: "_Array") -> bool:
        return self._array <= x._array

    def __eq__(self, other: "_Array") -> bool:
        return self._array == other._array

    def __ne__(self, other: "_Array") -> bool:
        return not self.__eq__(other)

    def extend(self, obj: Union[list, "_Array"]) -> None:
        self.__check_locked()

        for item in obj:
            self.append(item)

    def append(self, py_obj: Any) -> None:
        self.__check_locked()

        if isinstance(py_obj, tuple):
            py_obj = list(py_obj)

        if isinstance(py_obj, list) and not isinstance(py_obj, _Array):
            if self._array and not isinstance(self._array[0], _Array):
                raise TypeError(
                    'You cannot add an array to a single dimension array.'
                )

            dim = self.add_dimension()
            for item in py_obj:
                if isinstance(item, _Array) and item.is_locked:
                    item = item.copy()

                dim.append(item)

            return
        try:
            if self._c_type in (
            py_obj._c_type, py_obj.__class__.__name__):  # NOQA
                self._array.append(py_obj)
                return

        except AttributeError:
            if isinstance(py_obj, (int, str, float, bytes, bool)):
                py_type = _convert_basic_type(py_obj, self._c_type)
                self._array.append(py_type)

    def __str__(self):
        return str(self._array)

    def __repr__(self):
        return repr(self._array)


def _convert_basic_type(obj, c_type):
    try:
        if c_type in (obj._c_type, obj.__class__.__name__):  # NOQA
            return obj
        else:
            raise TypeError('incompatable type')
    except AttributeError:
        pass

    glob = globals()

    if c_type in glob:
        cls = glob[c_type]
        cls = type(
            c_type,
            (cls,),
            {'_obj': obj, '_c_type': c_type + ' *'}
        )
        try:
            instance = cls(obj)
            return instance
        except:  # NOQA
            instance = cls()
            instance._obj = obj
            return instance

    if isinstance(obj, bool):
        if c_type != 'bool':
            raise TypeError(
                'incompatible types "bool" and "{0}"'.format(c_type)
            )
        cls = type(
            c_type,
            (_Bool,),
            {'_c_type': c_type + ' *', '_obj': obj}
            )
        return cls(obj)

    if isinstance(obj, float):
        for item in ('double', 'float'):
            if c_type.startswith(item):
                cls = type(
                    c_type,
                    (_Float,),
                    {'_c_type': c_type + ' *', '_obj': obj}
                )
                return cls(obj)

        raise TypeError(
            'incompatible types "float" and "{0}"'.format(c_type)
        )

    if isinstance(obj, bytes) and c_type == 'char':
        obj = obj.decode('utf-8')

    if isinstance(obj, str):
        if c_type != 'char':
            raise TypeError(
                'incompatible types "str" and "{0}"'.format(c_type)
            )

        cls = type(
            c_type,
            (_String,),
            {'_c_type': c_type + ' *', '_obj': obj}
        )

        return cls(obj)

    raise TypeError('Unknown type ("{0}")'.format(c_type))


class _Float(float):
    _c_type = 'float *'
    _obj = None

    def __new__(cls, value):
        instance = super().__new__(cls, value)
        instance._obj = value
        return instance

    @classmethod
    def as_array(cls, size=None):
        if size is not None:
            new_cls = type(
                cls.__name__ + '[{}]'.format(size),
                (_Array,),
                {'_c_type': cls._c_type.split(' ')[0]}

            )
        else:
            new_cls = type(
                cls.__name__ + '[]',
                (_Array,),
                {'_c_type': cls._c_type.split(' ')[0]}

            )

        return new_cls()


class _Integer(int):
    _c_type = ''
    _obj = None

    def __new__(cls, value):
        instance = super().__new__(cls, value)
        instance._obj = value
        return instance

    @classmethod
    def as_array(cls, size=None):
        if size is not None:
            new_cls = type(
                cls.__name__ + '[{}]'.format(size),
                (_Array,),
                {'_c_type': cls._c_type.split(' ')[0]}

            )
        else:
            new_cls = type(
                cls.__name__ + '[]',
                (_Array,),
                {'_c_type': cls._c_type.split(' ')[0]}

            )

        return new_cls()


class _String(str):
    _c_type = ''
    _obj = None

    def __new__(cls, value):
        instance = super().__new__(cls, value)
        instance._obj = value.encode('utf-8')
        return instance

    @classmethod
    def as_array(cls, size=None):
        if size is not None:
            new_cls = type(
                cls.__name__ + '[{}]'.format(size),
                (_Array,),
                {'_c_type': cls._c_type.split(' ')[0]}

            )
        else:
            new_cls = type(
                cls.__name__ + '[]',
                (_Array,),
                {'_c_type': cls._c_type.split(' ')[0]}

            )

        return new_cls()


class _Bool(int):
    _c_type = 'bool *'
    _obj = None

    def __new__(cls, value):
        instance = super().__new__(cls, value)
        instance._obj = value
        return instance

    @classmethod
    def as_array(cls, size=None):
        if size is not None:
            new_cls = type(
                cls.__name__ + '[{}]'.format(size),
                (_Array,),
                {'_c_type': cls._c_type.split(' ')[0]}

            )
        else:
            new_cls = type(
                cls.__name__ + '[]',
                (_Array,),
                {'_c_type': cls._c_type.split(' ')[0]}

            )

        return new_cls()


class void(object):
    _c_type = 'void *'

    def __init__(self, value):
        try:
            self._obj = _lib_lvgl.ffi.cast(self._c_type, value)
            self.ctype = _get_c_type(value)

        except:  # NOQA
            c_obj = _get_c_obj(value)

            try:
                self._obj = _lib_lvgl.ffi.cast(self._c_type, c_obj)
                self.ctype = _get_c_type(c_obj)
                value = c_obj
            except:  # NOQA
                self._obj = value

        self.__original__object__ = value

    def __str__(self):
        return '(void *) ({})'.format(self.ctype)

    @classmethod
    def as_array(cls, size=None):
        if size is not None:
            new_cls = type(
                cls.__name__ + '[{}]'.format(size),
                (_Array,),
                {'_c_type': cls._c_type.split(' ')[0]}

            )
        else:
            new_cls = type(
                cls.__name__ + '[]',
                (_Array,),
                {'_c_type': cls._c_type.split(' ')[0]}

            )

        return new_cls()


class char(_String):
    _c_type = 'char *'


class uint8_t(_Integer):
    _c_type = 'uint8_t *'


class uint16_t(_Integer):
    _c_type = 'uint16_t *'


class uint32_t(_Integer):
    _c_type = 'uint32_t *'


class uint64_t(_Integer):
    _c_type = 'uint64_t *'


class int8_t(_Integer):
    _c_type = 'int8_t *'


class int16_t(_Integer):
    _c_type = 'int16_t *'


class int32_t(_Integer):
    _c_type = 'int32_t *'


class int64_t(_Integer):
    _c_type = 'int64_t *'


class int_(_Integer):
    _c_type = 'int *'


class uintptr_t(_Integer):
    _c_type = 'unsigned int *'


class intptr_t(_Integer):
    _c_type = 'signed int *'


class size_t(_Integer):
    _c_type = 'size_t *'


class _StructUnion(object):
    _c_type = ''

    def as_buffer(self, c_type, size=None):
        if size is None:
            cast = _lib_lvgl.ffi.cast(c_type + '[]', self._obj)
        else:
            cast = _lib_lvgl.ffi.cast(c_type + '[{}]'.format(size), self._obj)
        return _lib_lvgl.ffi.buffer(cast)[:]

    @classmethod
    def as_array(cls, size=None):
        if size is not None:
            new_cls = type(
                cls.__name__ + '[{}]'.format(size),
                (_Array,),
                {'_c_type': cls._c_type.split(' ')[0]}

            )
        else:
            new_cls = type(
                cls.__name__ + '[]',
                (_Array,),
                {'_c_type': cls._c_type.split(' ')[0]}

            )

        return new_cls()

    def __init__(self, **kwargs):
        self._obj = _lib_lvgl.ffi.new(self._c_type)

        for key, value in list(kwargs.items())[:]:
            if value == _DefaultArg:
                continue

            self._set_field(key, value)

    def _get_field(self, field_name, c_type):
        key = '__py_{0}__'.format(field_name)
        if key in self.__dict__:
            return self.__dict__[key]

        py_obj = _get_py_obj(getattr(self._obj, field_name), c_type)

        self.__dict__[key] = py_obj
        return py_obj

    def _set_field(self, field_name, py_obj):
        c_obj = _get_c_obj(py_obj)
        setattr(self._obj, field_name, c_obj)
        self.__dict__['__py_{0}__'.format(field_name)] = py_obj
        self.__dict__['__c_{0}__'.format(field_name)] = c_obj


_PY_C_TYPES = (_Float, _Integer, _String, _StructUnion)
_global_cb_store = _CBStore()
