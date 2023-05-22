# -*- coding: utf-8 -*-

import os
import sys
from pycparser import c_generator

from . import utils


generator = c_generator.CGenerator()


def get_py_type(name):
    if not name:
        return name

    if name.startswith('_'):
        name = name[1:]
        private = True
    else:
        private = False

    if name.startswith('lv_'):
        if private:
            return '"_{0}"'.format(name[3:])
        else:
            return '"{0}"'.format(name[3:])

    elif name.startswith('void'):
        return None
    elif name.startswith('float'):
        return 'Float'

    return '"' + name + '"'


def format_name(name):
    if name:
        if name.startswith('_'):
            private = True
            name = name[1:]
        else:
            private = False

        if name.startswith('lv_'):
            name = name[3:]
        if name.startswith('ENUM_'):
            name = name[5:]
        if name.startswith('LV_'):
            name = name[3:]

        if private:
            name = '_' + name

    return name


class Decl:

    def __init__(
            self,
            name,
            quals,
            align,
            storage,
            funcspec,
            type,
            init,
            bitsize
    ):  # NOQA
        self.name = name
        self.type = type
        self.quals = quals
        self.align = align
        self.storage = storage
        self.funcspec = funcspec
        self.init = init
        self.bitsize = bitsize

    def get_types(self):
        return self.type.get_types()

    def get_type(self):
        return self.type.declname

    def gen_pyi(self):

        s_name = format_name(self.name)

        if isinstance(self.type, (TypeDecl, PtrDecl, ArrayDecl, FuncDecl)):
            name, type_, code = self.type.gen_pyi()

        else:
            raise RuntimeError(str(s_name) + ' : ' + str(type(self.type)))

        if name is None:
            return s_name, type_, code

        if s_name != name:
            return s_name, name, code

        return name, type_, code

    def __str__(self):
        if self.name:
            return self.name

        return ''


class Typedef:
    template = '''\
class {typedef_name}({typedef_type}):
    pass
'''

    def __init__(self, name, quals, storage, type):  # NOQA
        self.name = name
        self.type = type
        self.quals = quals
        self.storage = storage

    def gen_pyi(self):
        s_name = format_name(self.name)

        name, type_, code = self.type.gen_pyi()

        if code and code.startswith('class'):
            if name is None and type_ is None:
                if s_name and code.startswith('class None'):
                    code = code.replace('class None', 'class ' + s_name, 1)

                    nme = self.name
                    if nme.startswith('_'):
                        nme = nme[1:]

                    code = code.replace(
                        "_c_type = 'None",
                        "_c_type = '" + nme
                    )

                type_ = name = s_name

            if name and s_name and s_name != name:
                code += '\n\n\nclass {0}({1}):\n    pass'.format(
                    s_name,
                    name
                )

            return name, type_, code

        return s_name, name, code

    def __str__(self):
        if self.name:
            return self.name
        return ''


class Enumerator:
    template1 = '''\
{0}: {1} = (
    {1}(
        _lib_lvgl.lib.{2}  # NOQA
    )
)'''
    template2 = '''\
{0}: {{type}} = (
    {{type}}(
        _lib_lvgl.lib.{1}  # NOQA
    )
)'''

    def __init__(self, name, value):  # NOQA
        self.name = name
        self.value = value

    def gen_pyi(self):
        name = format_name(self.name)

        type_ = find_int_type(name)

        if type_:
            code = self.template1.format(name, type_, self.name)
            py_enums.append(code)

            return name, type_, code

        return name, type_, self.template2.format(name, self.name)


class EnumeratorList:

    def __init__(self, enumerators):
        self.enumerators = enumerators

    def __iter__(self):
        if self.enumerators is not None:
            for item in self.enumerators:
                yield item


class Enum:

    def __init__(self, name, values):
        self.name = name
        self.values = values

    def gen_pyi(self):
        name = format_name(self.name)
        enumerators = []

        if name:
            t_name = find_int_type(name)

            if t_name is None:
                if name.startswith('_'):
                    t_name = name[1:]
                else:
                    t_name = name
        else:
            t_name = None

        if self.values is not None:
            for enum_item in self.values:
                e_name, e_type, e_code = enum_item.gen_pyi()

                if e_type is None:
                    if t_name is not None:
                        e_code = e_code.format(type=t_name)

                    elif name is not None:
                        e_code = e_code.format(type=name)

                enumerators.append(e_code)

        code = '\n'.join(enumerators)

        return name, None, code

    def __str__(self):
        if self.name:
            return self.name
        return ''


