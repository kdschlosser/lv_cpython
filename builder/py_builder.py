# -*- coding: utf-8 -*-

import os
import sys
from pycparser import c_generator  # NOQA
from pycparser import c_ast  # NOQA

from . import utils

pragma_pack = None

PRIMITIVES = {
    'int8_t': 'int8_t',
    'uint8_t': 'uint8_t',

    'int16_t': 'int16_t',
    'uint16_t': 'uint16_t',

    'int32_t': 'int32_t',
    'uint32_t': 'uint32_t',

    'int64_t': 'int64_t',
    'uint64_t': 'uint64_t',

    'float': 'float_t',
    'double': 'double_t',
    'size_t': 'size_t',

    'int': 'int_t',
    'unsigned int': 'uint_t',

    'long': 'long_t',
    'unsigned long': 'ulong_t',

    'long int': 'long_t',
    'unsigned long int': 'long_t',

    'long long': 'longlong_t',
    'unsigned long long': 'ulonglong_t',

    'long long int': 'longlong_t',
    'unsigned long long int': 'ulonglong_t',

    'char': 'char_t',
    'unsigned char': 'uchar_t',

    'short': 'short_t',
    'unsigned short': 'ushort_t',

    'short int': 'short_t',
    'unsigned short int': 'ushort_t',

    'bool': 'bool_t',
}

last_node = None


def visit(self, node):
    global last_node

    if utils.is_lib_c_node(node):
        return ''

    method = f'visit_{node.__class__.__name__}'

    if last_node is None:
        last_node = node
    elif last_node == node:
        print('ERROR:', node)
        return ''

    ret = getattr(self, method, self.generic_visit)(node)
    return '' if ret.strip() == ';' else ret


# # turns function definitions into declarations.
# def visit_FuncDef(self, n):
#     decl = self.visit(n.decl)  # NOQA
#     self.indent_level = 0
#     if n.param_decls:
#         knrdecls = ';\n'.join(self.visit(p) for p in n.param_decls)
#         res = decl + '\n' + knrdecls + ';\n'
#     else:
#         res = decl + ';\n'
#
#     return res


# def visit_FuncDecl(self, n):
#     s = self._generate_type(n)
#     func_name, params = s.split('(', 1)
#     retval, func_name = func_name.rsplit(' ', 1)
#     export_symbols.append(func_name.replace('*', ''))
#     return s


def visit_Decl(self, n, no_type=False):
    # no_type is used when a Decl is part of a DeclList, where the type is
    # explicitly only for the first declaration in a list.
    #
    s = n.name if no_type else self._generate_decl(n)
    if n.bitsize:
        s += ' : ' + self.visit(n.bitsize)
    if n.init:
        s += ' = ' + self._visit_expr(n.init)

    if (
        '\n' not in s.strip() and
        s.strip().endswith(')') and
        ';' not in s
        and '(' in s
        and '=' not in s
    ):
        func_name, params = s.split('(', 1)
        retval, func_name = func_name.rsplit(' ', 1)

        if 'printf' in func_name:
            return s

        if s.endswith('...)'):
            return s

        retval += ' ' + ('*' * func_name.count('*'))
        func_name = func_name.replace('*', '')

        if not func_name.strip():
            return s

        new_func_name = 'py_' + func_name
        retval = retval.replace('static ', '').strip()
        retval = retval.replace('inline ', '').strip()
        retval = retval.replace('extern ', '').strip()

        if func_name == 'SDL_main':
            return ''

        if retval.strip() == 'void':
            ret = ''
        else:
            ret = 'return '

        param_names = []
        open_par = 0
        param = ''
        temp_arg_count = 0
        temp_args = []

        def _get_param_name(p, t_count):
            p = p.strip()

            if not p:
                return '', t_count
            if p.count('('):
                p_name = p.split(')', 1)[0]
                p_name = p_name.split('(', 1)[-1]
            elif ' ' not in p:
                if p == 'void':
                    temp_args.append([None, ''])
                    return '', t_count
                p_name = ''
            else:
                p_name = p.rsplit(' ', 1)[-1]

            p_name = p_name.split('[')[0]
            p_name = p_name.replace('*', '').strip()

            if not p_name:
                t_count += 1
                p_name = f'arg{t_count}'
                temp_args.append([p, p + ' ' + p_name])
            else:
                temp_args.append([None, p_name])

            return p_name, t_count

        for char in params:
            if char == ',':
                if open_par > 0:
                    param += char
                    continue

                param_name, temp_arg_count = _get_param_name(param, temp_arg_count)

                param_names.append(param_name)
                param = ''
                continue

            if char == '(':
                open_par += 1
            if char == ')':
                open_par -= 1

                if open_par < 0:
                    param_name, temp_arg_count = _get_param_name(param, temp_arg_count)
                    param_names.append(param_name)
            param += char

        if func_name in ('SDL_CreateThread', 'SDL_CreateThreadWithStackSize'):
            param_names = param_names[:-2]
            params = params.rsplit(',', 2)[0] + ')'

        repl_pattern = []
        repl_text = []
        for pattern, repl in temp_args:
            if pattern is not None:
                repl_pattern.append(pattern)
                repl_text.append(repl)

        repl_pattern = ', '.join(repl_pattern)
        if repl_pattern:
            params = params.replace(repl_pattern, ', '.join(repl_text))

        param_names = ', '.join(param_names)

        template = '''\
{retval} {new_func_name}({params} {{
    {ret}{func_name}({param_names});
}}
                '''
        data = template.format(
            retval=retval,
            new_func_name=new_func_name,
            params=params,
            func_name=func_name,
            param_names=param_names,
            ret=ret
        )

        if func_name in ('SDL_CreateThread', 'SDL_CreateThreadWithStackSize'):
            s = s.rsplit(',', 2)[0] + ')'

        decl = s.replace(func_name, new_func_name, 1).replace('static ', '')
        decl = decl.replace('inline ', '').replace('extern ', '') + ';'
        export = (
            '__declspec(dllexport) ' if sys.platform.startswith('win') else ''
        )

        func_decls.append(export + decl)

        func_defs.append(export + data)
        export_symbols.append(new_func_name)
        return s

    '''
    <class 'pycparser.c_ast.Decl'>: extern const <class 'pycparser.c_ast.IdentifierType'>: lv_font_t lv_font_montserrat_8;
    '''
    if isinstance(n.type, c_ast.TypeDecl):
        print(n.name)
        print(n.type.type)
        print(n.type.declname)

        if n.name.startswith('lv_font_'):
            type_ = n.type.type.names[0]

            export = (
                '__declspec(dllexport) ' if sys.platform.startswith('win') else ''
            )

            decl = f'{export} extern const {type_} * py_{n.name} = &{n.name};'
            exported_variables.append(decl)
            exported_variable_names.append(n.name)
    return s


