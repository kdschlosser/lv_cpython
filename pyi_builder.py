import sys

from pycparser import c_generator, c_ast

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

    elif name.endswith('_t'):
        if name.startswith('uint') or name.startswith('int'):
            return 'int'
        if name.startswith('size'):
            return 'int'

    elif name.startswith('void'):
        return 'None'
    elif name.startswith('float'):
        return 'float'
    elif name.startswith('char'):
        return 'str'

    return name


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
    def __init__(self, name, quals, align, storage, funcspec, type, init, bitsize):  # NOQA
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

    def get_ast(self):
        return c_ast.Decl(
            self.name,
            self.quals,
            self.align,
            self.storage,
            self.funcspec,
            self.type.get_ast(),
            self.init,
            self.bitsize
        )

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


pyi_typedef_template = '''\
class {typedef_name}({typedef_type}):
    pass'''


class Typedef:
    def __init__(self, name, quals, storage, type):  # NOQA
        self.name = name
        self.type = type
        self.quals = quals
        self.storage = storage

    def get_ast(self):
        return c_ast.Typedef(
            self.name, 
            self.quals, 
            self.storage, 
            self.type.get_ast()
        )

    def gen_pyi(self):
        s_name = format_name(self.name)

        name, type_, code = self.type.gen_pyi()

        if code and code.startswith('class'):
            if name is None and type_ is None:
                if s_name and code.startswith('class None'):
                    code = code.replace('class None', 'class ' + s_name, 1)

                type_ = name = s_name

            if name and s_name and s_name != name:
                code += '\n\n\nclass {0}({1}):\n    pass'.format(
                    s_name,
                    name
                )

            return name, type_, code

        if code and ': int = ' in code:
            if name:
                code += '\n\n\nclass {0}(int):\n    pass'.format(name)

                if s_name and s_name != name:
                    code += '\n\n\nclass {0}({1}):\n    pass'.format(
                        s_name,
                        name
                    )
                    return s_name, name, code

                return name, 'int', code

        return s_name, name, code

    def __str__(self):
        if self.name:
            return self.name
        return ''


py_enums = []
py_enum_names = []


class Enumerator:
    def __init__(self, name, value):  # NOQA
        self.name = name
        self.value = value

    def get_ast(self):
        return Enumerator(self.name, c_ast.Constant('int', 1))

    def gen_pyi(self):
        name = format_name(self.name)

        if name not in py_enum_names:
            py_enums.append('{0} = _lib_lvgl.lib.{1}'.format(name, self.name))

        return name, 'int', '{0}: int = ...'.format(name)


class EnumeratorList:
    def __init__(self, enumerators):
        self.enumerators = enumerators

    def get_ast(self):

        if self.enumerators is None:
            enumerators = None

        else:
            enumerators = []
            for enumerator in self.enumerators:
                enumerators.append(enumerator.get_ast())

        return c_ast.EnumeratorList(enumerators)

    def __iter__(self):
        if self.enumerators is not None:
            for item in self.enumerators:
                yield item


pyi_enum_template = '{enum_name} = int'


class Enum:

    def __init__(self, name, values):
        self.name = name
        self.values = values

    def get_ast(self):
        if self.values is not None:

            return c_ast.Enum(
                self.name,
                self.values.get_ast()
            )

        return c_ast.Enum(
            self.name,
            self.values
        )

    def gen_pyi(self):
        name = format_name(self.name)
        enumerators = []

        if self.values is not None:
            for enum_item in self.values:
                enumerators.append(enum_item.gen_pyi()[-1])

        code = '\n'.join(enumerators)

        if name:
            return name, 'int', code

        else:
            return None, None, code

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

    def get_ast(self):
        return c_ast.TypeDecl(
            self._declname,
            self.quals,
            self.align,
            self.type.get_ast()
        )

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

                    return declname, None, code

                if name and declname and name != declname:
                    return declname, name, code

            if not name:
                name = declname

            return name, type_, code

        if isinstance(self.type, Enum):
            name, type_, code = self.type.gen_pyi()

            if declname:
                if not name:
                    name = declname
                    type_ = 'int'
                else:
                    type_ = name
                    name = declname

            return name, type_, code

        raise RuntimeError(str(declname) + ' : ' + str(type(self.type)))

    def __str__(self):
        if self._declname:
            return self._declname
        return ''