class TypeDecl:

    def __init__(self, declname, quals, align, type):  # NOQA
        self._declname = declname
        self.type = type
        self.quals = quals
        self.align = align

    @property
    def declname(self):
        return str(self.type)

    def gen_pyi(self):
        declname = format_name(self._declname)

        if isinstance(self.type, IdentifierType):
            return declname, self.type.gen_pyi()[-1], None

        if isinstance(self.type, (Struct, Union)):
            name, type_, code = self.type.gen_pyi()

            if name is None and code is None and type_:
                return declname, type_, None

            if code:
                if name is None:
                    code = code.replace(
                        'class None',
                        'class ' + declname,
                        1
                    )

                    nme = self._declname
                    if nme.startswith('_'):
                        nme = nme[1:]

                    code = code.replace(
                        "_c_type = 'None",
                        "_c_type = '" + nme
                    )

                    return declname, None, code

                if name and declname and name != declname:
                    return declname, name, code

            if not name:
                name = declname

            return name, type_, code

        if isinstance(self.type, Enum):
            name, type_, code = self.type.gen_pyi()

            if '{type}' in code:
                if declname:
                    if not name:
                        name = declname

                    code = code.format(type=declname)

                    if code not in py_enums:
                        py_enums.append(code)

                else:
                    raise RuntimeError

            type_ = name
            name = declname

            if name and type_ and name != type_ and name not in int_types:
                int_types[name] = type_

            return name, type_, code

        raise RuntimeError(str(declname) + ' : ' + str(type(self.type)))

    def __str__(self):
        if self._declname:
            return self._declname
        return ''


class IdentifierType:

    def __init__(self, names):
        self.names = names

    def gen_pyi(self):
        if self.names is None:
            return None, None, None

        return None, None, str(self)

    def get_raw_type(self):
        if self.names is not None:
            return ' '.join(self.names)

    def __str__(self):
        if self.names is not None:
            names = [get_py_type(name) for name in self.names]

            return ' '.join(str(name) for name in names)
        return ''


class ParamList:

    def __init__(self, params):
        self.params = params

    def __getitem__(self, item):
        return self.params[item]

    def __iter__(self):
        if self.params is not None:
            for item in self.params:
                yield item


class EllipsisParam:

    def __init__(self, **_):
        pass


class FuncDecl:
    param_template = '{param_name}: {param_type}'
    param_conv_template = (
        "    {param_name} = _get_c_obj({param_name}, '{param_type}')"
    )
    template = '''\
def {func_name}({params}) -> {ret_type}:{callback_code}
{arg_conversions}
    res = _lib_lvgl.lib.{o_func_name}({param_names}
    return _get_py_obj(res, '{c_type}')
'''

    callback_code_user_data_struct_template = '''\
    try:
        cb_store = {first_param_name}.user_data
    except:  # NOQA
        raise RuntimeError(
            'no user_data field available in the first parameter'
        )

    cb_store['{cb_type}'] = {param_name}

    {param_name} = getattr(_lib_lvgl.lib, 'py_{full_cb_type}')
    cb_store['{cb_type}.c_func'] = {param_name}'''

    var_args_template = '''
    args = list(args)
    for i, arg in enumerate(args):
        args[i] = _get_c_obj(arg)
    '''

    callback_code_user_data_param_template = '''\
    cb_store = _global_cb_store
    if '{cb_type}.{func_name}' in cb_store:
        store = cb_store['{cb_type}.{func_name}']
        if {param_name} in store:
            del store[{param_name}]
    else:
        store = _CBStore()
        store['{cb_type}.{func_name}'] = store

    cb_store_handle = _lib_lvgl.ffi.new_handle(store)    
    c_func = getattr(_lib_lvgl.lib, 'py_{full_cb_type}')
    store[{param_name}] = cb_store_handle
    store['{cb_type}'] = {param_name}
    store['{cb_type}.c_func'] = c_func

    cb_store['{cb_type}.{func_name}'] = store
    {param_name} = c_func

    user_data = cb_store_handle'''

    def __init__(self, args, type):  # NOQA
        self.args = args
        self.type = type

    @property
    def declname(self):
        return self.type.declname

    def get_types(self):
        types = []

        for arg in self.args:
            types.append(format_name(arg.declname))

    def __getitem__(self, item):
        return self.args[item]

    def gen_pyi(self):
        args = self.args or []

        if isinstance(self.type, (TypeDecl, PtrDecl)):
            name, type_, code = self.type.gen_pyi()
        else:
            raise RuntimeError(str(type(self.type)))

        if isinstance(self.type, PtrDecl):
            if type_ in ('None', None):
                type_ = 'Any'

            if isinstance(self.type.type, PtrDecl):
                declname = self.type.type.type._declname  # NOQA
            else:
                declname = self.type.type._declname  # NOQA
        else:
            declname = self.type._declname  # NOQA

        params = []
        param_names = []
        param_conversions = []

        callback_format_params = None
        has_user_data = False

        for param in args:
            if isinstance(param, (Decl, Typename)):
                param_name = param.name
                p_name, p_type, _ = param.gen_pyi()
            elif isinstance(param, EllipsisParam):
                params.append('*args')
                param_names.append('*args')
                param_conversions.append(self.var_args_template)
                break
            else:
                raise RuntimeError(str(type(param)))

            if param_name is None:
                continue

            if param_name == 'user_data':
                has_user_data = True
                continue

            param_names.append(param_name)

            if p_type is None:
                p_type = 'Any'

            params.append(
                self.param_template.format(
                    param_name=p_name,
                    param_type=p_type
                )
            )

            if '_cb_t' in p_type:
                t = param.type
                while isinstance(t, PtrDecl):
                    t = t.type

                full_cb_type = t.type.get_raw_type()

                callback_format_params = dict(
                    param_name=param_name,
                    cb_type=p_type.replace('"', ''),
                    full_cb_type=full_cb_type
                )

            else:
                param_conversions.append(
                    self.param_conv_template.format(
                        param_name=param_name,
                        param_type=p_type.replace('"', '')
                    )
                )

        if params:
            params = '\n    ' + (',\n    '.join(params)) + '\n'
        else:
            params = ''

        if param_conversions:
            param_conversions = '\n' + ('\n'.join(param_conversions))
        else:
            param_conversions = ''

        if callback_format_params is None:
            callback_code = ''
        elif has_user_data:
            param_names.append('user_data')
            callback_format_params['func_name'] = declname

            callback_code = self.callback_code_user_data_param_template.format(
                **callback_format_params
            )
        else:
            callback_format_params['first_param_name'] = param_names[0]

            callback_code = self.callback_code_user_data_struct_template.format(
                **callback_format_params
            )

        if callback_code:
            callback_code = '\n' + callback_code + '\n'

        if param_names:
            param_names = (
                    '  # NOQA\n        ' + (
                ',\n        '.join(param_names)) + '\n    )'
            )
        else:
            param_names = ')  # NOQA'

        return name, type_, self.template.format(
            o_func_name=declname,
            func_name=name,
            params=params,
            ret_type=type_,
            c_type=type_.replace('"', '')
            if type_ and type_ != 'Any'
            else 'void' if type is not None else '',
            arg_conversions=param_conversions,
            param_names=param_names,
            callback_code=callback_code
        )


