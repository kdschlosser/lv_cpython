import sys
import os
from types import FunctionType
import inspect


def run(lib_path):
    lvgl_path = os.path.join(lib_path, 'lvgl')
    sys.path.insert(0, lib_path)

    import lvgl

    functions = {}
    structs_unions = {}
    enum_items = {}

    create_funcs = {}
    other = []

    basic_types = []

    for key, value in lvgl.__dict__.items():
        if value in (
            lvgl._StructUnion,  # NOQA
            lvgl._String,  # NOQA
            lvgl._Bool,  # NOQA
            lvgl._CBStore,  # NOQA
            lvgl._lib_lvgl,  # NOQA
            lvgl._get_c_obj,  # NOQA
            lvgl._get_py_obj,  # NOQA
            lvgl._get_c_type,  # NOQA
            lvgl._Array,  # NOQA
            lvgl._AsArrayMixin,  # NOQA
            lvgl._DefaultArg,  # NOQA
            lvgl._Integer,  # NOQA
            lvgl._PY_C_TYPES,  # NOQA
            lvgl.Union,  # NOQA
            lvgl.Any,  # NOQA
            lvgl.Callable,  # NOQA
            lvgl.Optional,  # NOQA
            lvgl.List,  # NOQA
            lvgl._Float,  # NOQA
            lvgl._convert_basic_type  # NOQA
        ):
            continue

        if key.startswith('__'):
            continue

        if isinstance(value, FunctionType):
            if key.endswith('_create') and not key.startswith('sdl') and not key.startswith('indev'):
                create_funcs[key] = value
            else:
                functions[key] = value

        elif key.isupper():
            enum_items[key] = key

        else:
            try:
                if issubclass(value, lvgl._StructUnion):  # NOQA
                    structs_unions[key] = {
                        'cls': value,
                        'name': key,
                        'p_methods': {},
                        'methods': {},
                        'enums': {}
                    }
                elif issubclass(value, (
                    lvgl._Float,  # NOQA
                    lvgl._Integer,  # NOQA
                    lvgl._String,  # NOQA
                    lvgl._Bool,  # NOQA
                    lvgl.void  # NOQA
                )):
                    basic_types.append(key)

            except TypeError:
                other.append(key)

    obj_classes = {}

    def convert_type(ano):
        if ano == 'void':
            return '_lvgl.void'


        for type_ in basic_types:
            if type_ in ano:
                return ano

        if '_Bool' in ano:
            if '_lvgl' not in ano:
                ano = ano.replace('_Bool', '_lvgl._Bool')
            return ano

        if 'List[' in ano:
            ano = ano.split('List[')[1:]
            for i, itm in enumerate(ano):
                if '_lvgl' in itm:
                    itm = itm.replace('_lvgl.', '"')[:-1] + '"]'
                    ano[i] = itm
            ano.insert(0, '')
            ano = 'List['.join(ano)
            ano = ano.replace('obj_t', 'obj')
            return ano

        if '_lvgl' in ano:
            ano = ano.replace('_lvgl.', '"') + '"'

        ano = ano.replace('obj_t', 'obj')

        return ano

    def convert_annotation(annot):
        try:
            annot = annot.__name__
        except:  # NOQA
            annot = str(annot)

        annot = annot.replace("ForwardRef('", '').replace("')", '')

        if annot.startswith('typing'):
            annot = annot.replace('typing.', '')
            if annot.startswith('List['):
                annot = annot.split('List[')[1:]

                for i, itm in enumerate(annot):
                    if itm.startswith('typing'):
                        itm = itm.replace('typing.', '')
                    else:
                        itm = itm.lstrip('_')
                        itm = f'_lvgl.{itm}'
                    annot[i] = itm

                annot.insert(0, '')
                annot = 'List['.join(annot)
                return annot

            return annot

        if '"' in annot:
            qoted = True
            annot = annot.replace('"', '')
        else:
            qoted = False

        annot = annot.replace('bool', '_Bool')

        if not annot.startswith('_Bool'):
            annot = annot.lstrip('_')

        if annot.startswith('List['):
            annot.replace('List[', '')
            if annot.startswith('typing'):
                annot = annot.replace('typing.', '')
                return f'List[{annot}'

            if not annot.startswith('_Bool'):
                annot = annot.lstrip('_')
            annot = f'List[_lvgl.{annot}'
        elif qoted:
            if not annot.startswith('_Bool'):
                annot = annot.lstrip('_')
            annot = f'_lvgl.{annot}'

        elif annot != 'None':
            if not annot.startswith('_Bool'):
                annot = annot.lstrip('_')
            annot = f'_lvgl.{annot}'

        return annot

    for name, func in create_funcs.items():
        cls_name = name.replace('_create', '')

        sig = inspect.signature(func)
        params = list(sig.parameters.items())

        if params:
            param_name, param = params[0]
            notation = param.annotation

            if notation == param.empty:
                functions[name] = func
                continue

            p_notation = convert_annotation(notation).replace('_lvgl.', '')
            ret_val = convert_annotation(sig.return_annotation).replace('_lvgl.', '')

            if ret_val != p_notation:
                functions[name] = func
                continue

            new_params = ['self']
            param_names = []

            for p_name, param in params:
                if param.kind == param.VAR_POSITIONAL:
                    p_name = f'*{p_name}'
                    new_params.append(p_name)
                else:
                    anno = convert_annotation(param.annotation)
                    new_params.append(f'{p_name}: {anno}')

                param_names.append(p_name)

            obj_classes[cls_name] = {
                'name': cls_name,
                'methods': {},
                'enums': {},
                'create_func_name': name,
                'parent_cls': p_notation,
                'arg_names': ', '.join(param_names),
                'args': ', '.join(new_params),
                'type': ret_val
            }


    def get_common_name(name1, name2, limit=99):
        name1 = name1.split('_')
        name2 = name2.split('_')

        res = []

        for i in range(min(len(name1), len(name2))):
            if len(res) == limit:
                break

            if name1[i] != name2[i]:
                break

            res.append(name1[i])

        return '_'.join(res)


    def get_uncommon_name(name1, name2):
        cmmon = get_common_name(name1, name2)
        cmmon += '_'

        return name2.replace(cmmon, '', 1)


    for cls_name1, cls in obj_classes.items():
        cls_name2 = cls['parent_cls']
        matched_name = ''

        for cls_name3 in obj_classes.keys():
            if cls_name1 == cls_name3:
                continue

            common_name = get_common_name(cls_name2, cls_name3)

            if not common_name:
                continue

            if len(common_name) > len(matched_name):
                matched_name = cls_name3

        if not matched_name:
            if get_common_name(cls_name1, cls_name2):
                cls['parent_cls'] = f'_lvgl.{cls_name2}'
                continue

            raise RuntimeError

        cls['parent_cls'] = matched_name


    for func_name, func in list(functions.items()):
        match = None
        matched_common_name = ''
        for cls_name, cont in obj_classes.items():

            common = get_common_name(func_name, cls_name)
            if not common:
                continue

            sig = inspect.signature(func)

            params = list(sig.parameters.items())
            if not params:
                continue

            param_name, param = params[0]

            anno = param.annotation
            if anno == param.empty:
                continue

            anno = convert_annotation(anno).replace('_lvgl.', '')

            if cont['type'] != anno:
                continue

            if len(common) > len(matched_common_name):
                matched_common_name = common
                match = cont

        if match is None:
            continue

        del functions[func_name]

        new_params = ['self']
        param_names = ['self']

        sig = inspect.signature(func)

        for param_name, param in list(sig.parameters.items())[1:]:
            if param.kind == param.VAR_POSITIONAL:
                param_name = f'*{param_name}'
                new_params.append(param_name)
            else:
                anno = convert_annotation(param.annotation)
                anno = anno.replace('NoneType', 'void')
                anno = convert_type(anno)
                new_params.append(f'{param_name}: {anno}')

            param_names.append(param_name)

        anno = convert_annotation(sig.return_annotation)
        anno = convert_type(anno)
        ret_val = f' -> {anno}'

        new_func_name = get_uncommon_name(match['name'], func_name)
        if new_func_name == 'del':
            new_func_name = '_del'
        match['methods'][new_func_name] = {
            'name': func_name,
            'ret_val': ret_val,
            'params': ', '.join(new_params),
            'param_names': ', '.join(param_names)
        }

    structs = {}

    for func_name, func in list(functions.items()):
        match = None
        matched_common_name = ''

        sig = inspect.signature(func)
        params = list(sig.parameters.items())
        if not params:
            continue

        param_name, param = params[0]

        anno = param.annotation
        if anno == param.empty:
            continue

        anno = convert_annotation(anno).replace('_lvgl.', '')


        for struct_name, cont in structs.items():
            common = get_common_name(func_name, struct_name)
            if not common:
                continue

            if struct_name != anno:
                continue

            if len(common) > len(matched_common_name):
                matched_common_name = common
                match = cont

        for struct_name, cont in structs_unions.items():
            common = get_common_name(func_name, struct_name)
            if not common:
                continue

            if struct_name != anno:
                continue

            if len(common) > len(matched_common_name):
                matched_common_name = common
                match = cont

        if match is None:
            continue

        del functions[func_name]

        new_params = ['self']
        param_names = ['self']

        for param_name, param in list(sig.parameters.items())[1:]:
            if param.kind == param.VAR_POSITIONAL:
                param_name = f'*{param_name}'
                new_params.append(param_name)
            else:
                anno = convert_annotation(param.annotation)
                anno = anno.replace('NoneType', 'void').replace('None', 'void')
                anno = convert_type(anno)
                new_params.append(f'{param_name}: {anno}')

            param_names.append(param_name)

        anno = convert_annotation(sig.return_annotation)
        anno = convert_type(anno)
        ret_val = f' -> {anno}'

        new_func_name = get_uncommon_name(match['name'], func_name)
        if new_func_name == 'del':
            new_func_name = '_del'

        match['methods'][new_func_name] = {
            'name': func_name,
            'ret_val': ret_val,
            'params': ', '.join(new_params),
            'param_names': ', '.join(param_names)
        }

        structs[match['name']] = match
        try:
            del structs_unions[match['name']]
        except KeyError:
            pass

    for enum_name, val in sorted(list(enum_items.items())):
        match = None
        matched_common_name = ''
        for cls_name, cont in obj_classes.items():
            common = get_common_name(enum_name.lower(), cls_name, 2)

            if not common:
                continue

            if len(common) > len(matched_common_name):
                matched_common_name = common
                match = cont

        if match is None:
            continue

        new_enum_name = enum_name.replace(matched_common_name.upper() + '_', '')
        match['enums'][new_enum_name] = enum_name
        del enum_items[enum_name]


    for cls_name, cont in obj_classes.items():

        def _match_enums(mtched_name=None):
            if mtched_name is not None:
                matches = []

                for enum, vl in list(cont['enums'].items()):
                    comm = get_common_name(mtched_name, enum, 3)

                    if not comm:
                        continue

                    if comm != mtched_name:
                        continue

                    matches.append((enum, vl))

                m_enums = {}
                matched_enums = {}

                for mtch, vl in matches:
                    del cont['enums'][mtch]
                    n_enum_name = get_uncommon_name(mtched_name, mtch)
                    m_enums[n_enum_name] = [mtch, vl]

                matched_enums[mtched_name] = m_enums

                return matched_enums

            matched_enums = {}

            for enum1, val1 in list(cont['enums'].items()):
                matches = []
                mtched_name = ''

                for enum2, val2 in list(cont['enums'].items()):
                    if enum1 == enum2:
                        continue

                    comm = get_common_name(enum1, enum2, 2)
                    if not comm:
                        continue

                    if len(common) > len(mtched_name):
                        mtched_name = comm
                        matches = [(enum1, val1)]

                    matches.append((enum2, val2))

                if mtched_name:
                    m_enums = {}

                    for mtch, vl in matches:
                        del cont['enums'][match]
                        n_enum_name = get_uncommon_name(mtched_name, mtch)
                        m_enums[n_enum_name] = [match, vl]

                    matched_enums[mtched_name] = m_enums

            return matched_enums

        storage = {}
        if cls_name == 'obj':
            storage.update(_match_enums('CLASS_THEME_INHERITABLE'))
            storage.update(_match_enums('CLASS_GROUP_DEF'))
            storage.update(_match_enums('CLASS_EDITABLE'))

        elif cls_name == 'chart':
            storage.update(_match_enums('AXIS_PRIMARY'))
            storage.update(_match_enums('AXIS_SECONDARY'))

        elif cls_name == 'imgbtn':
            storage.update(_match_enums('STATE'))

        elif cls_name == 'menu':
            storage.update(_match_enums('ROOT_BACK_BTN'))


        storage.update(_match_enums())
        cont['enums'] = storage

    used = []

    output = open(os.path.join(lvgl_path, 'mpy.py'), 'w')

    output.write('from typing import Union, Any, Callable, Optional, List  # NOQA\n\n')
    output.write('import lvgl as _lvgl\n\n\n')

    enum_template = '''
class {name}:
{items}'''

    enum_item_template = '    {name} = _lvgl.{o_name}'

    def output_enum(nme, items):
        new_items = []

        if len(items) == 1:
            print('{0} = _lvgl.{1}'.format(*items[0]))

            output.write('{0} = _lvgl.{1}\n\n'.format(*items[0]))
        else:
            for ename, o_name in items:
                if ename[0].isdigit():
                    ename = f'_{ename}'

                new_items.append(f'    {ename} = _lvgl.{o_name}')

            tmpl = enum_template.format(
                name=nme,
                items='\n'.join(new_items)
            )

            output.write(tmpl + '\n\n')


    def sort_enums(mtch_name=None):

        if mtch_name is not None:
            m_enums = []

            for ename, vlue in list(enum_items.items()):

                comm = get_common_name(ename, mtch_name, 2)

                if comm and comm == mtch_name:
                    nenum_name = ename.replace(mtch_name + '_', '')
                    m_enums.append((nenum_name, vlue))
                    used.append(ename)

                    try:
                        del enum_items[ename]
                    except KeyError:
                        continue

            output_enum(mtch_name, m_enums)
            return


        for enum_name1, value1 in list(enum_items.items()):
            if enum_name1 in used:
                continue

            mtched_common_name = ''
            matches = []

            for enum_name2, value2 in list(enum_items.items()):
                if enum_name2 in used:
                    continue

                if enum_name1 == enum_name2:
                    continue

                cmm = get_common_name(enum_name1, enum_name2, 2)

                if not cmm:
                    continue

                if len(cmm) > len(mtched_common_name):
                    matches = [(enum_name1, value1)]
                    mtched_common_name = cmm

                matches.append((enum_name2, value2))

            if not mtched_common_name:
                used.append(enum_name1)
                try:
                    del enum_items[enum_name1]
                except KeyError:
                    pass

                output_enum(enum_name1, [(enum_name1, value1)])
            else:
                m_enums = []

                for ename, vl in matches:
                    try:
                        del enum_items[ename]
                    except KeyError:
                        continue

                    used.append(ename)

                    nenum_name = get_uncommon_name(mtched_common_name, ename)
                    m_enums.append((nenum_name, vl))

                output_enum(mtched_common_name, m_enums[:])

            try:
                del enum_items[enum_name1]
            except KeyError:
                pass

    for e_name in (
        'EXPLORER',
        'INDEV_TYPE',
        'INDEV_STATE',
        'DRAW_MASK',
        'DRAW_LAYER',
        'FS_RES',
        'FS_MODE',
        'FS_SEEK',
        'DISP_ROTATION',
        'FONT_SUBPX',
        'ANIM_IMG',
        'SPAN_MODE',
        'SPAN_OVERFLOW',
        'FLEX_ALIGN',
        'FLEX_FLOW',
        'GRID_ALIGN',
        'GRID',
        'COLOR_FORMAT',
        'STYLE_RES',
        'STYLE_PROP'
    ):
        sort_enums(e_name)

    '''
    OBJ_CLASS_EDITABLE
    OBJ_CLASS_GROUP
    OBJ_CLASS_THEME

    CHART_AXIS

    IMGBTN_STATE
    MENU_ROOT
    '''
    sort_enums()


    class_template = '''\
class {name}({parent_cls}):
{enums}
    def __init__({args}):
        if self.__class__.__name__ == 'obj':
            super().__init__()
        else:
            super().__init__(_lvgl._DefaultArg)  # NOQA
                                    
        for arg in ({arg_names},):
            if arg == _lvgl._DefaultArg:  # NOQA
                break
        else:
            cls = _lvgl.{create_func_name}({arg_names})
            cls.cast(self)
   
{methods}'''


    method_template = '''\
    def {name}({args}){ret_val}:
        return _lvgl.{o_name}({arg_names})
'''

    for name in structs_unions.keys():
        output.write(f'{name} = _lvgl.{name}\n')

    output.write('\n\n')

    for item in other:
        output.write(f'{item} = _lvgl.{item}\n')


    output.write('\n\n')
    function_template = '''\
def {name}({args}){ret_val}:
    return _lvgl.{o_name}({arg_names})
'''

    for func_name, func in list(functions.items()):
        new_params = []
        param_names = []

        sig = inspect.signature(func)

        for param_name, param in list(sig.parameters.items()):
            if param.kind == param.VAR_POSITIONAL:
                param_name = f'*{param_name}'
                new_params.append(param_name)
            else:
                anno = convert_annotation(param.annotation)
                anno = anno.replace('NoneType', 'void')
                anno = convert_type(anno)
                new_params.append(f'{param_name}: {anno}')

            param_names.append(param_name)

        anno = convert_annotation(sig.return_annotation)
        anno = convert_type(anno)
        ret_val = f' -> {anno}'

        fnc = function_template.format(
            name=func_name,
            o_name=func_name,
            args=', '.join(new_params),
            arg_names=', '.join(param_names),
            ret_val=ret_val
        )

        output.write('\n' + fnc + '\n')

    output.write('\n\n')


    struct_class_template = '''\
class {name}({parent_cls}):

{methods}'''

    for name, value in structs.items():
        methods = []

        for method_name, cont in value['methods'].items():
            meth = method_template.format(
                name=method_name,
                o_name=cont['name'],
                args=cont['params'],
                arg_names=cont['param_names'],
                ret_val=cont['ret_val']
            )

            methods.append(meth)

        cls = struct_class_template.format(
            name=name,
            parent_cls=f'_lvgl.{name}',
            methods='\n'.join(methods),
        )

        output.write(cls + '\n\n')

    for name, value in obj_classes.items():
        methods = []
        enms = []

        for method_name, cont in value['methods'].items():
            meth = method_template.format(
                name=method_name,
                o_name=cont['name'],
                args=cont['params'],
                arg_names=cont['param_names'],
                ret_val=cont['ret_val']
            )

            methods.append(meth)

        for enum_cls_name, d in value['enums'].items():
            enm_items = []

            for item_name, data in d.items():
                o_enum_name = data[-1]
                enm_items.append(enum_item_template.format(name=item_name, o_name=o_enum_name))

            enm_cls = enum_template.format(name=enum_cls_name, items='\n'.join(enm_items))

            enm_cls = '\n'.join('    ' + line for line in enm_cls.split('\n'))
            enms.append(enm_cls)

        if enms:
            enms = '\n'.join(enms)
            enms += '\n'
        else:
            enms = ''

        cls = class_template.format(
            name=name,
            parent_cls=value['parent_cls'],
            enums=enms,
            args=value['args'],
            create_func_name=value['create_func_name'],
            arg_names=value['arg_names'],
            methods='\n'.join(methods),
            fp='' if name == 'obj' else '_lvgl._DefaultArg'
        )

        output.write(cls + '\n\n')


    output.close()

if __name__ == '__main__':
    run(r'..\build\lib.win-amd64-cpython-310')