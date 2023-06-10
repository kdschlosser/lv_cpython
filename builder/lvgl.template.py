from typing import Union, Any, Callable, Optional, List  # NOQA

try:
    import __lib_lvgl as _lib_lvgl  # NOQA
except ImportError:
    from . import __lib_lvgl as _lib_lvgl  # NOQA


__version__ = "0.1.1b"

_MPY = False


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
            self._dirty = True

            for item in self._array:
                if isinstance(item, _StructUnion):
                    c_array.append(item.as_dict())
                else:
                    c_array.append(_get_c_obj(item, self._c_type))

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
        self._dirty = False
        list.__init__(self)

    def __len__(self):
        self.__handle_dirty()
        return len(self._array)

    def __iter__(self):
        self.__handle_dirty()
        return iter(self._array)

    def __getitem__(self, item):
        self.__handle_dirty()
        return self._array[item]

    def __setitem__(self, key, value):
        self.__check_locked()

        self._array[key] = value

    def __handle_dirty(self):
        if self._dirty:
            obj = self._obj
            self.__obj = None
            self._obj = obj
            self._dirty = False

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

        self.__handle_dirty()

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
        self.__handle_dirty()
        return obj in self._array

    def __reversed__(self) -> "_Array":
        self.__check_locked()
        self._array.__reversed__()
        return self

    def __gt__(self, x: "_Array") -> bool:
        self.__handle_dirty()
        return self._array > x._array

    def __ge__(self, x: "_Array") -> bool:
        self.__handle_dirty()
        return self._array >= x._array

    def __lt__(self, x: "_Array") -> bool:
        self.__handle_dirty()
        return self._array < x._array

    def __le__(self, x: "_Array") -> bool:
        self.__handle_dirty()
        return self._array <= x._array

    def __eq__(self, other: "_Array") -> bool:
        self.__handle_dirty()
        return self._array == other._array

    def __ne__(self, other: "_Array") -> bool:
        self.__handle_dirty()
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

        self._array.append(py_obj)

    def as_dict(self):
        self.__handle_dirty()
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
# This class checks to see if wrapper classes are being used by
# the mpy module. The reason why this meta class exists is so that objects
# comming from C code get redirected to those wrapper classes instead of to
# the C API classes. If the redirection does not occur then the methods in
# the wraapper classes would not be accessable.
class _StructUnionMeta(type):
    _wrapped_classes = {}
    _classes = {}
    _calling_from_meta = False

    def __init__(cls, name, bases, dct):
        global _MPY

        super().__init__(name, bases, dct)

        if '.mpy.' in str(bases[0]) or f'lvgl.{name}' in str(bases[0]):
            _MPY = True

            if name not in _StructUnionMeta._wrapped_classes:
                _StructUnionMeta._wrapped_classes[name] = cls

    def __call__(cls, *args, **kwargs):
        name = cls.__name__

        if not _StructUnionMeta._calling_from_meta:
            if not cls.__module__.endswith('mpy'):
                if name.endswith('_t') and name[:-2] in _StructUnionMeta._wrapped_classes:
                    cls = _StructUnionMeta._wrapped_classes[name[:-2]]  # NOQA
                elif name.startswith('_') and name[1:] in _StructUnionMeta._wrapped_classes:
                    cls = _StructUnionMeta._wrapped_classes[name[1:]]  # NOQA
                elif name.startswith('_') and name.endswith('_t') and name[1:-2] in _StructUnionMeta._wrapped_classes:
                    cls = _StructUnionMeta._wrapped_classes[name[1:-2]]  # NOQA
                elif name in _StructUnionMeta._wrapped_classes:
                    cls = _StructUnionMeta._wrapped_classes[name]  # NOQA

        _StructUnionMeta._calling_from_meta = True
        try:
            instance = super(_StructUnionMeta, cls).__call__(*args, **kwargs)
        except TypeError:
            instance = super(_StructUnionMeta, cls).__call__(_DefaultArg)
        _StructUnionMeta._calling_from_meta = False
        return instance


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
            try:
                setattr(self._obj, field_name, c_obj)
            except TypeError:
                size = len(py_obj)
                cast = _lib_lvgl.ffi.cast(f'{c_type}[{size}]', c_obj)
                setattr(self._obj, field_name, cast)
            self.__dict__['__py_{0}__'.format(field_name)] = py_obj
            self.__dict__['__c_{0}__'.format(field_name)] = c_obj

        if isinstance(py_obj, _Array):
            c_type = c_type.split('[')[-1][:-1]
            c_obj = py_obj._obj  # NOQA
            _setattr()
            return

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