class Typename:

    def __init__(self, name, quals, align, type):  # NOQA
        self.name = name
        self.type = type
        self.quals = quals
        self.align = align

    def get_type(self):
        return self.type.declname

    def gen_pyi(self):

        s_name = format_name(self.name)

        if isinstance(self.type, TypeDecl):
            name, type_, code = self.type.gen_pyi()
            if name:
                return name, type_, code

            return s_name, type_, code

        if isinstance(self.type, PtrDecl):
            name, type_, code = self.type.gen_pyi()
            if name:
                return name, type_, code

            return s_name, type_, code

        raise RuntimeError(str(s_name) + ' : ' + str(type(self.type)))

    def __str__(self):
        if self.name:
            return self.name
        return ''


class PtrDecl:

    def __init__(self, quals, type):  # NOQA
        self.quals = quals
        self.type = type

    @property
    def declname(self):
        return self.type.declname

    def get_types(self):
        if isinstance(self.type, (PtrDecl, FuncDecl)):
            return self.type.get_types()
        return []

    def gen_pyi(self):
        if isinstance(self.type, TypeDecl):
            return self.type.gen_pyi()
        if isinstance(self.type, FuncDecl):
            return self.type.gen_pyi()
        if isinstance(self.type, PtrDecl):
            return self.type.gen_pyi()

        raise RuntimeError(str(type(self.type)))

    def __str__(self):
        type_ = get_py_type(str(self.type))
        if type_:
            return type_

        return ''


class FuncDef:

    def __init__(self, decl, param_decls, body):  # NOQA
        self.decl = decl
        self.param_decls = param_decls
        self.body = body

    def gen_pyi(self):
        return self.decl.gen_pyi()