class IdentifierType:

    def __init__(self, names):
        self.names = names

    def get_ast(self):
        return c_ast.IdentifierType(self.names)

    def gen_pyi(self):
        if self.names is None:
            return None, None, None

        return None, None, str(self)

    def __str__(self):
        if self.names is not None:
            names = [get_py_type(name) for name in self.names]

            return ' '.join(names)
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

    def get_ast(self):
        if self.params is None:
            return c_ast.ParamList(None)

        params = []
        for param in self.params:
            params.append(param.get_ast())

        return c_ast.ParamList(params)


class EllipsisParam:

    def __init__(self, **_):
        pass


pyi_funcdecl_param_template = '{param_name}: {param_type}'
pyi_funcdecl_template = """\
def {func_name}({params}) -> {ret_type}:
    ..."""


class FuncDecl:
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

    def get_ast(self):
        if self.args is None:
            return c_ast.FuncDecl(None, self.type.get_ast())

        return c_ast.FuncDecl(self.args.get_ast(), self.type.get_ast())

    def gen_pyi(self):
        args = self.args or []

        if isinstance(self.type, (TypeDecl, PtrDecl)):
            name, type_, code = self.type.gen_pyi()
        else:
            raise RuntimeError(str(type(self.type)))

        params = []

        for param in args:
            if isinstance(param, (Decl, Typename)):
                param_name = param.name
                p_name, p_type, _ = param.gen_pyi()
            elif isinstance(param, EllipsisParam):
                params.append('*args')
                break
            else:
                raise RuntimeError(str(type(param)))

            if param_name is None:
                continue

            if param_name == 'user_data':
                continue

            params.append(
                pyi_funcdecl_param_template.format(
                    param_name=p_name,
                    param_type=p_type
                )
            )

        params = ', '.join(params)

        return name, type_, pyi_funcdecl_template.format(
            func_name=name,
            params=params,
            ret_type=type_
        )


class Typename:
    def __init__(self, name, quals, align, type):  # NOQA
        self.name = name
        self.type = type
        self.quals = quals
        self.align = align

    def get_type(self):
        return self.type.declname

    def get_ast(self):
        return c_ast.Typename(
            self.name, 
            self.quals, 
            self.align, 
            self.type.get_ast()
        )

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

    def get_ast(self):
        return c_ast.PtrDecl(self.quals, self.type.get_ast())

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

    def get_ast(self):
        return c_ast.FuncDef(self.decl.get_ast(), None, None)

    def gen_pyi(self):
        return self.decl.gen_pyi()


pyi_struct_param_template = '{field_name}: Optional[{field_type}] = None'
pyi_struct_field_template = '    {field_name}: {field_type} = ...'

pyi_struct_template = '''\
class {struct_name}:{fields}{nested_structs}
    def __init__({params}):
        ...'''


callback_template = '''\
@_lib_lvgl.ffi.def_extern(name='py_lv_{func_name}')
def __{func_name}_callback_func(*args):
    return {func_name}._callback_func(*args)


class _{func_name}(_CallbackWrapper):

    def __call__(self, func):
        return _{func_name}(self.ctype, func)


{func_name} = _{func_name}('lv_{func_name}', None)

'''

pyi_callback_template = '''
class {func_name}:
    def __init__(self, func: Callable[{param_types}, {ret_type}]):
        ...'''