exported_variables = []
exported_variable_names = []


setattr(c_generator.CGenerator, 'visit', visit)
# setattr(c_generator.CGenerator, 'visit_FuncDecl', visit_FuncDecl)
setattr(c_generator.CGenerator, 'visit_Decl', visit_Decl)
# setattr(c_generator.CGenerator, 'visit_FuncDef', visit_FuncDef)

generator = c_generator.CGenerator()


def get_py_type(name):
    if not name:
        return name

    if name in PRIMITIVES:
        return PRIMITIVES[name]

    if name.startswith('_'):
        name = name[1:]
        private = True
    else:
        private = False

    if name.startswith('lv_'):
        return (
            '"_{0}"'.format(name[3:]) if private else '"{0}"'.format(name[3:])
        )

    return None if name.startswith('void') else f'"{name}"'


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
            name = f'_{name}'

    return name


class Decl(c_ast.Decl):

    def get_types(self):
        return self.type.get_types()

    def get_type(self):
        return self.type._declname  # NOQA

    def gen_py(self):

        s_name = format_name(self.name)

        if isinstance(self.type, (TypeDecl, PtrDecl, ArrayDecl, FuncDecl)):
            name, type_, code, r_ptr = self.type.gen_py()
        else:
            raise RuntimeError(f'{str(s_name)} : {str(type(self.type))}')

        return (
            (s_name, type_, code, r_ptr)
            if name is None else (s_name, name, code, r_ptr)
            if s_name != name else (name, type_, code, r_ptr)
        )


class Typedef(c_ast.Typedef):
    template = '''\
class {typedef_name}({typedef_type}):
    pass
'''

    def gen_py(self):
        s_name = format_name(self.name)

        name, type_, code, ptr = self.type.gen_py()

        if code and code.startswith('class'):
            if name is None and type_ is None:
                if s_name and code.startswith('class None'):
                    code = code.replace('class None', f'class {s_name}', 1)
                    self.type.fields.name = s_name

                type_ = name = s_name

            if name and s_name and s_name != name:
                code += '\n\n\nclass {0}({1}):\n    pass'.format(
                    s_name,
                    name
                )

            return name, type_, code, ptr

        return s_name, name, code, ptr


enum_namespace = {'INT32_MAX': 0x7FFFFFFF}
current_enum_count = -1


class Enumerator(c_ast.Enumerator):
    template1 = '''\
{0}: {1} = {2}'''
    template2 = '''\
{0}: {{type}} = {1}'''

    def gen_py(self):
        global current_enum_count
        name = format_name(self.name)

        type_ = find_int_type(name)

        try:
            value = generator.visit(self.value)
        except RecursionError:
            print('ENUM_ERROR:', name)
            return None, None, ''

        if not value.strip():
            current_enum_count += 1
            value = '0x' + hex(current_enum_count)[2:].upper()
            enum_namespace[name] = current_enum_count
        else:
            value = value.replace('_LV_', '_').replace('LV_', '')
            for char in '0123456789':
                value = value.replace(char + 'U)', char + ')')
                value = value.replace(char + 'U ', char + ' ')
                value = value.replace(char + 'L ', char + ' ')
                value = value.replace(char + 'L)', char + ')')

            exec(f'{name} = {value}', enum_namespace)
            current_enum_count = enum_namespace[name]

            if value.isdigit():
                value = '0x' + hex(current_enum_count)[2:].upper()

        if type_:
            code = self.template1.format(name, type_, value)
            # py_enums.append(code)

            return name, type_, code

        return name, type_, self.template2.format(name, value)


class EnumeratorList(c_ast.EnumeratorList):

    def __iter__(self):
        if self.enumerators is not None:
            yield from self.enumerators


class Enum(c_ast.Enum):

    def gen_py(self):
        global current_enum_count

        current_enum_count = -1
        name = format_name(self.name)
        enumerators = []

        if name:
            t_name = find_int_type(name)

            if t_name is None:
                t_name = name[1:] if name.startswith('_') else name
        else:
            t_name = None

        if self.values is not None:
            for enum_item in self.values:
                e_name, e_type, e_code = enum_item.gen_py()

                if e_type is None:
                    if t_name is not None:
                        e_code = e_code.format(type=t_name)

                    elif name is not None:
                        e_code = e_code.format(type=name)

                enumerators.append(e_code)

        code = '\n'.join(enumerators)

        return name, None, code, 0


class TypeDecl(c_ast.TypeDecl):

    @property
    def _declname(self):
        return str(self.type)

    def gen_py(self):
        declname = format_name(self.declname)

        if isinstance(self.type, IdentifierType):
            return declname, self.type.gen_py()[-1], None, 0

        if isinstance(self.type, (Struct, Union)):
            name, type_, code = self.type.gen_py()

            if name is None and code is None and type_:
                return declname, type_, None, 0

            if code:
                if name is None:
                    code = code.replace('class None', f'class {declname}', 1)

                    def iter_nested(nest):
                        for nested in nest:
                            nested.fields.name = (
                                nested.fields.name.replace('None', declname)
                            )
                            iter_nested(nested.nested_structs)

                    self.type.fields.name = declname
                    iter_nested(self.type.nested_structs)

                    return declname, None, code, 0

                if name and declname and name != declname:
                    return declname, name, code, 0

            if not name:
                name = declname

            return name, type_, code, 0

        if isinstance(self.type, Enum):
            name, type_, code, _ = self.type.gen_py()

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

            return name, type_, code, 0

        raise RuntimeError(f'{str(declname)} : {str(type(self.type))}')


class IdentifierType(c_ast.IdentifierType):

    def gen_py(self):
        names = [get_py_type(name) for name in self.names]

        return (
            (None, None, None) if self.names is None
            else (None, None, ' '.join(str(name) for name in names))
        )

    def get_raw_type(self):
        if self.names is not None:
            return ' '.join(self.names)


