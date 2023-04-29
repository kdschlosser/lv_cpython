# This module overrides the python import system so that we are able to
# manipulate hoiw things are accessed in LVGL. so a user  should be able to do
# the following

import os
import sys

try:
    import _lib_lvgl
except ImportError:
    base_path = os.path.dirname(__file__)
    lvgl_path = os.path.join(base_path, 'lvgl')

    sys.path.insert(0, lvgl_path)

    import _lib_lvgl


class _Function(object):

    def __init__(self, func):
        self.__func = func

    def __call__(self, *args):
        args = list(args)

        for i, arg in enumerate(args):
            if isinstance(arg, str):
                arg = arg.encode('utf-8')
                args[i] = arg

            elif isinstance(arg, _StructWrapper):
                args[i] = arg._obj

            elif isinstance(arg, (list, tuple)):
                array = []
                struct_initilizer = None

                for item in arg:
                    if isinstance(item, str):
                        item = item.encode('utf-8')
                    elif isinstance(item, _StructWrapper):
                        if struct_initilizer is None:
                            struct_initilizer = (
                                item._initilizer.replace(
                                    item.__name__,
                                    item.__name__ + '[]'
                                )
                            )

                        item = item._obj

                    array.append(item)

                if struct_initilizer is not None:
                    array = _lib_lvgl.ffi.new(struct_initilizer, array)

                args[i] = array

        res = self.__func(*args)
        if isinstance(res, bytes):
            return res.decode('utf-8')

        if isinstance(res, (int, float)):
            return res

        cdata = str(res)

        if cdata.count('*') > 1:
            count = 0
            array = []
            while True:
                obj = res[count]
                if obj == _lib_lvgl.ffi.NULL:
                    break

                if isinstance(obj, bytes):
                    obj = obj.decode('utf-8')
                elif isinstance(obj, (int, float)):
                    pass

                elif 'cdata' in str(obj):
                    name = ''

                    for item in str(obj).split(' '):
                        if '*' in item:
                            break
                        name = item

                    cls = type(name, (_StructWrapper,), {'_obj': obj})
                    obj = cls()

                array.append(obj)
                count += 1

            return array

        if 'cdata' in cdata:
            name = ''

            for item in cdata.split(' '):
                if '*' in item:
                    break
                name = item

            cls = type(name, (_StructWrapper,), {'_obj': res})
            return cls()

        return res


class _StructWrapper(object):
    _initilizer = ''
    _obj = None

    def __init__(self, **kwargs):
        if self._obj is None:
            for k, v in list(kwargs.items())[:]:
                if isinstance(v, str):
                    v = v.encode('utf-8')
                    kwargs[k] = v

            if kwargs:
                self.__dict__['_obj'] = _lib_lvgl.ffi.new(self._initilizer, kwargs)
            else:
                self.__dict__['_obj'] = _lib_lvgl.ffi.new(self._initilizer)
        else:
            self.__dict__['_obj'] = self._obj

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        try:
            res = getattr(self._obj, item)
        except AttributeError:
            raise AttributeError(item)

        if isinstance(res, (int, float)):
            return res

        if isinstance(res, bytes):
            return res.decode('utf-8')

        cdata = str(res)

        if cdata.count('*') > 1:
            count = 0
            array = []
            store_locally = False
            while True:
                obj = res[count]
                if obj == _lib_lvgl.ffi.NULL:
                    break

                if isinstance(obj, bytes):
                    obj = obj.decode('utf-8')
                elif isinstance(obj, (int, float)):
                    pass

                elif 'cdata' in str(obj):
                    name = ''

                    for item in str(obj).split(' '):
                        if '*' in item:
                            break
                        name = item

                    cls = type(name, (_StructWrapper,), {'_obj': obj})
                    obj = cls()
                    store_locally = True

                array.append(obj)
                count += 1

            if store_locally:
                self.__dict__[item] = array

            return array

        if 'cdata' in cdata:
            name = ''

            for item in cdata.split(' '):
                if '*' in item:
                    break
                name = item

            cls = type(name, (_StructWrapper,), {'_obj': res})
            self.__dict__[item] = cls()
            return self.__dict__[item]

        return res

    def __setattr__(self, key, value):
        if isinstance(value, _StructWrapper):
            setattr(self._obj, key, value._obj)
            self.__dict__[key] = value

        elif isinstance(value, (list, tuple)):
            array = []
            store_locally = False

            for item in value:
                if isinstance(item, _StructWrapper):
                    array.append(item._obj)
                    store_locally = True
                elif isinstance(item, str):
                    item = item.encode('utf-8')
                    array.append(item)
                else:
                    array.append(value)

            setattr(self._obj, key, array)

            if store_locally:
                self.__dict__[key] = value

        elif isinstance(value, str):
            value = value.encode('utf-8')
            setattr(self._obj, key, value)
        else:
            setattr(self._obj, key, value)


class _StructFactory(object):

    def __init__(self, initilizer):
        self.name = ''

        for item in initilizer.split(' '):
            if '*' in item:
                break
            self.name = item

        self.__initilizer = initilizer

    def __call__(self, **kwargs):
        cls = type(
            self.name,
            (_StructWrapper,),
            {'_initilizer': self.__initilizer}
        )
        return cls(**kwargs)


class _lvgl(object):

    def __init__(self):
        mod = sys.modules[__name__]

        self.__name__ = mod.__name__
        self.__doc__ = mod.__doc__
        self.__package__ = mod.__package__
        self.__loader__ = mod.__loader__
        self.__spec__ = mod.__spec__
        self.__file__ = mod.__file__

        sys.modules[__name__] = self

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        if item.is_upper():
            if hasattr(_lib_lvgl.lib, 'LV_' + item):
                res = getattr(_lib_lvgl.lib, 'LV_' + item)
            else:
                raise AttributeError(item)

        elif hasattr(_lib_lvgl.lib, 'lv_' + item):
            res = _Function(getattr(_lib_lvgl.lib, 'lv_' + item))

        elif hasattr(_lib_lvgl.ffi, item):
            return getattr(_lib_lvgl.ffi, item)

        else:
            try:
                _lib_lvgl.ffi.new('lv_' + item + ' *')
            except:
                raise AttributeError(item)
            else:
                res = _StructFactory('lv_' + item + ' *')

        object.__setattr__(self, item, res)

        return res


__lvgl = _lvgl()