class Struct:
    def __init__(self, name, decls):
        self.name = name
        self.decls = decls

    def get_ast(self):
        if self.decls is None:
            return c_ast.Struct(self.name, None)

        decls = []
        for decl in self.decls:
            decls.append(decl.get_aast())
        return c_ast.Struct(self.name, decls)

    def gen_pyi(self):
        s_name = format_name(self.name)

        params = []
        fields = []
        nested_structs = []

        if self.decls is None:
            return None, s_name, None

        field_names = []

        callbacks = []

        for field in self.decls:
            if isinstance(field, Decl):
                name, type_, code = field.gen_pyi()

                if isinstance(field.type, PtrDecl):
                    if isinstance(field.type.type, FuncDecl):
                        if code and code.startswith('def '):
                            callbacks.append(field)

                if isinstance(field.type, TypeDecl):
                    if isinstance(field.type.type, (Union, Struct)) and code:
                        code = '\n'.join(
                            '    ' + line for line in code.split('\n')
                            )
                        nested_structs.append(code)
                        field_names.append(name)

                        params.append(
                            name + ': ' + 'Optional[' + name + '] = None'
                        )
                        continue

                if not code:
                    code = type_

                if not name:
                    raise RuntimeError(repr(type_) + ' : ' + repr(code))

                field_names.append(name)

                params.append(
                    pyi_struct_param_template.format(
                        field_name=name,
                        field_type=type_
                    )
                )

                fields.append(
                    pyi_struct_field_template.format(
                        field_name=name,
                        field_type=type_
                    )
                )

            else:
                raise RuntimeError(str(type(field)))

        if fields:
            fields = '\n' + ('\n'.join(fields)) + '\n'

        else:
            fields = ''

        if not fields and not nested_structs:
            return None, s_name, None

        if nested_structs:
            nested_structs = '\n' + ('\n'.join(nested_structs)) + '\n'
        else:
            nested_structs = ''

        params.insert(0, '/')
        params.insert(0, 'self')
        params = ', '.join(params)

        return s_name, None, pyi_struct_template.format(
            struct_name=s_name,
            nested_structs=nested_structs,
            fields=fields,
            params=params
        )

    def __str__(self):
        if self.name:
            return self.name

        return ''


class Union(Struct):

    def get_ast(self):
        if self.decls is None:
            return c_ast.Union(self.name, None)

        decls = []
        for decl in self.decls:
            decls.append(decl.get_aast())
        return c_ast.Union(self.name, decls)


class ArrayDecl:

    def __init__(self, type, dim, dim_quals):  # NOQA
        self.type = type
        self.dim = dim
        self.dim_quals = dim_quals

    @property
    def declname(self):
        return self.type.declname

    def get_ast(self):
        return c_ast.ArrayDecl(self.type.get_ast(), self.dim, self.dim_quals)

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

            return'List[' + type_ + ']'
        else:
            return 'list'


class CatchAll:

    def __init__(self, name):
        self.name = name

    def __call__(self, **_):
        return self

    @property
    def children(self):
        print(self.name)

        def wrapper():
            return []

        return wrapper

    def gen_pyi(self):  # NOQA
        return None, None, None

    def __str__(self):
        return ''
    

used_classes = {}
#C_AST NODES


class ArrayRef(c_ast.ArrayRef):
    def __init__(self, name, subscript):
        used_classes['ArrayRef'] = True
        c_ast.ArrayRef.__init__(self, name, subscript)


class Assignment(c_ast.Assignment):
    def __init__(self, op, lvalue, rvalue):
        used_classes['Assignment'] = True
        c_ast.Assignment.__init__(self, op, lvalue, rvalue)


class BinaryOp(c_ast.BinaryOp):
    def __init__(self, op, left, right):
        used_classes['BinaryOp'] = True
        c_ast.BinaryOp.__init__(self, op, left, right)
        

class Compound(c_ast.Compound):
    def __init__(self, block_items):
        used_classes['Compound'] = True
        c_ast.Compound.__init__(self, block_items)


class CompoundLiteral(c_ast.CompoundLiteral):
    def __init__(self, type, init):
        used_classes['CompoundLiteral'] = True
        c_ast.CompoundLiteral.__init__(self, type, init)


class Constant(c_ast.Constant):
    def __init__(self, type, value):
        used_classes['Constant'] = True
        c_ast.Constant.__init__(self, type, value)


class EllipsisParam(c_ast.EllipsisParam):
    def __init__(self):
        used_classes['EllipsisParam'] = True
        c_ast.EllipsisParam.__init__(self)