class ParamList(c_ast.ParamList):

    def __getitem__(self, item):
        return self.params[item]

    def __iter__(self):
        if self.params is not None:
            yield from self.params


class EllipsisParam(c_ast.EllipsisParam):
    pass


def format_pointer(count, name):
    if name == 'void_t' and count > 0:
        count -= 1

    if 'List' not in name:
        return ('_ctypes.POINTER(' * count) + name + (')' * count)
    count = name.count('List')
    name = name.split('List[')[-1].split(']')[0]
    return ('_ctypes.POINTER(' * count) + name + (')' * count)


def format_byref(count, name):
    return f'_ctypes.byref({name})' if count else name


def get_normalized_type_name(type_):
    if type_.startswith('_'):
        if type_[1:] in py_struct_names:
            return type_[1:]
        if type_[1:] in py_enum_names:
            return type_[1:]
        if type_[1:] in py_int_type_names:
            return type_[1:]

    return type_


class CFunction(object):

    def __init__(self, name):
        self.name = name
        self.argtypes = []
        self.restype = None

    def append(self, arg):
        self.argtypes.append(arg)

    def __str__(self):
        if self.argtypes:
            argtypes = ',\n    '.join(arg.c_arg for arg in self.argtypes)

            argtypes = '\n    ' + argtypes + '\n'
        else:
            argtypes = ''

        res = f'_{lib_name}.{self.name}.argtypes = __CArgList({argtypes})\n'
        res += f'_{lib_name}.{self.name}.restype = {self.restype}'
        return res


class FunctionRetval(object):

    def __init__(self, type_, pointer_count):
        self.type = type_
        self.pointer_count = pointer_count

    @property
    def c_retval(self):
        if self.py_retval == 'None':
            return 'None'

        restype = (
            'void_t'
            if self.pointer_count and self.type in ('None', None)
            else self.type
        )
        restype = format_pointer(
            self.pointer_count,
            str(restype).replace('"', '')
        )
        return restype

    @property
    def py_retval(self):
        if self.type == 'void_t' and not self.pointer_count:
            return 'None'

        return self.type.replace('"', '')


callback_storage_names = []


class FunctionParam(object):
    callback_template = '''\
_{name}_callback_storage = {{}}


def _{name}_weakref_callback(ref):
    if ref in _{name}_callback_storage:
        del _{name}_callback_storage[ref]


'''

    callback_conversion_template = '''\
    if inspect.ismethod({param_name}):
        # This has to be done this way because WeakMethod is not hashable so 
        # it cannot be stored in a dictionary aand the __hash__ method is read 
        # only so it can only be added upon class creation. So we dynamically
        # construct the class pointing __hash__ to the methods __hash__  
        weakmethod = type(
            'weakmethod', 
            (weakref.WeakMethod,), 
            {{'__hash__': {param_name}.__hash__}}
        )
        ref = weakmethod({param_name}, _{name}_weakref_callback)
    elif inspect.isfunction({param_name}):
        ref = weakref.ref({param_name}, _{name}_weakref_callback)
    else:
        raise TypeError

    if ref not in _{name}_callback_storage:
        {param_name} = {param_type}({param_name})
        _{name}_callback_storage[ref] = {param_name}
    else:
        {param_name} = _{name}_callback_storage[ref]
'''

    conversion_template = '''\
    {param_name} = _convert_to_ctype(
        {param_name}, 
        _{lib_name}.{c_func_name}.argtypes.{param_name}
    )
'''

    def __init__(self, py_func_name, c_func_name, name, type_, pointer_count):
        self.py_func_name = py_func_name
        self.c_func_name = c_func_name
        self.name = name
        self.pointer_count = pointer_count

        if type_ is None:
            type_ = 'Any'

        type_ = type_.replace('"', '').replace('Any', 'void_t')
        type_ = type_.replace('None', 'void_t')

        self.type = type_

    @property
    def is_callback(self):
        for item in ('_cb_t', '_f_t', '_xcb_t'):
            if not str(self.type).endswith(item):
                continue
            return True
        return False

    @property
    def callback_storage(self):
        if not self.is_callback:
            return

        name = self.py_func_name.split('_')
        if name[0]:
            name = name[0]
        else:
            name = name[1]

        if name not in callback_storage_names:
            callback_storage_names.append(name)
            return self.callback_template.format(name=name)

    @property
    def py_arg(self):
        type_ = self.type
        if f'_type_{type_}' in int_typeing_names:
            type_ = f'_type_{type_}'

        return f'{self.name}: {type_}'

    @property
    def c_arg(self):
        type_ = format_pointer(self.pointer_count, self.type)
        return f'{self.name}={type_}'

    @property
    def c_conversion(self):
        if self.is_callback:
            name = self.py_func_name.split('_')
            if name[0]:
                name = name[0]
            else:
                name = name[1]

            return self.callback_conversion_template.format(
                param_name=self.name,
                name=name,
                param_type=self.type
            )

        return self.conversion_template.format(
            param_name=self.name,
            c_func_name=self.c_func_name,
            lib_name=lib_name
        )