class Struct:
    property_template = '''\
    @property
    def {field_name}(self) -> {field_type}:
        return self._get_field(
            '{field_name}', 
            '{c_type}'
        )

    @{field_name}.setter
    def {field_name}(self, value: {field_type}):
        self._set_field(
            '{field_name}', 
            value, 
            '{c_type}'
        )'''

    user_data_property_template = '''\
    @property
    def user_data(self) -> dict:
        if '__cb_store__' not in self.__dict__:
            cb_store = self.__dict__['__cb_store__'] = _CBStore()
            cb_store_handle = _lib_lvgl.ffi.new_handle(cb_store)
            self.__dict__['__cb_store_handle__'] = cb_store_handle
            self._obj.user_data = cb_store_handle

        return self.__dict__['__cb_store__']

    @user_data.setter
    def user_data(self, value: dict):
        if '__cb_store__' in self.__dict__:
            if self.__dict__['__cb_store__'] == value:
                return

        cb_store_handle = _lib_lvgl.ffi.new_handle(value)
        self.__dict__['__cb_store__'] = value
        self.__dict__['__cb_store_handle__'] = cb_store_handle
        self._obj.user_data = cb_store_handle'''

    callback_property_template = '''\
    @property
    def {field_name}(self) -> Optional[{field_type}]:
        cb_store = self.user_data
        return cb_store.get('{field_type}', None)

    @{field_name}.setter
    def {field_name}(self, value: {field_type}):
        cb_store = self.user_data
        if '{field_type}' not in cb_store:
            cb_store['{field_type}'] = value
            c_func = getattr(_lib_lvgl.lib, 'py_{full_field_type}')
            cb_store['{field_type}.c_func'] = c_func
            self._obj.{field_name} = c_func
        else:
            cb_store['{field_type}'] = value'''

    int_param_template = (
        '{field_name}: Optional[{field_type}] = 0'
    )
    bool_param_template = (
        '{field_name}: Optional[{field_type}] = False'
    )

    param_template = (
        '{field_name}: Optional[{field_type}] = _DefaultArg'
    )
    field_template = '    {field_name}: {field_type} = ...'

    template = '''\
class {struct_name}(_StructUnion): {nested_structs}
    _c_type = '{c_type} *'

    def __init__({params}):

        super().__init__({param_names})
{py_properties}
'''

    def __init__(self, name, decls):
        self.name = name
        self.decls = decls

    def gen_pyi(self):
        s_name = format_name(self.name)

        params = []
        nested_structs = []
        py_properties = []
        param_names = []

        if self.decls is None:
            return None, s_name, None

        for field in self.decls:
            if isinstance(field, Decl):
                name, type_, code = field.gen_pyi()
                full_field_type = None

                if isinstance(field.type, PtrDecl):
                    if isinstance(field.type.type, FuncDecl):
                        if code and code.startswith('def '):
                            continue

                elif isinstance(field.type, TypeDecl):
                    if isinstance(field.type.type, (Union, Struct)) and code:
                        code = '\n'.join(
                            '    ' + line for line in code.rstrip().split('\n')
                        )

                        code = code.replace(name, '_' + name)

                        nested_structs.append(code)
                        # field_names.append(name)
                        param_names.append(name + '=' + name)
                        params.append(
                            name + ': ' + 'Optional[_' + name + '] = None'
                        )

                        py_properties.append(
                            self.property_template.format(
                                field_name=name,
                                field_type='_' + name,
                                c_type=''
                            )
                        )

                        continue

                    elif isinstance(field.type.type, IdentifierType):
                        full_field_type = field.type.type.get_raw_type()

                if not code:
                    code = type_

                if not name:
                    raise RuntimeError(repr(type_) + ' : ' + repr(code))

                if type_ in (None, 'None'):
                    type_ = 'Any'

                for item in ('Any', 'List', 'bool'):
                    if type_.startswith(item):
                        break

                else:
                    if '"' not in type_:
                        type_ = '"' + type_ + '"'

                param_names.append(name + '=' + name)

                for item in ('_cb_t', '_f_t'):
                    if item not in type_:
                        continue

                    py_properties.append(
                        self.callback_property_template.format(
                            field_name=name,
                            field_type=type_,
                            full_field_type=full_field_type
                        )
                    )

                    params.append(
                        self.param_template.format(
                            field_name=name,
                            field_type=type_
                        )
                    )

                    break
                else:
                    if name == 'user_data':
                        py_properties.append(self.user_data_property_template)

                    else:
                        py_properties.append(
                            self.property_template.format(
                                field_name=name,
                                field_type=type_,
                                c_type=type_.replace('"', '')
                                if type_ != 'Any'
                                else 'void'
                            )
                        )

                    if str(type_) == 'bool':
                        params.append(
                            self.bool_param_template.format(
                                field_name=name,
                                field_type=type_
                            )
                        )

                    elif str(type_).replace('"', '') in int_types:
                        params.append(
                            self.int_param_template.format(
                                field_name=name,
                                field_type=type_
                            )
                        )
                    else:

                        params.append(
                            self.param_template.format(
                                field_name=name,
                                field_type=type_
                            )
                        )

            else:
                raise RuntimeError(str(type(field)))

        if not params and not nested_structs:
            return None, s_name, None

        if nested_structs:
            nested_structs = '\n' + ('\n\n'.join(nested_structs)) + '\n'
        else:
            nested_structs = ''

        params.insert(0, '/')
        params.insert(0, 'self')
        if len(', '.join(params)) > 40:
            params = (
                    '\n        ' +
                    (', \n        '.join(params)) +
                    '\n    '
            )
        else:
            params = ', '.join(params)

        py_properties = '\n' + ('\n\n'.join(py_properties))

        param_names = (
                '\n            ' +
                (', \n            '.join(param_names)) +
                '\n        '
        )

        if self.name is None:
            c_type = 'None'
        elif self.name.startswith('_'):
            c_type = self.name[1:]
        else:
            c_type = self.name

        return s_name, None, self.template.format(
            c_type=c_type,
            struct_name=s_name,
            nested_structs=nested_structs,
            py_properties=py_properties,
            param_names=param_names,
            params=params
        )

    def __str__(self):
        if self.name:
            return self.name

        return ''


class Union(Struct):
    pass


class ArrayDecl:

    def __init__(self, type, dim, dim_quals):  # NOQA
        self.type = type
        self.dim = dim
        self.dim_quals = dim_quals

    @property
    def declname(self):
        return self.type.declname

    def gen_pyi(self):
        if isinstance(self.type, TypeDecl):
            name, type_, code = self.type.gen_pyi()
            if code:
                return name, 'List[' + code + ']', None

            return name, 'List[' + type_ + ']', None

        if isinstance(self.type, PtrDecl):
            name, type_, code = self.type.gen_pyi()

            if name is None:
                return type_, 'List[' + code + ']', None

            if type_ is None:
                type_ = 'Any'

            return name, 'List[' + type_ + ']', None

        if isinstance(self.type, ArrayDecl):
            name, type_, _ = self.type.gen_pyi()
            return name, 'List[' + type_ + ']', None

        raise RuntimeError(str(type(self.type)))

    def __str__(self):
        type_ = str(self.type)
        if type_:
            type_ = get_py_type(type_)
            if type_ == 'None':
                type_ = 'Any'

            return 'List[' + type_ + ']'
        else:
            return 'list'