class __fs_driver(object):

    def __init__(self):
        import sys

        sys.modules['fs_driver'] = self
        self.__open_files = []

    def __fs_open_cb(self, _, path, mode):
        if mode == FS_MODE_WR:  # NOQA
            p_mode = 'wb'
        elif mode == FS_MODE_RD:  # NOQA
            p_mode = 'rb'
        elif mode == FS_MODE_WR | FS_MODE_RD:  # NOQA
            p_mode = 'rb+'
        else:
            raise RuntimeError(
                "fs_open_callback() - "
                "open mode error, {0} is invalid mode".format(mode)
            )

        try:
            f = open(path, p_mode)
        except OSError as e:
            raise RuntimeError(
                "fs_open_callback('{0}')".format(path)
            ) from e

        res = dict(file=f, path=path)
        handle = _lib_lvgl.ffi.new_handle(res)
        self.__open_files.append(handle)

        return handle

    def __fs_close_cb(self, _, fs_file):
        file_cont = _lib_lvgl.ffi.from_handle(fs_file)

        try:
            file_cont['file'].close()
        except OSError as e:
            raise RuntimeError(
                "fs_close_callback('{0}')".format(file_cont['path'])
            ) from e

        self.__open_files.remove(fs_file)

        return FS_RES_OK  # NOQA

    def __fs_read_cb(  # NOQA
            self,
        _,
        fs_file,
        buf,
        num_bytes_to_read,
        num_bytes_read
    ):
        file_cont = _lib_lvgl.ffi.from_handle(fs_file)

        try:
            data = file_cont['file'].read(num_bytes_to_read)
            num_bytes_read[0] = len(data)
            _lib_lvgl.ffi.buffer(buf)[:] = bytes(data)

        except OSError as e:
            raise RuntimeError(
                "fs_read_callback('{0}')".format(file_cont['path'])
            ) from e

        return FS_RES_OK  # NOQA

    def __fs_seek_cb(self, _, fs_file, pos, whence):  # NOQA
        file_cont = _lib_lvgl.ffi.from_handle(fs_file)

        try:
            file_cont['file'].seek(pos, whence)
        except OSError as e:
            raise RuntimeError(
                "fs_seek_callback('{0}')".format(file_cont['path'])
            ) from e

        return FS_RES_OK  # NOQA

    def __fs_tell_cb(self, _, fs_file, pos):  # NOQA
        file_cont = _lib_lvgl.ffi.from_handle(fs_file)

        try:
            tpos = file_cont['file'].tell()
            pos[0] = tpos
        except OSError as e:
            raise RuntimeError(
                "fs_tell_callback('{0}')".format(file_cont['path'])
            ) from e

        return FS_RES_OK  # NOQA

    def __fs_write_cb(self, _, fs_file, buf, btw, bw):  # NOQA
        file_cont = _lib_lvgl.ffi.from_handle(fs_file)

        try:
            num_bytes = file_cont['file'].write(buf[:btw])
            bw[0] = num_bytes
        except OSError as e:
            raise RuntimeError(
                "fs_write_callback('{0}')".format(file_cont['path'])
            ) from e

        return FS_RES_OK  # NOQA

    def fs_register(self, fs_drv, letter, cache_size=500):
        fs_drv.init()
        fs_drv.letter = ord(letter)
        fs_drv.open_cb = self.__fs_open_cb
        fs_drv.read_cb = self.__fs_read_cb
        fs_drv.write_cb = self.__fs_write_cb
        fs_drv.seek_cb = self.__fs_seek_cb
        fs_drv.tell_cb = self.__fs_tell_cb
        fs_drv.close_cb = self.__fs_close_cb

        if cache_size >= 0:
            fs_drv.cache_size = cache_size

        fs_drv.register()


__fs_driver()


# This next code block overrides the default imnport machinery in Python
# This allows me to inject a non existant module into the import system.
# the "dynamic" module being injected is the display_driver module that runs
# the code to create the SDL window, mouse and keyboard drivers

__SDL_DISPLAY = None

import sys
import os

from importlib.abc import (
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
            with open(self.filename) as f:
                data = f.read()
        else:
            if globals()['__SDL_DISPLAY'] is None:
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