class Function(object):
    return_attr = 'res = '
    return_conversion = '''
    return _convert_to_py_type(
        res, 
        _strip_pointer(_lib_lvgl.{c_func_name}.restype), 
        pointer_count=_pointer_count(_lib_lvgl.{c_func_name}.restype)
    )'''

    template = '''\
{callback_storage}def {func_name}({params}) -> {ret_type}:
{arg_conversions}
    {return_attr}_{lib_name}.{o_func_name}({param_names}){return_conversion}
'''

    get_return_conversion = '''
    
    for key, value in _{name}_callback_storage.items():
        if value == res:
            return key()
        
    return None'''

    def __init__(self, name, c_name):
        self.name = name
        self.c_name = c_name
        self.c_func = CFunction(c_name)
        self.params = []
        self.restype = None

    def append(self, name, type_, pointer_count=0):
        param = FunctionParam(
            self.name,
            self.c_name,
            name,
            type_,
            pointer_count
        )
        self.params.append(param)
        self.c_func.append(param)

    def __str__(self):
        self.c_func.restype = self.restype.c_retval

        callback_storage = None

        is_callback_func = False

        for param in self.params:
            callback_storage = param.callback_storage
            if param.is_callback and not is_callback_func:
                is_callback_func = True

            if callback_storage is not None:
                break

        if callback_storage is None:
            callback_storage = ''

        params = ', '.join(param.py_arg for param in self.params)

        if len(params) + len(self.name) > 40:
            params = ',\n    '.join(param.py_arg for param in self.params)
            params = '\n    ' + params + '\n'

        conversions = '\n'.join(param.c_conversion for param in self.params)
        param_names = ', '.join(param.name for param in self.params)

        if self.restype.py_retval == 'None':
            return_conversion = ''
            return_attr = ''
        elif self.name.endswith('_cb') or self.name.startswith('anim_path_'):
            if '_get_' in self.name:
                return_attr = self.return_attr

                name = self.name.split('_')
                if name[0]:
                    name = name[0]
                else:
                    name = name[1]

                return_conversion = self.get_return_conversion.format(name=name)

            elif '_set_' in self.name:
                return_conversion = self.return_conversion.format(c_func_name=self.c_name)
                return_attr = self.return_attr
            else:
                return_conversion = self.return_conversion.format(c_func_name=self.c_name)
                return_attr = self.return_attr
                conversions = ''

        elif is_callback_func:
            if 'get_' in self.name or '_get' in self.name:
                return_attr = self.return_attr

                name = self.name.split('_')
                if name[0]:
                    name = name[0]
                else:
                    name = name[1]

                return_conversion = self.get_return_conversion.format(name=name)

            else:
                return_conversion = self.return_conversion.format(c_func_name=self.c_name)
                return_attr = self.return_attr
        else:
            return_conversion = self.return_conversion.format(c_func_name=self.c_name)
            return_attr = self.return_attr

        tmpl1 = str(self.c_func)

        tmpl2 = self.template.format(
            callback_storage=callback_storage,
            func_name=self.name,
            params=params,
            ret_type=self.restype.py_retval,
            arg_conversions=conversions,
            return_attr=return_attr,
            lib_name=lib_name,
            o_func_name=self.c_name,
            param_names=param_names,
            return_conversion=return_conversion
        )
        return tmpl1 + '\n\n\n' + tmpl2


class FuncDecl(c_ast.FuncDecl):

    def __init__(self, args, type):  # NOQA
        self.args = args
        self.type = type

    @property
    def _declname(self):
        return self.type._declname  # NOQA

    def get_types(self):
        return [format_name(arg._declname) for arg in self.args]  # NOQA

    def __getitem__(self, item):
        return self.args[item]

    def gen_py(self):
        args = self.args or []

        if isinstance(self.type, (TypeDecl, PtrDecl)):
            name, type_, code, r_ptr = self.type.gen_py()
        else:
            raise RuntimeError(str(type(self.type)))

        if type_ in ('None', None):
            type_ = 'void_t'

        r_type = self.type
        while isinstance(r_type, PtrDecl):
            r_type = r_type.type

        declname = r_type.declname  # NOQA

        possible_callback = False

        if declname in export_symbols:
            o_func_name = declname
        elif f'py_{declname}' in export_symbols:
            o_func_name = f'py_{declname}'
        else:
            o_func_name = declname
            possible_callback = True

        if name.startswith('_txt_encoded'):
            return None, None, None, 0

        func = Function(name, o_func_name)

        for param in args:
            if isinstance(param, (Decl, Typename)):
                param_name = param.name
                p_name, p_type, code, p_ptr = param.gen_py()
            elif isinstance(param, EllipsisParam):
                return None, None, None, 0
            else:
                raise RuntimeError(str(type(param)))

            if param_name is None:
                if p_type not in ('None', 'void_t'):
                    return None, None, None, 0

                continue

            if p_type is None:
                print('nested callback func:', param, type(param), p_name, name, o_func_name)
                continue

            if 'va_list' in p_type:
                return None, None, None, 0

            func.append(p_name, p_type, p_ptr)

        if possible_callback:
            if name in py_callback_names:
                return None, None, None, 0

            print('CALLBACK:', name, o_func_name)
            return None, None, None, 0

        func.restype = FunctionRetval(type_, r_ptr)

        return name, type_, str(func), r_ptr


class Typename(c_ast.Typename):

    def get_type(self):
        return self.type._declname  # NOQA

    def gen_py(self):
        s_name = format_name(self.name)

        if isinstance(self.type, (TypeDecl, PtrDecl)):
            name, type_, code, ptr = self.type.gen_py()
            if name:
                return name, type_, code, ptr

            return s_name, type_, code, ptr

        raise RuntimeError(f'{str(s_name)} : {str(type(self.type))}')


class PtrDecl(c_ast.PtrDecl):

    @property
    def _declname(self):
        return self.type._declname  # NOQA

    def byref(self, name):  # NOQA
        return f'_ctypes.byref({name})'

    @property
    def pointer(self):
        return f'_ctypes.POINTER({self.type._declname})'  # NOQA

    def get_types(self):
        if isinstance(self.type, (PtrDecl, FuncDecl)):
            return self.type.get_types
        return []

    def gen_py(self):
        if isinstance(self.type, (TypeDecl, FuncDecl, PtrDecl)):
            name, type_, code, ptr = self.type.gen_py()
            ptr += 1
            return name, type_, code, ptr

        raise RuntimeError(str(type(self.type)))


class FuncDef(c_ast.FuncDef):

    def gen_py(self):
        return self.decl.gen_py()


class StructField(object):

    def __init__(self, name, bitsize, type_):
        self.name = name
        self.bitsize = bitsize
        self.type = type_

    def __str__(self):
        real_type = get_type_from_py_type(self.type)

        if real_type is None:
            real_type = 'void_t'

        if not real_type.startswith('_') and f'_{real_type}' in py_struct_names:
            type_ = f'_{real_type}'
        elif not real_type.startswith('_') and real_type in py_typedef_names:
            for t_def in py_typedefs:
                if isinstance(t_def, TDef) and t_def.name == real_type and t_def.type is not None:
                    type_ = t_def.type
                    break
            else:
                type_ = real_type
        else:
            type_ = real_type

        if real_type != self.type:
            type_ = self.type.replace(real_type, type_)

        if self.bitsize is None:
            return f"    ('{self.name}', {type_})"

        return f"    ('{self.name}', {type_}, {self.bitsize.value})"