class CatchAll:

    def __init__(self, name):
        self.name = name

    def __call__(self, **_):
        return self

    @property
    def children(self):
        def wrapper():
            return []

        return wrapper

    def gen_pyi(self):  # NOQA
        return None, None, None

    def __str__(self):
        return ''


callbacks = []


class RootTypedef(Typedef):
    struct_userdata_template = (
        'cb_store = _lib_lvgl.ffi.from_handle({param_name}.user_data)'
    )
    arg_user_data_template = 'cb_store = _lib_lvgl.ffi.from_handle(user_data)'

    callback_param_conversion_template = '''\
        {param_name} = _get_py_obj(
            {param_name},
            '{c_type}'
        )'''

    callback_template = '''\
@_lib_lvgl.ffi.def_extern(
    name='py_lv_{func_name}'
)
def __{func_name}_callback_func({params}):
    try:
        {struct_userdata}
    except:  # NOQA
        print('No "user_data" field available ({func_name})')
        return

    if '{func_name}' in cb_store:
        func = cb_store['{func_name}']{param_conversion}
        try:
            res = func({param_names})

            if res is None:
                return None

            return _get_c_obj(res)

        except:  # NOQA
            import traceback

            traceback.print_exc()
    else:
        print('"{func_name}" is not registered')
'''

    pyi_callback_template = '{func_name} = Callable[{param_types}, {ret_type}]'

    def gen_pyi(self):
        s_type = self.type
        if isinstance(s_type, PtrDecl):
            s_type = s_type.type
            if isinstance(s_type, FuncDecl):
                s_type = s_type.type
                if isinstance(s_type, (TypeDecl, PtrDecl)):
                    if isinstance(s_type, PtrDecl):
                        s_type = s_type.type
                        ptr = True
                    else:
                        ptr = False

                    name = s_type._declname  # NOQA

                    for item in ('_cb_t', '_f_t'):

                        if item in name:
                            if name.replace('lv_', '', 1) in py_callback_names:
                                return

                            try:
                                ret_type = get_py_type(s_type.type.names[0])

                                if ret_type in (None, 'None') and ptr:
                                    ret_type = 'Any'

                            except:  # NOQA
                                ret_type = get_py_type(s_type.type.name)

                            param_names = []
                            params = []
                            param_types = []
                            param_conversions = []
                            arg_user_data = False

                            for param in self.type.type.args.params:
                                p_ptr = False

                                if isinstance(param, Typename):
                                    p_type = param.type
                                    param_name = param.name

                                    if isinstance(p_type, PtrDecl):
                                        p_type = p_type.type.type
                                        p_ptr = True

                                        if isinstance(p_type, IdentifierType):
                                            param_type = get_py_type(
                                                p_type.names[0]
                                            )
                                        elif isinstance(p_type, Struct):
                                            param_type = get_py_type(
                                                p_type.name
                                            )
                                        else:
                                            raise RuntimeError(
                                                str(type(p_type))
                                            )

                                    elif isinstance(p_type, TypeDecl):
                                        p_type = p_type.type
                                        param_type = get_py_type(
                                            p_type.names[0]
                                        )
                                    else:
                                        raise RuntimeError(str(type(p_type)))

                                elif isinstance(param, Decl):
                                    p_type = param.type
                                    param_name = param.name

                                    if isinstance(p_type, PtrDecl):
                                        p_type = p_type.type
                                        p_ptr = True

                                        if isinstance(p_type, IdentifierType):
                                            param_type = get_py_type(
                                                p_type.names[0]
                                            )

                                        elif isinstance(p_type, TypeDecl):
                                            p_type = p_type.type

                                            if isinstance(
                                                    p_type,
                                                    IdentifierType
                                            ):
                                                param_type = get_py_type(
                                                    p_type.names[0]
                                                )

                                            elif isinstance(p_type, Struct):
                                                param_type = get_py_type(
                                                    p_type.name
                                                )

                                            else:
                                                raise RuntimeError(
                                                    str(type(p_type))
                                                )
                                        else:
                                            raise RuntimeError(
                                                str(type(p_type))
                                            )

                                    elif isinstance(p_type, TypeDecl):
                                        param_type = get_py_type(
                                            p_type.type.names[0]
                                        )

                                    elif isinstance(p_type, ArrayDecl):
                                        param_type = 'List[' + get_py_type(
                                            p_type.type.type.names[0]
                                        ) + ']'

                                    else:
                                        raise RuntimeError(str(type(p_type)))
                                else:
                                    raise RuntimeError(str(type(param)))

                                if param_name == 'user_data':
                                    arg_user_data = len(param_names) - 1
                                    param_type = 'Any'
                                else:
                                    param_conversions.append(
                                        self.callback_param_conversion_template.format(
                                            # NOQA
                                            param_name=param_name,
                                            c_type='void'
                                            if param_type in ('None', None)
                                            else param_type.replace('"', '')
                                        )
                                    )

                                if p_ptr and param_type in ('None', None):
                                    param_type = 'Any'

                                param_types.append(param_type)
                                param_names.append(param_name)
                                params.append(
                                    param_name + ': ' + str(param_type)
                                )

                            if param_types:
                                param_types = '[' + (', '.join(
                                    str(pt) for pt in param_types
                                )
                                ) + ']'
                            else:
                                param_types = '...'

                            if param_conversions:
                                param_conversions = (
                                        '\n' + (
                                    '\n'.join(param_conversions)) + '\n'
                                )
                            else:
                                param_conversions = ''

                            if arg_user_data is False:
                                struct_userdata = (
                                    self.struct_userdata_template.format(
                                        param_name=param_names[0]
                                    )
                                )
                            else:
                                param_names.insert(arg_user_data, 'None')
                                struct_userdata = self.arg_user_data_template

                            if param_names:
                                if 'user_data' in param_names:
                                    user_data = 'user_data'
                                else:
                                    user_data = param_names[0] + '.user_data'

                                if len(', '.join(param_names)) > 45:
                                    param_names = (
                                            '\n                ' +
                                            ',\n                '.join(
                                                param_names
                                            )
                                            + '\n            '
                                    )
                                else:
                                    param_names = ', '.join(param_names)
                            else:
                                user_data = None
                                param_names = ''

                            if params:
                                if len(', '.join(params)) > 45:
                                    params = (
                                            '\n    ' +
                                            ',\n    '.join(params) +
                                            '\n'
                                    )
                                else:
                                    params = ', '.join(params)
                            else:
                                params = ''

                            if user_data is not None:
                                callbacks.append(
                                    self.callback_template.format(
                                        func_name=name.replace('lv_', '', 1),
                                        params=params,
                                        user_data=user_data,
                                        param_conversion=param_conversions,
                                        param_names=param_names,
                                        struct_userdata=struct_userdata
                                    )
                                )

                                cb = self.pyi_callback_template.format(
                                    func_name=name.replace('lv_', '', 1),
                                    param_types=param_types,
                                    ret_type=ret_type
                                )

                                if len(cb) > 80:
                                    cb += '  # NOQA'

                                py_callbacks.append(cb)

                                py_callback_names.append(
                                    name.replace('lv_', '', 1)
                                )

                            return

        t_name = format_name(self.name)
        name, type_, code = self.type.gen_pyi()

        if isinstance(self.type, TypeDecl):
            if type_:
                type_ = type_.replace('"', '')

            if code and '_lib_lvgl.lib.' in code and 'LV_' in code:
                if name and type_ and name == type_:
                    type_ = 'int_'

                    tdef = self.template.format(
                        typedef_name=name,
                        typedef_type=type_
                    )
                    if name not in py_int_type_names:
                        py_int_type_names.append(name)
                        py_int_types.append(tdef)

            else:
                if (
                        name and
                        type_ and
                        t_name and
                        name == t_name and
                        name != type_ and
                        not code
                ):
                    if type_ in int_types:
                        tdef = self.template.format(
                            typedef_name=name,
                            typedef_type=type_
                        )

                        py_int_type_names.append(name)
                        py_int_types.append(tdef)

                    else:
                        if t_name not in py_typedef_names:
                            tdef = self.template.format(
                                typedef_name=t_name,
                                typedef_type=type_
                            )

                            py_typedef_names.append(t_name)
                            py_typedefs.append(tdef)

                    return

                if code:
                    if code.startswith('class'):
                        if (
                                name and type_ and
                                name not in py_struct_names and
                                type_ not in py_struct_names
                        ):
                            py_struct_names.append(type_)
                            py_struct_names.append(name)
                            py_structs.append(code)

                        elif (
                                name and not type_ and
                                name not in py_struct_names
                        ):
                            py_struct_names.append(name)
                            py_structs.append(code)

                        elif (
                                type_ and not name and
                                type_ not in py_struct_names
                        ):
                            py_struct_names.append(type_)
                            py_structs.append(code)

                    else:
                        code = self.template.format(
                            typedef_name=t_name,
                            typedef_type=type_
                        )

                        if (
                                type_ and
                                type_ not in (
                                py_callback_names + py_typedef_names
                        )
                        ):
                            py_typedef_names.append(type_)
                            py_typedefs.append(code)

                    if t_name and type_ and t_name != type_:
                        if t_name not in py_callback_names + py_typedef_names:
                            tdef = self.template.format(
                                typedef_name=t_name,
                                typedef_type=type_
                            )

                            py_typedef_names.append(t_name)
                            py_typedefs.append(tdef)

        elif isinstance(self.type, ArrayDecl):
            if code:
                if not t_name:
                    t_name = name

                code = '{name}: {type} = ...'.format(name=t_name, type=code)

                if t_name not in py_typedef_names:
                    py_typedef_names.append(t_name)
                    py_typedefs.append(code)

        elif isinstance(self.type, PtrDecl):
            if (
                    name not in
                    py_type_names + py_callback_names +
                    py_typedef_names + py_struct_names +
                    py_enum_names + py_func_names
            ):
                py_typedef_names.append(name)
                py_typedefs.append(code)

            if t_name and name and t_name != name:
                if t_name not in py_callback_names + py_typedef_names:
                    py_typedef_names.append(t_name)
                    py_typedefs.append(
                        'class {0}({1}):\n    pass'.format(t_name, name)
                    )

        else:
            raise RuntimeError(str(type(self.type)))