class EmptyStatement(c_ast.EmptyStatement):
    def __init__(self):
        used_classes['EmptyStatement'] = True
        c_ast.EmptyStatement.__init__(self)


class ExprList(c_ast.ExprList):
    def __init__(self, exprs):
        used_classes['ExprList'] = True
        c_ast.ExprList.__init__(self, exprs)


class FuncCall(c_ast.FuncCall):
    def __init__(self, name, args):
        used_classes['FuncCall'] = True
        c_ast.FuncCall.__init__(self, name, args)


class ID(c_ast.ID):
    def __init__(self, name):
        used_classes['ID'] = True
        c_ast.ID.__init__(self, name)

        
class InitList(c_ast.InitList):
    def __init__(self, exprs):
        used_classes['InitList'] = True
        c_ast.InitList.__init__(self, exprs)

        
class Return(c_ast.Return):
    def __init__(self, expr):
        used_classes['Return'] = True
        c_ast.Return.__init__(self, expr)


class StructRef(c_ast.StructRef):
    def __init__(self, name, type, field):
        used_classes['StructRef'] = True
        c_ast.StructRef.__init__(self, name, type, field)


class TernaryOp(c_ast.TernaryOp):
    def __init__(self, cond, iftrue, iffalse):
        used_classes['TernaryOp'] = True
        c_ast.TernaryOp.__init__(self, cond, iftrue, iffalse)


class UnaryOp(c_ast.UnaryOp):
    def __init__(self, op, expr):
        used_classes['UnaryOp'] = True
        c_ast.UnaryOp.__init__(self, op, expr)

        
        
class RootTypedef(Typedef):

    def gen_pyi(self):
        t_name = format_name(self.name)

        if isinstance(self.type, TypeDecl):
            name, type_, code = self.type.gen_pyi()

            if name and t_name and name == t_name and type_ and not code:
                if t_name not in pyi_typedef_names:
                    pyi_typedef_names.append(t_name)
                    pyi_typedefs.append(
                        'class {0}({1})'
                        ':\n    pass'.format(t_name, type_)
                    )
                return

            if code:
                if code.startswith('class'):
                    if (
                        name and type_ and
                        name not in pyi_struct_names and
                        type_ not in pyi_struct_names
                    ):
                        pyi_struct_names.append(type_)
                        pyi_struct_names.append(name)
                        pyi_structs.append(code)

                    elif (
                        name and not type_ and
                        name not in pyi_struct_names
                    ):
                        pyi_struct_names.append(name)
                        pyi_structs.append(code)

                    elif (
                        type_ and not name and
                        type_ not in pyi_struct_names
                    ):
                        pyi_struct_names.append(type_)
                        pyi_structs.append(code)

                elif ': int' in code:
                    if name:
                        tdef = pyi_typedef_template.format(
                            typedef_name=name,
                            typedef_type=type_
                        )

                        if name not in pyi_typedef_names:
                            pyi_typedef_names.append(name)
                            pyi_typedefs.append(tdef)

                    if code not in pyi_enums:
                        pyi_enums.append(code)
                else:
                    code = pyi_typedef_template.format(
                        typedef_name=t_name,
                        typedef_type=type_.replace('"', '')
                    )

                    if type_ not in pyi_callback_names + pyi_typedef_names:
                        pyi_typedef_names.append(type_)
                        pyi_typedefs.append(code)

                if t_name and type_ and t_name != type_:
                    if (
                        t_name not in
                        pyi_callback_names + pyi_typedef_names
                    ):
                        pyi_typedef_names.append(t_name)
                        pyi_typedefs.append(
                            'class {0}({1})'
                            ':\n    pass'.format(t_name, type_)
                        )

        elif isinstance(self.type, ArrayDecl):
            name, type_, code = self.type.gen_pyi()

            if code:
                if not t_name:
                    t_name = name

                code = '{name}: {type} = ...'.format(name=t_name, type=code)

                if t_name not in pyi_typedef_names:
                    pyi_typedef_names.append(t_name)
                    pyi_typedefs.append(code)

        elif isinstance(self.type, PtrDecl):
            name, type_, code = self.type.gen_pyi()

            if (
                name not in
                pyi_type_names + pyi_callback_names +
                pyi_typedef_names + pyi_struct_names +
                pyi_enum_names + pyi_func_names
            ):
                pyi_typedef_names.append(name)
                pyi_typedefs.append(code)

            if t_name and name and t_name != name:
                if t_name not in pyi_callback_names + pyi_typedef_names:
                    pyi_typedef_names.append(t_name)
                    pyi_typedefs.append(
                        'class {0}({1}):\n    pass'.format(t_name, name)
                    )

        else:
            raise RuntimeError(str(type(self.type)))