class StructFields(object):
    template = """\
{name}._fields_ = [
{fields}
]
"""

    def __init__(self, name):
        self.name = name
        self.fields = []

    def append(self, field):
        self.fields.append(field)

    def replace(self, old_name, new_name):
        for field in self.fields:
            if field.name == old_name:
                field.name = new_name
                return

    def __str__(self):
        fields = ',\n'.join(
            str(field).replace('None.', self.name + '.')
            for field in self.fields
        )
        return self.template.format(name=self.name, fields=fields)


class Struct(c_ast.Struct):
    _base_type = 'Structure'

    property_template = '''\
        @property
        def {field_name}(self) -> {field_type}:  # NOQA
            ...

        @{field_name}.setter
        def {field_name}(self, value: {field_type}):
            ...'''

    param_eval = '''\
        if {param_name} != _DefaultArg:
            kwargs['{param_name}'] = {param_name}'''
    param_template = (
        '{field_name}: Optional[{field_type}] = _DefaultArg'
    )

    special_types_template = '''\
        '{param_name}': {param_type}'''

    template = '''\
class {struct_name}(_{base_type}): {pack}{nested_structs}
    _special_types_ = {{{special_types}}}
    
    def __init__({params}):
        _{base_type}.__init__(self)
        kwargs = {{}}
{param_evals}
        for key, value in kwargs.items():
            setattr(self, key, value)
        
    if TYPE_CHECKING:
{py_properties}
'''

    def __init__(self, *args, **kwargs):
        self.fields = None
        self.nested_structs = []

        super().__init__(*args, **kwargs)

    def gen_py(self):
        s_name = format_name(self.name)

        params = []
        nested_structs = []
        py_properties = []
        param_names = []
        fields = []
        param_evals = []
        special_types = []

        if self.decls is None:
            return None, s_name, None

        for field in self.decls:
            if isinstance(field, Decl):
                name, type_, code, ptr = field.gen_py()

                if isinstance(field.type, PtrDecl):
                    if code and code.startswith('def '):
                        if isinstance(field.type.type, FuncDecl):
                            continue

                elif isinstance(field.type, TypeDecl):
                    if isinstance(field.type.type, (Union, Struct)) and code:
                        code = (
                            '\n'.join(
                                f'    {line}'
                                for line in code.rstrip().split('\n')
                            )
                        )
                        code = code.replace(field.name, f'_{field.name}')
                        field.type.type.fields.name = (
                            f'{s_name}._{field.type.type.fields.name}'
                        )
                        for nested in field.type.type.nested_structs:
                            nested.fields.name = (
                                f'{s_name}._{nested.fields.name}'
                            )

                        self.nested_structs.append(field.type.type)

                        size = f"    setattr(_{field.name}, '__SIZE__', "
                        size += f"_ctypes.sizeof(_{field.name}))"

                        nested_structs.append(code + f'\n\n{size}')
                        # field_names.append(name)
                        param_names.append(f'{field.name}={field.name}')
                        p_field = f'{field.name}: Optional[_{field.name}]'
                        p_field += ' = _DefaultArg'
                        params.append(p_field)
                        field.name = f'{s_name}._{field.name}'

                        py_properties.append(
                            self.property_template.format(
                                field_name=name,
                                field_type=f'_{name}'
                            )
                        )
                        fields.append(StructField(name, None, f'{s_name}._{name}'))
                        param_evals.append(self.param_eval.format(
                            param_name=name
                        ))

                        continue

                if not code:
                    code = type_

                if type_ in (None, 'None'):
                    type_ = 'Any'

                if not name:
                    raise RuntimeError(f'{repr(type_)} : {repr(code)}')

                for item in ('Any', 'List', 'bool'):
                    if type_.startswith(item):
                        break
                else:
                    if '"' not in type_:
                        type_ = '"' + type_ + '"'

                param_names.append(name + '=' + name)

                if type_.replace('"', '').replace('Any', 'void_t') == 'va_list':
                    return None, None, None

                prop_type = type_
                if f'_type_{prop_type}' in int_typeing_names:
                    prop_type = f'_type_{prop_type}'
                else:
                    for t in int_typeing_names:
                        if t[5:] in prop_type:
                            prop_type.replace(t[5:], t)
                            break
                        if t[6:] in prop_type:
                            prop_type.replace(t[6:], t)
                            break

                py_properties.append(
                    self.property_template.format(
                        field_name=name,
                        field_type=prop_type
                    )
                )
                fields.append(
                    StructField(
                        name,
                        field.bitsize,
                        format_pointer(
                            ptr,
                            type_.replace('"', '').replace('Any', 'void_t')
                        )
                    )
                )
                param_evals.append(
                    self.param_eval.format(param_name=name)
                )

                if type_.startswith('List'):
                    special_types.append(
                        self.special_types_template.format(
                            param_name=name,
                            param_type='list'
                        )
                    )

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

        self.fields = StructFields(s_name)

        for field in fields:
            self.fields.append(field)

        struct_fields.append(self.fields)

        nested_structs = (
            '\n{0}\n'.format('\n\n'.join(nested_structs))
            if nested_structs else ''
        )
        params.insert(0, 'self')
        if len(', '.join(params)) > 40:
            params = '\n        {0}\n    '.format(', \n        '.join(params))
        else:
            params = ', '.join(params)

        py_properties = '\n{0}'.format('\n\n'.join(py_properties))

        special_types = ',\n'.join(special_types)
        if special_types:
            special_types = '\n' + special_types + '\n    '

        if pragma_pack is None:
            pack = ''
        else:
            pack = f'\n    _pack_ = {pragma_pack}'

        return s_name, None, self.template.format(
            pack=pack,
            base_type=self._base_type,
            struct_name=s_name,
            nested_structs=nested_structs,
            py_properties=py_properties,
            param_evals='\n'.join(param_evals),
            params=params,
            special_types=special_types
        )


class Union(Struct):
    _base_type = 'Union'