int_types = {
    'DPI_DEF': 'coord_t',
    'ANIM_REPEAT_INFINITE': 'uint16_t',
    'ANIM_PLAYTIME_INFINITE': 'uint32_t',
    'LOG_LEVEL_*': 'log_level_t',
    '_STR_SYMBOL_*': 'uint8_t',
    'SIZE_CONTENT': 'coord_t',
    'COORD_MAX': 'coord_t',
    'COORD_MIN': 'coord_t',
    'COLOR_DEPTH': 'uint8_t',
    'ZOOM_NONE': 'int16_t',
    'RADIUS_CIRCLE': 'int32_t',
    'LABEL_DOT_NUM': 'uint32_t',
    'LABEL_POS_LAST': 'uint32_t',
    'LABEL_TEXT_SELECTION_OFF': 'uint32_t',
    'BTNMATRIX_BTN_NONE': 'uint16_t',
    'CHART_POINT_NONE': 'coord_t',
    'DROPDOWN_POS_LAST': 'uint32_t',
    'TEXTAREA_CURSOR_LAST': 'int32_t',
    'PART_TEXTAREA_PLACEHOLDER': 'style_selector_t',
    'TABLE_CELL_NONE': 'uint16_t',
    'OBJ_FLAG_FLEX_IN_NEW_TRACK': 'obj_flag_t',
    'GRID_CONTENT': 'coord_t',
    'GRID_TEMPLATE_LAST': 'coord_t',
    'part_t': 'style_selector_t',
    'state_t': 'style_selector_t',
    'uint8_t': None,
    'uint16_t': None,
    'uint32_t': None,
    'uint64_t': None,
    'int8_t': None,
    'int16_t': None,
    'int32_t': None,
    'int64_t': None,
    'uintptr_t': 'int_',
    'intptr_t': 'int_',
    'int_': None
}