class RootDecl(Decl):

    def gen_pyi(self):
        d_name = format_name(self.name)

        if isinstance(self.type, Enum):
            name, type_, code = self.type.gen_pyi()

            if code:
                if name is None:
                    name = d_name

                if name and type_ and name != type_:
                    t_code = 'class {0}({1}):\n    pass'.format(name, type_)

                    if name not in pyi_typedef_names:
                        pyi_typedef_names.append(name)
                        pyi_typedefs.append(t_code)

                if code not in pyi_enums:
                    pyi_enums.append(code)

        elif isinstance(self.type, FuncDecl):
            name, type_, code = self.type.gen_pyi()
            if code:
                if not name and d_name:
                    name = d_name

                if name not in pyi_callback_names + pyi_func_names:
                    pyi_func_names.append(name)
                    pyi_funcs.append(code)

        elif isinstance(self.type, TypeDecl):
            name, type_, code = self.type.gen_pyi()

            if code:
                if not name and d_name:
                    name = d_name

                code = '{name}: {type} = ...'.format(name=name, type=code)

                if name not in pyi_type_names:
                    pyi_type_names.append(name)
                    pyi_types.append(code)

        elif isinstance(self.type, PtrDecl):
            name, type_, code = self.type.gen_pyi()
            if code:
                if not name and d_name:
                    name = d_name

                if name not in pyi_callback_names + pyi_func_names:
                    pyi_func_names.append(name)
                    pyi_funcs.append(code)

        elif isinstance(self.type, Struct):
            name, type_, code = self.type.gen_pyi()
            if code:
                if not name and d_name:
                    name = d_name

                if name not in pyi_struct_names:
                    pyi_struct_names.append(name)
                    pyi_structs.append(code)

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
                if name not in pyi_callback_names + pyi_func_names:
                    pyi_func_names.append(name)
                    pyi_funcs.append(code)

        else:
            raise RuntimeError(str(type(self.decl)))


pyi_callbacks = []
pyi_callback_names = []


pyi_typedefs = []
pyi_typedef_names = []

pyi_funcs = []
pyi_func_names = []

pyi_enums = []
pyi_enum_names = []

pyi_structs = []
pyi_struct_names = []

pyi_types = []
pyi_type_names = []


# this is some monkey patching code to flatten the output when printing a node.
def setup():

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


class _Module(dict):
    py_enums = py_enums
    pyi_callback_names = pyi_callback_names
    pyi_callbacks = pyi_callbacks
    pyi_typedefs = pyi_typedefs
    pyi_funcs = pyi_funcs
    pyi_enums = pyi_enums
    pyi_structs = pyi_structs
    pyi_types = pyi_types
    used_nodes = used_classes

    @staticmethod
    def setup():
        setup()

    @staticmethod
    def get_py_type(item):
        return get_py_type(item)

    def __init__(self):
        mod = sys.modules[__name__]
        self.__file__ = mod.__file__
        self.__loader__ = mod.__loader__
        self.__name__ = mod.__name__
        self.__package__ = mod.__package__
        self.__spec__ = mod.__spec__
        self.__original_module__ = mod
        sys.modules[__name__] = self

        dict.__init__(self)

    def __getitem__(self, item):
        if item in self.__original_module__.__dict__:
            return self.__original_module__.__dict__[item]

        return CatchAll(item)


_mod = _Module()