class ArrayDecl(c_ast.ArrayDecl):

    @property
    def _declname(self):
        return self.type._declname  # NOQA

    def gen_py(self):
        if isinstance(self.type, TypeDecl):
            name, type_, code, ptr = self.type.gen_py()
            if code:
                return name, f'List[{code}]', None, ptr

            return name, f'List[{type_}]', None, ptr

        if isinstance(self.type, PtrDecl):
            name, type_, code, ptr = self.type.gen_py()

            if name is None:
                return type_, f'List[{code}]', None, ptr

            if type_ is None:
                type_ = 'Any'

            return name, f'List[{type_}]', None, ptr

        if isinstance(self.type, ArrayDecl):
            name, type_, _, ptr = self.type.gen_py()
            return name, f'List[{type_}]', None, ptr

        raise RuntimeError(str(type(self.type)))


class CatchAll:

    def __call__(self, **_):
        return self

    @property
    def children(self):
        def wrapper():
            return []

        return wrapper

    def gen_py(self):  # NOQA
        return None, None, None


class TDef(object):
    template = '''\
{name} = {type}'''

    def __init__(self, name, type_):
        self.name = name
        self.type = type_

    def __str__(self):
        return self.template.format(name=self.name, type=self.type)


def get_type_from_py_type(type_):
    type_ = type_.split('POINTER(')[-1]
    type_ = type_.split(')')[0]
    return type_


class CBFunc(object):

    def __init__(self, name, restype, param_types):
        self.name = name
        self.restype = restype
        self.param_types = param_types

    def __str__(self):
        real_restype = get_type_from_py_type(self.restype)

        if self.restype == 'None':
            restype = self.restype
        elif (
            not real_restype.startswith('_') and
            f'_{real_restype}' in py_struct_names
        ):
            restype = f'_{real_restype}'
        elif (
            not real_restype.startswith('_') and
            real_restype in py_typedef_names
        ):
            for t_def in py_typedefs:
                if isinstance(t_def, TDef) and t_def.name == real_restype:
                    restype = t_def.type
                    break
            else:
                restype = real_restype
        else:
            restype = real_restype

        if real_restype == 'void_t':
            restype = real_restype
        elif real_restype != self.restype:
            restype = self.restype.replace(real_restype, restype)

        param_types = []
        for type_ in self.param_types:
            temp_type = type_
            real_type = get_type_from_py_type(type_)

            if real_type is None:
                real_type = 'void_t'

            if (
                not real_type.startswith('_') and
                f'_{real_type}' in py_struct_names
            ):
                type_ = f'_{real_type}'
            elif (
                not real_type.startswith('_') and
                real_type in py_typedef_names
            ):
                for t_def in py_typedefs:
                    if isinstance(t_def, TDef) and t_def.name == real_type and t_def.type is not None:
                        type_ = t_def.type
                        break
                else:
                    type_ = real_type
            else:
                type_ = real_type

            if temp_type != real_type:
                type_ = temp_type.replace(real_type, type_)

            param_types.append(type_)

        res = f"{self.name} = CFUNCTYPE({restype}, "
        res += f"{', '.join(param_types)})"
        if len(res) > 80:
            res = f"{self.name} = CFUNCTYPE(\n"
            res += f"    {restype},\n"
            param_types = ',\n'.join('    ' + p for p in param_types)
            res += param_types
            res += '\n)'

        return res


int_typeing_names = [
    '_type_float_t',
    '_type_string_t',
    '_type_bool_t',
    '_type_uint8_t',
    '_type_uint16_t',
    '_type_uint32_t',
    '_type_uint64_t',
    '_type_int8_t',
    '_type_int16_t',
    '_type_int32_t',
    '_type_int64_t',
    '_type_int_t',
    '_type_char_t',
    '_type_uintptr_t',
    '_type_intptr_t',
    '_type_size_t',
]


