from typing import Union, Any, Callable, Optional, List  # NOQA

from . import __lib_lvgl as _lib_lvgl  # NOQA


__version__ = "0.1.1b"


def binding_version():
    return __version__


def _get_py_obj(c_obj, c_type):
    if c_type == 'None':
        return None

    if c_obj == _lib_lvgl.ffi.NULL:
        return None

    if not isinstance(c_obj, (int, float, str, bytes)):
        type_ = _lib_lvgl.ffi.typeof(c_obj)

        while type_.kind == 'pointer':
            type_ = type_.item

        if type_.kind == 'array':
            # not used at the moment, need to find a way to test it
            size = type_.length  # NOQA

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

    if c_type + '_' in glob:
        cls = glob[c_type + '_']
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
        except Exception:  # NOQA
            return c_obj

    try:
        _ = c_obj[0]

        cls = type(c_type, (_Array,), {'_c_type': c_type})
        array = cls()
        array._obj = c_obj  # NOQA
        return array
    except Exception:  # NOQA
        pass

    return c_obj


def _get_c_obj(py_obj, c_type):
    if isinstance(py_obj, dict):
        return py_obj

    if py_obj is None:
        return _lib_lvgl.ffi.NULL

    if hasattr(py_obj, '_obj'):
        return py_obj._obj  # NOQA

    if c_type is not None:
        globs = globals()

        if c_type.startswith('List'):
            c_type = c_type.split('[')[-1][:-1]
            cls = type(f'{c_type}[]', (_Array,), {'_c_type': c_type})
            instance = cls()

            type_cls = globs[c_type]

            for i, item in enumerate(py_obj):
                if hasattr(item, '_obj'):
                    continue

                item_inst = (
                    type_cls(**item) if isinstance(item, dict)
                    else type_cls(item)
                )
                py_obj[i] = item_inst

            instance.extend(py_obj)

            return instance._obj  # NOQA

        def _instance(_c_type):
            c = globs[_c_type]

            try:
                if isinstance(py_obj, dict):
                    ins = c(**py_obj)
                else:
                    ins = c(py_obj)

                return ins._obj  # NOQA
            except Exception:  # NOQA
                pass


        if c_type in globs:
            obj = _instance(c_type)
            if obj is not None:
                return obj

        if f'{c_type}_' in globs:
            obj = _instance(f'{c_type}_')
            if obj is not None:
                return obj

    if isinstance(py_obj, (int, float)):
        return py_obj
    if isinstance(py_obj, str):
        return py_obj.encode('utf-8')

    if isinstance(py_obj, tuple):
        py_obj = list(py_obj)

    return [py_obj] if isinstance(py_obj, list) else py_obj


def _get_c_type(c_obj):
    if isinstance(c_obj, int):
        return None

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


class _AsArrayMixin:
    _c_type = ''

    @classmethod
    def as_array(cls, size=None):
        new_cls = type(
            cls.__name__ + ('[]' if size is None else f'[{size}]'),
            (_Array,),
            {'_c_type': cls._c_type.split(' ')[0]}
        )

        return new_cls()