def find_int_type(name):
    if name is None:
        return None

    if name in int_types:
        return int_types[name]

    for key, val in int_types.items():
        if key.endswith('*') and name.startswith(key[:-1]):
            return val


class RootDecl(Decl):
    int_type_template = '''\
class {name}({type}):
    pass
'''

    def gen_pyi(self):
        d_name = format_name(self.name)

        if isinstance(self.type, Enum):
            name, type_, code = self.type.gen_pyi()

            if code:
                def _check_code(c):
                    if ')\n_' in c:
                        c = list('_' + item + ')' for item in c.split(')\n_'))
                        c = '\n\n'.join(c)[1:-1].split('\n\n')
                        for item in c[:]:
                            if item in py_enums:
                                return False

                    elif c in py_enums:
                        return False

                    return True

                if name is None:
                    name = d_name

                if name:
                    e_type = find_int_type(name)

                    if e_type:
                        type_ = e_type

                if '{type}' in code:
                    if type_:
                        code = code.format(type=type_)
                        if _check_code(code):
                            py_enums.append(code)
                        return
                    elif name:
                        code = code.format(type=name)
                        if _check_code(code):
                            py_enums.append(code)
                        return
                    else:
                        raise RuntimeError

                if name and type_ and name != type_:
                    if name not in py_int_type_names:
                        py_int_type_names.append(name)
                        py_int_types.append(
                            self.int_type_template.format(name=name, type=type_)
                        )

                if _check_code(code):
                    py_enums.append(code)

        elif isinstance(self.type, FuncDecl):
            name, type_, code = self.type.gen_pyi()
            if code:
                if not name and d_name:
                    name = d_name

                if name not in py_callback_names + py_func_names:
                    py_func_names.append(name)
                    py_funcs.append(code)

        elif isinstance(self.type, TypeDecl):
            name, type_, code = self.type.gen_pyi()

            if code:
                if not name and d_name:
                    name = d_name

                code = '{name}: {type} = ...'.format(name=name, type=code)

                if name not in py_type_names:
                    py_type_names.append(name)
                    py_types.append(code)

        elif isinstance(self.type, PtrDecl):
            name, type_, code = self.type.gen_pyi()
            if code:
                if not name and d_name:
                    name = d_name

                if name not in py_callback_names + py_func_names:
                    py_func_names.append(name)
                    py_funcs.append(code)

        elif isinstance(self.type, Struct):
            name, type_, code = self.type.gen_pyi()
            if code:
                if not name and d_name:
                    name = d_name

                if name not in py_struct_names:
                    py_struct_names.append(name)
                    py_structs.append(code)

        else:
            raise RuntimeError(str(type(self.type)))