class RootTypedef(Typedef):

    def gen_py(self):
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

                    name = s_type.declname  # NOQA

                    for item in ('_cb_t', '_f_t', '_xcb_t'):
                        if item not in name:
                            continue

                        if name.replace('lv_', '', 1) in py_callback_names:
                            return

                        try:
                            ret_type = get_py_type(s_type.type.names[0])
                        except:  # NOQA
                            ret_type = get_py_type(s_type.type.name)

                        if ptr and ret_type in (None, 'None'):
                            ret_type = 'void_t'

                        ret_type = str(ret_type).replace('"', '')

                        ret_type = format_pointer(ptr, ret_type)

                        param_names = []
                        params = []
                        param_types = []

                        for param in self.type.type.args.params:
                            p_ptr = 0

                            if isinstance(param, Typename):
                                p_type = param.type
                                param_name = param.name

                                if isinstance(p_type, PtrDecl):
                                    p_type = p_type.type.type
                                    p_ptr = 1

                                    if isinstance(p_type, IdentifierType):
                                        param_type = get_py_type(
                                            p_type.names[0]
                                        )
                                    elif isinstance(p_type, Struct):
                                        param_type = get_py_type(p_type.name)
                                    else:
                                        raise RuntimeError(str(type(p_type)))

                                elif isinstance(p_type, TypeDecl):
                                    p_type = p_type.type
                                    param_type = get_py_type(p_type.names[0])
                                else:
                                    raise RuntimeError(str(type(p_type)))

                            elif isinstance(param, Decl):
                                p_type = param.type
                                param_name = param.name

                                p_ptr = 0
                                while isinstance(p_type, PtrDecl):
                                    p_type = p_type.type
                                    p_ptr += 1

                                if isinstance(p_type, IdentifierType):
                                    param_type = get_py_type(
                                        p_type.names[0]
                                    )

                                elif isinstance(p_type, ArrayDecl):
                                    if p_ptr == 0:
                                        p_ptr = 1

                                    param_type = get_py_type(
                                        p_type.type.type.names[0]
                                    )

                                elif isinstance(p_type, TypeDecl):
                                    p_type = p_type.type

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
                                else:
                                    raise RuntimeError(str(type(p_type)))

                            else:
                                raise RuntimeError(str(type(param)))

                            if p_ptr and param_type in ('None', None):
                                param_type = 'void_t'

                            # if param_type.startswith('_'):
                            #     param_type = param_type[1:]
                            #
                            # elif param_type.startswith('"_'):
                            #     param_type = '"' + param_type[2:]

                            param_types.append(
                                format_pointer(
                                    p_ptr,
                                    param_type.replace('"', '')
                                )
                            )
                            param_names.append(param_name)
                            params.append(f'{param_name}: {param_type}')

                        param_types = [
                            str(pt).replace('"', '') for pt in param_types
                        ]

                        temp = CBFunc(
                            get_py_type(name).replace('"', ''),
                            ret_type,
                            param_types
                        )

                        name = get_py_type(name).replace('"', '')

                        if name not in func_pointer_names:
                            func_pointer_names.append(name)
                            func_pointers.append(temp)

                        return

        t_name = format_name(self.name)
        print(type(self.type))
        name, type_, code, ptr = self.type.gen_py()

        if name == 'vaformat_t':
            return

        if isinstance(self.type, TypeDecl):
            if type_:
                type_ = type_.replace('"', '')

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
                        size = f"setattr({name}, '__SIZE__', "
                        size += f"_ctypes.sizeof({name}))"
                        py_struct_sizes.append(size)

                        if code.startswith('class ' + type_):
                            if name not in py_typedef_names:
                                py_typedef_names.append(name)
                                py_typedefs.append(
                                    TDef(name, type_)
                                )
                        return

                    elif (
                        name and not type_ and
                        name not in py_struct_names
                    ):
                        py_struct_names.append(name)
                        py_structs.append(code)
                        size = f"setattr({name}, '__SIZE__', "
                        size += f"_ctypes.sizeof({name}))"
                        py_struct_sizes.append(size)
                        return

                    elif (
                        type_ and not name and
                        type_ not in py_struct_names
                    ):
                        py_struct_names.append(type_)
                        py_structs.append(code)
                        size = f"setattr({type_}, '__SIZE__', "
                        size += f"_ctypes.sizeof({type_}))"
                        py_struct_sizes.append(size)
                        return

                elif '=' in code and name:
                    if name and type_ and name == type_:
                        type_ = 'int_t'

                        if name not in py_int_type_names:
                            tdef = self.template.format(
                                typedef_name=name,
                                typedef_type=type_
                            )
                            py_int_type_names.append(name)
                            py_int_types.append(tdef)

                        int_type_name = f'_type_{name}'

                        if int_type_name not in int_typeing_names:
                            int_type = (
                                f'_type_{name} = Union[{name}, {type_}, int]'
                            )

                            int_typeing_names.append(int_type_name)
                            int_typing.append(int_type)

                        return

                    elif name and type_:
                        if name not in py_int_type_names and type_ in int_types:
                            tdef = self.template.format(
                                typedef_name=name,
                                typedef_type=type_
                            )
                            py_int_type_names.append(name)
                            py_int_types.append(tdef)

                            int_type = (
                                f'_type_{name} = Union[{name}, {type_}, int]'
                            )
                            int_typing.append(int_type)
                            return

                if (
                    t_name and
                    type_ and
                    t_name != type_ and
                    type_ not in int_types and
                    t_name not in (
                        py_callback_names +
                        py_typedef_names +
                        py_int_type_names
                    )
                ):
                    py_typedef_names.append(t_name)
                    py_typedefs.append(TDef(t_name, type_))
                    return

                if (
                    name and type_ and t_name and
                    name == t_name and name != type_ and not code
                ):
                    if type_ in int_types:
                        if name not in py_int_type_names:
                            tdef = self.template.format(
                                typedef_name=name,
                                typedef_type=type_
                            )
                            py_int_type_names.append(name)
                            py_int_types.append(tdef)

                            int_type = (
                                f'_type_{name} = Union[{name}, {type_}, int]'
                            )
                            int_typing.append(int_type)

                        return
            elif (
                name and
                type_ and
                t_name and
                t_name == name and
                type_.replace('"', '') != name
            ):
                type_ = type_.replace('"', '')

                if type_ in int_types:
                    if name not in py_int_type_names:
                        tdef = self.template.format(
                            typedef_name=name,
                            typedef_type=type_.replace('"', '')
                        )

                        py_int_type_names.append(name)
                        py_int_types.append(tdef)

                        int_type = f'_type_{name} = Union[{name}, {type_}, int]'
                        int_typing.append(int_type)
                    return

            if type_ != t_name and t_name not in py_typedef_names:
                py_typedef_names.append(t_name)
                py_typedefs.append(TDef(t_name, type_))
                return

            if name and t_name and type_ and name == t_name == type_:
                return

        elif isinstance(self.type, ArrayDecl):
            if code:
                if not t_name:
                    t_name = name

                if t_name not in py_typedef_names + py_int_type_names:
                    code = '{name}: {type} = ...'.format(name=t_name, type=code)

                    py_typedef_names.append(t_name)
                    py_typedefs.append(code)
            else:
                array_type = type_.split(
                    '[', 1
                )[-1][:-1].replace('"', '').strip()

                code = '{name}: {type} = ({array_type} * {dim})()'.format(
                    name=name,
                    type=type_,
                    array_type=array_type,
                    dim=generator.visit(self.type.dim)
                )
                py_typedef_names.append(name)
                py_typedefs.append(code)
                return

        elif isinstance(self.type, PtrDecl):
            if (
                name not in
                py_type_names[:] +
                py_typedef_names[:] +
                py_func_names +
                py_int_type_names[:]
            ):
                py_typedef_names.append(name)
                py_typedefs.append(code)

            if t_name and name and t_name != name:
                if (
                    t_name not in
                    py_callback_names[:] +
                    py_typedef_names[:] +
                    py_int_type_names[:]
                ):
                    py_typedef_names.append(t_name)
                    py_typedefs.append(
                        TDef(t_name, name)
                    )
            return

        print(str(type(self.type)))
        raise RuntimeError


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
    'uintptr_t': 'int_t',
    'intptr_t': 'int_t',
    'int_t': None,
    'bool_t': None
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
    variable_template = '''\
__{py_name}_pointer = _ctypes.POINTER({c_type})
{py_name} = __{py_name}_pointer.in_dll(_lib_lvgl, "{c_name}")'''

    def gen_py(self):
        d_name = format_name(self.name)

        if isinstance(self.type, Enum):
            name, type_, code, _ = self.type.gen_py()

            if code:
                def _check_code(c):
                    if ')\n_' in c:
                        c = [f'_{item})' for item in c.split(')\n_')]
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
                        int_type = f'_type_{name} = Union[{name}, {type_}, int]'
                        int_typing.append(int_type)

                if _check_code(code):
                    py_enums.append(code)

        elif isinstance(self.type, FuncDecl):
            name, type_, code, ptr = self.type.gen_py()
            if code:
                if not name and d_name:
                    name = d_name

                if name not in py_callback_names + py_func_names:
                    py_func_names.append(name)
                    py_funcs.append(code)

        elif isinstance(self.type, TypeDecl):
            name, type_, code, ptr = self.type.gen_py()

            if self.name in exported_variable_names:
                c_name = 'py_' + self.name
                code = self.variable_template.format(
                    py_name=d_name,
                    c_type=type_.replace('"', ''),
                    c_name=c_name
                )

                if d_name not in py_type_names:
                    py_type_names.append(d_name)
                    py_types.append(code)

                return

            if code:
                if not name and d_name:
                    name = d_name

                code = '{name}: {type} = ...'.format(name=name, type=code)

                if name not in py_type_names:
                    py_type_names.append(name)
                    py_types.append(code)

        elif isinstance(self.type, PtrDecl):
            name, type_, code, ptr = self.type.gen_py()
            if code:
                if not name and d_name:
                    name = d_name

                if name not in py_callback_names + py_func_names:
                    py_func_names.append(name)
                    py_funcs.append(code)

        elif isinstance(self.type, Struct):
            name, type_, code = self.type.gen_py()
            if code:
                if not name and d_name:
                    name = d_name
                    self.type.fields.replace('None', name)
                    self.type.fields.name = (
                        self.type.fields.name.replace('None', name)
                    )
                    for nested in self.type.nested_structs:
                        nested.fields.name = (
                            nested.fields.name.replace('None.', name)
                        )

                if name not in py_struct_names:
                    py_struct_names.append(name)
                    py_structs.append(code)

                    size = f"setattr({name}, '__SIZE__', "
                    size += f"_ctypes.sizeof({name}))"
                    py_struct_sizes.append(size)

        else:
            raise RuntimeError(str(type(self.type)))