class _Array(list):
    _c_type = ''

    def as_buffer(self, c_type, size=None):
        if size is None:
            cast = _lib_lvgl.ffi.cast(f'{c_type}[]', self._obj)
        else:
            cast = _lib_lvgl.ffi.cast(f'{c_type}[{size}]', self._obj)
        return _lib_lvgl.ffi.buffer(cast)[:]

    @property
    def _obj(self):
        if self.__obj is None:
            c_array = []
            dim = self._dim

            for item in self._array:

                c_obj = _get_c_obj(item, self._c_type)
                py_obj = _get_py_obj(c_obj, self._c_type)
                c_array.append(py_obj.as_dict())
                if isinstance(item, _Array):
                    dim += item._dim

            if '[' in self.__class__.__name__:
                size = self.__class__.__name__.split('[')[-1]
                size = size.split(']')[0]

                if not size:
                    size = str(len(c_array))

                if size and size.isdigit():
                    dim = dim.split(']', 1)[-1]

                    dim = '[{0}]'.format(size) + dim

                    if c_array:
                        try:
                            self.__obj = _lib_lvgl.ffi.new(
                                self._c_type + dim,
                                c_array
                            )
                        except _lib_lvgl.ffi.error:
                            self.__obj = _lib_lvgl.ffi.new(
                                f'lv_{self._c_type}{dim}',
                                c_array
                            )
                    else:
                        self.__obj = _lib_lvgl.ffi.new(
                            self._c_type + dim
                        )
                    return self.__obj

            c_type = self._c_type + dim

            try:
                self.__obj = _lib_lvgl.ffi.new(
                    c_type,
                    [c_array]
                )
            except _lib_lvgl.ffi.error:
                self.__obj = _lib_lvgl.ffi.new(f'lv_{c_type}', [c_array])

        return self.__obj

    @_obj.setter
    def _obj(self, c_obj):
        size = _lib_lvgl.ffi.typeof(c_obj).length
        array = []

        dim = ''

        for i in range(size):
            c_item = c_obj[i]
            py_item = _get_py_obj(c_item, self._c_type)

            if py_item is None:
                break

            if isinstance(py_item, _Array) and not dim:
                dim += py_item._dim

            array.append(py_item)

        self.__class__.__name__ = '{0}[{1}]{2}'.format(self._c_type, size, dim)

        self._array = array
        self.__obj = c_obj

    @property
    def _dim(self):
        size = len(self)
        return '[]' if size == 0 else '[{0}]'.format(size)

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

        cls = type(f'{self._c_type}[]', (_Array,), {'_c_type': self._c_type})
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

    def as_dict(self):
        return [item.as_dict() for item in self]

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

    def _instance(_c_type):
        c = glob[_c_type]
        c = type(
            c_type,
            (c,),
            {'_obj': obj, '_c_type': f'{c_type} *'}
        )

        try:
            return c()
        except Exception:  # NOQA
            ins = c()
            ins._obj = obj
            return ins

    if c_type in glob:
        return _instance(c_type)

    if f'{c_type}_' in glob:
        return _instance(f'{c_type}_')

    if isinstance(obj, bool):
        if c_type != 'bool':
            raise TypeError(
                f'incompatible types "bool" and "{c_type}"'
            )

        cls = type(
            c_type,
            (_Bool,),
            {'_obj': obj, '_c_type': f'{c_type} *'}
        )
        return cls(obj)

    if isinstance(obj, float):
        for item in ('double', 'float'):
            if c_type.startswith(item):
                cls = type(
                    c_type,
                    (_Float,),
                    {'_obj': obj, '_c_type': f'{c_type} *'}
                )
                return cls(obj)

        raise TypeError(
            f'incompatible types "float" and "{c_type}"'
        )

    if isinstance(obj, bytes) and c_type == 'char':
        obj = obj.decode('utf-8')

    if isinstance(obj, str):
        if c_type != 'char':
            raise TypeError(
                f'incompatible types "str" and "{c_type}"'
            )

        cls = type(
            c_type,
            (_String,),
            {'_obj': obj, '_c_type': f'{c_type} *'}
        )

        return cls(obj)

    raise TypeError(f'Unknown type ("{c_type}")')


class _Float(float, _AsArrayMixin):
    _c_type = 'float *'
    _obj = None

    def as_dict(self):
        return self._obj

    def __new__(cls, value):
        instance = super().__new__(cls, value)
        instance._obj = value
        return instance


class _Integer(int, _AsArrayMixin):
    _obj = None

    def as_dict(self):
        return self._obj

    def __new__(cls, value):
        instance = super().__new__(cls, value)
        instance._obj = value
        return instance


class _String(str, _AsArrayMixin):
    _obj = None

    def as_dict(self):
        return self._obj

    def __new__(cls, value):
        instance = super().__new__(cls, value)
        instance._obj = value.encode('utf-8')
        return instance


class _Bool(int, _AsArrayMixin):
    _c_type = 'bool *'
    _obj = None

    def as_dict(self):
        return self._obj

    def __new__(cls, value):
        instance = super().__new__(cls, value)
        instance._obj = value
        return instance


class void(_AsArrayMixin):
    _c_type = 'void *'

    def as_dict(self):
        return self._obj

    def __init__(self, value):
        try:
            self._obj = _lib_lvgl.ffi.cast(self._c_type, value)
            self.ctype = _get_c_type(value)

        except Exception:  # NOQA
            c_obj = _get_c_obj(value, None)

            try:
                self._obj = _lib_lvgl.ffi.cast(self._c_type, c_obj)
                self.ctype = _get_c_type(c_obj)
                value = c_obj
            except Exception:  # NOQA
                self._obj = value

        self.__original__object__ = value

    def __str__(self):
        return f'(void *) ({self.ctype})'