class RootFuncDef(FuncDef):

    def gen_pyi(self):
        if self.param_decls is not None:
            raise RuntimeError(str(type(self.param_decls)))

        if isinstance(self.decl, Decl):
            name, type_, code = self.decl.gen_pyi()

            if not name:
                name = type_

            if code:
                if name not in py_callback_names + py_func_names:
                    py_func_names.append(name)
                    py_funcs.append(code)

        else:
            raise RuntimeError(str(type(self.decl)))


py_enums = []
py_enum_names = []

py_int_types = []
py_int_type_names = []

py_callbacks = []
py_callback_names = []

py_typedefs = []
py_typedef_names = []

py_funcs = []
py_func_names = []

py_structs = []
py_struct_names = []

py_types = []
py_type_names = []


class GlobalsWrapper(dict):

    def __init__(self):
        self.globs = globals()
        dict.__init__(self)

    def __getitem__(self, item):
        if item in self.globs:
            return self.globs[item]

        return CatchAll(item)


# this is some monkey patching code to flatten the output when printing a node.
def patch_pycparser():
    def _repr(obj):
        if isinstance(obj, list):
            return '[' + (', '.join(_repr(item) for item in obj)) + ']'
        else:
            return repr(obj)

    def cls_repr(self):
        result = self.__class__.__name__ + '('
        attrs = []

        for name in self.__slots__[:-2]:
            attrs.append(name + '=' + _repr(getattr(self, name)))

        result += ', '.join(attrs)
        result += ')'

        return result

    ast = sys.modules['pycparser.c_ast']

    setattr(ast.Node, '__repr__', cls_repr)  # NOQA


TEMPLATE = '''\
{py_template}

# ****************  INTEGER_TYPES  ****************
{int_types}
# ************************************************


# ****************  ENUMERATIONS  ****************
{enums}
# ************************************************


# ***************  STRUCTS/UNIONS  ***************
{structs}
# ************************************************


# **************  CALLBACK TYPES  ****************
{callback_types}
# ************************************************


# *****************  CALLBACKS  ******************
{callbacks}
# ************************************************


# ******************  TYPEDEFS  ******************
{typedefs}
# ************************************************


# *****************  FUNCTIONS  ******************
{functions}
# ************************************************


def __build_font(name):
    try:
        f = getattr(_lib_lvgl.lib, name)
        f_pointer = _lib_lvgl.ffi.addressof(f)

        instance = font_t()
        instance._obj = f_pointer
        return instance

    except AttributeError:
        class dummy_class:

            @property
            def _obj(self):
                raise RuntimeError(
                    'LVGL was not compiled with this font ("{{0}}"'.format(name)
                )

        return dummy_class()


font_montserrat_12_subpx: font_t = __build_font(
    'lv_font_montserrat_12_subpx'
)

font_montserrat_28_compressed: font_t = __build_font(
    'lv_font_montserrat_28_compressed'
)

font_dejavu_16_persian_hebrew: font_t = __build_font(
    'lv_font_dejavu_16_persian_hebrew'
)

font_simsun_16_cjk: font_t = __build_font(
    'lv_font_simsun_16_cjk'
)

font_unscii_8: font_t = __build_font(
    'lv_font_unscii_8'
)

font_unscii_16: font_t = __build_font(
    'lv_font_unscii_16'
)

'''

FONT_TEMPLATE = '''\
font_montserrat_{0}: font_t = __build_font(
    'lv_font_montserrat_{0}'
)


'''

for i in range(8, 50, 2):
    TEMPLATE += FONT_TEMPLATE.format(i)

TEMPLATE += 'del __build_font\n'


def run(output_path, ast):
    patch_pycparser()

    globs = GlobalsWrapper()

    for child in ast:
        # check to see if this "child" (node) is from the
        # fake_lib_c includes if it is then we skip it since it
        # is not needed
        if utils.is_lib_c_node(child):
            continue

        # The way I wrote the pyi builder is rather crafty actually.
        # There is some smoke and mirrors to it but not too bad.
        # I wrote a class that overrides the module import of pyi_builder.
        # I did this to allow dynamic loading of the nodes that I
        # wanted to use from pycparser. The nodes I don't use I didn't
        # have to define specifically and instead it gets dumped into a
        # CatchAll class that does nothing. The string representation of
        # the nodes has been monkey pathed to flatten the output. I use
        # this output in a dynamic way using eval and setting the globals
        # dictionary to that module class I made which is a subclass
        # of a dict. This allow me to pull the requested c_ast classes
        # which are version that I wrote located in the pyi_builder
        # module. Doing this makes for a smaller code footprint because
        # I don't have to have all kinds of crazy instance checking to
        # see what I am dealing with.
        node = eval('Root' + str(child), globs)
        node.gen_pyi()

    base_path = os.path.dirname(__file__)

    with open(os.path.join(output_path, '__init__.py'), 'w') as f:
        f.write(
            TEMPLATE.format(
                py_template=open(os.path.join(base_path, 'lvgl.template.py'), 'r').read(),
                int_types='\n\n'.join(py_int_types),
                enums='\n\n'.join(py_enums),
                structs='\n\n'.join(py_structs),
                callback_types='\n\n'.join(py_callbacks),
                callbacks='\n\n'.join(callbacks),
                typedefs='\n\n'.join(py_typedefs),
                functions='\n\n'.join(py_funcs)
            )
        )