class RootFuncDef(FuncDef):

    def gen_py(self):
        if self.param_decls is not None:
            raise RuntimeError(str(type(self.param_decls)))

        if isinstance(self.decl, Decl):
            name, type_, code, ptr = self.decl.gen_py()

            if not name:
                name = type_

            if code:
                if name not in py_callback_names + py_func_names:
                    py_func_names.append(name)
                    py_funcs.append(code)

        else:
            raise RuntimeError(str(type(self.decl)))


class Pragma(c_ast.Pragma):

    def __init__(self, string, coord=None):
        super().__init__(string, coord)

    def gen_py(self):
        print('Pragma: ', self.string, self.coord)


class RootPragma(Pragma):

    def __init__(self, string, coord=None):
        super().__init__(string, coord)

    def gen_py(self):
        global pragma_pack

        print(self.string)
        if '(' not in self.string:
            return

        command, args = self.string.split('(', 1)
        if command == 'pack':
            args = args.split(')', 1)[0]
            args = [arg.strip() for arg in args.split(',')]
            if args[0] == 'pop':
                pragma_pack = None
            elif args[0] == 'push':
                pragma_pack = args[1]


class StaticAssert(c_ast.StaticAssert):

    def __init__(self, cond, message, coord=None):
        super().__init__(cond, message, coord)

    def gen_py(self):
        print('StaticAssert: ', self.cond, self.message, self.coord)


class RootStaticAssert(StaticAssert):

    def __init__(self, cond, message, coord=None):
        super().__init__(cond, message, coord)

    def gen_py(self):
        print('RootStaticAssert: ', self.cond, self.message, self.coord)



lib_name = 'lib_lvgl'
func_decls = []
func_restypes = []
export_symbols = []
pointer_decls = []
func_defs = []
struct_fields = []
callbacks = []
func_pointers = []
func_pointer_names = []
int_typing = []

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

py_struct_sizes = []


class GlobalsWrapper(dict):

    def __init__(self):
        self.globs = globals()
        dict.__init__(self)

    def __getitem__(self, item):
        if item in self.globs:
            return self.globs[item]

        return getattr(c_ast, item)


# this is some monkey patching code to flatten the output when printing a node.
def patch_pycparser():
    def _repr(obj):
        if isinstance(obj, list):
            return '[' + (', '.join(_repr(item) for item in obj)) + ']'
        else:
            return repr(obj)

    def cls_repr(self):
        result = f'{self.__class__.__name__}('
        attrs = []

        for name in self.__slots__[:-2]:
            attrs.append(name + '=' + _repr(getattr(self, name)))

        result += ', '.join(attrs)
        result += ')'

        return result

    ast = sys.modules['pycparser.c_ast']

    setattr(ast.Node, '__repr__', cls_repr)  # NOQA



def run(output_path, ast):
    global py_enums
    global py_int_types
    global py_callbacks
    global py_funcs
    global py_structs
    global py_types
    global struct_fields
    global func_pointers

    patch_pycparser()

    c_output = generator.visit(ast)

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
        node = eval(f'Root{str(child)}', globs)
        node.gen_py()

    base_path = os.path.dirname(__file__)

    template = open(os.path.join(base_path, 'lvgl.template.py'), 'r').read()
    template = template.replace('{', '{{').replace('}', '}}')
    template = template.replace("['~", '{').replace("~']", '}')

    with open(os.path.join(output_path, '__init__.py'), 'w') as f:
        f.write(
            template.format(
                int_types='\n\n'.join(str(item) for item in py_int_types),
                int_typing='\n'.join(str(item) for item in int_typing),
                enums='\n\n'.join(str(item) for item in py_enums),
                structs='\n\n'.join(str(item) for item in py_structs),
                struct_fields='\n\n'.join(str(item) for item in struct_fields),
                # func_restypes='\n\n'.join(func_restypes),
                typedefs='\n'.join(str(item) for item in py_typedefs),
                func_pointers='\n'.join(str(item) for item in func_pointers),
                functions='\n\n'.join(str(item) for item in py_funcs),
                py_struct_sizes='\n'.join(py_struct_sizes),
                # pointer_decls='\n'.join(pointer_decls)
                py_types='\n\n'.join(py_types)
            )
        )

    return c_output