class char(_String):
    _c_type = 'char *'


class uint8_t(_Integer):
    _c_type = 'uint8_t *'

    @classmethod
    def from_buffer(cls, data):
        return _lib_lvgl.ffi.from_buffer(cls._c_type.split(' ')[0] + '[]', data)

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



# This class checks to see if wrapper classes are being used by
# the mpy module. The reason why this meta class exists is so that objects
# comming from C code get redirected to those wrapper classes instead of to
# the C API classes. If the redirection does not occur then the methods in
# the wraapper classes would not be accessable.
class _StructUnionMeta(type):
    _wrapped_classes = {}
    _classes = {}

    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)

        if '.mpy.' in str(bases[0]) or f'lvgl.{name}' in str(bases[0]):
            nme = f'{name}_t' if not name.endswith('_t') else name
            if nme not in _StructUnionMeta._wrapped_classes:
                _StructUnionMeta._wrapped_classes[nme] = cls

    def __call__(cls, *args, **kwargs):
        name = cls.__name__

        if name in _StructUnionMeta._wrapped_classes:
            cls = _StructUnionMeta._wrapped_classes[name]  # NOQA

        elif name.startswith('_'):
            if name[1:] in _StructUnionMeta._wrapped_classes:
                cls = _StructUnionMeta._wrapped_classes[name[1:]]  # NOQA

        # elif name.endswith('_t') and name[:-2] in _StructUnionMeta._wrapped_classes:
        #     cls = _StructUnionMeta._wrapped_classes[name[:-2]]

        try:
            return super(_StructUnionMeta, cls).__call__(*args, **kwargs)
        except TypeError:
            return super(_StructUnionMeta, cls).__call__(_DefaultArg)


class _StructUnion(_AsArrayMixin, metaclass=_StructUnionMeta):
    _c_type = ''

    @classmethod
    def sizeof(cls):
        return _lib_lvgl.ffi.sizeof(cls._c_type)

    def cast(self, obj):
        obj._obj = self._obj

    def as_buffer(self, c_type, size=None):
        if size is None:
            cast = _lib_lvgl.ffi.cast(f'{c_type}[]', self._obj)
        else:
            cast = _lib_lvgl.ffi.cast(f'{c_type}[{size}]', self._obj)
        return _lib_lvgl.ffi.buffer(cast)[:]

    def __init__(self, **kwargs):
        self._obj = _lib_lvgl.ffi.new(self._c_type)

        for key, value in list(kwargs.items())[:]:
            if value == _DefaultArg:
                continue

            attr = getattr(self._obj, key)
            c_type = _get_c_type(attr)
            self._set_field(key, value, c_type)

    def _get_field(self, field_name, c_type):
        key = '__py_{0}__'.format(field_name)
        if key in self.__dict__:
            obj = self.__dict__[key]
            if isinstance(obj, (_StructUnion, _Array)):
                return obj

        py_obj = _get_py_obj(getattr(self._obj, field_name), c_type)

        self.__dict__[key] = py_obj
        return py_obj

    def _set_field(self, field_name, py_obj, c_type):
        def _setattr():
            setattr(self._obj, field_name, c_obj)
            self.__dict__['__py_{0}__'.format(field_name)] = py_obj
            self.__dict__['__c_{0}__'.format(field_name)] = c_obj


        if isinstance(py_obj, list):
            c_obj = [item.as_dict() for item in py_obj]
            _setattr()
            return

        c_obj = _get_c_obj(py_obj, c_type)
        if isinstance(c_obj, bytes):
            c_obj = _lib_lvgl.ffi.from_buffer(
                c_type.split(' ')[0] + f'[{len(c_obj)}]', bytearray(c_obj)
            )

        _setattr()

    def as_dict(self):
        res = {}
        for field in dir(self._obj):
            attr = getattr(self, field)
            res[field] = attr.as_dict()

        return res

_PY_C_TYPES = (_Float, _Integer, _String, _StructUnion)
_global_cb_store = _CBStore()
