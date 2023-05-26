import sys
import os

base_path = os.path.dirname(__file__)
build_path = os.path.join(base_path, '..', 'build')
lvgl_path = os.path.join(build_path, 'lvgl')
sys.path.insert(0, build_path)

from types import FunctionType
import inspect

import lvgl

def run():

    functions = {}
    structs_unions = {}
    enum_items = {}

    create_funcs = {}
    create_structs = {}
    other = []

    for key, value in lvgl.__dict__.items():
        if value in (
            lvgl._StructUnion,
            lvgl._String,
            lvgl._Bool,
            lvgl._CBStore,
            lvgl._lib_lvgl,
            lvgl._get_c_obj,
            lvgl._get_py_obj,
            lvgl._get_c_type,
            lvgl._Array,
            lvgl._AsArrayMixin,
            lvgl._DefaultArg,
            lvgl._Integer,
            lvgl._PY_C_TYPES,
            lvgl.Union,
            lvgl.Any,
            lvgl.Callable,
            lvgl.Optional,
            lvgl.List,
            lvgl._Float
        ):
            continue

        if key.startswith('__'):
            continue

        if isinstance(value, FunctionType):
            if key.endswith('_create'):
                create_funcs[key] = value
            else:
                functions[key] = value

        elif key.isupper():
            enum_items[key] = key

        else:
            try:
                if issubclass(value, lvgl._StructUnion):
                    structs_unions[key] = {
                        'cls': value,
                        'name': key,
                        'p_methods': {},
                        'methods': {},
                        'enums': {}
                    }
                else:
                    other.append(key)
            except TypeError:
                other.append(key)

    obj_classes = {}


    def convert_annotation(annot):
        annot = str(annot)

        annot = annot.replace("ForwardRef('", '').replace("')", '')

        if annot.startswith('typing'):
            annot = annot.replace('typing.', '')
            if annot.startswith('List['):
                annot = annot.split('List[')[1:]

                for i, item in enumerate(annot):
                    if item.startswith('typing'):
                        item = item.replace('typing.', '')
                    else:
                        item = f'_lvgl.{item}'
                    annot[i] = item

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

        if annot.startswith('List['):
            annot.replace('List[', '')
            if annot.startswith('typing'):
                annot = annot.replace('typing.', '')
                return f'List[{annot}'

            annot = f'List[_lvgl.{annot}'
        elif qoted:
            annot = f'_lvgl.{annot}'

        elif annot != 'None':
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
                continue

            p_notation = convert_annotation(notation).replace('_lvgl.', '')
            ret_val = convert_annotation(sig.return_annotation).replace('_lvgl.', '')

            if ret_val != p_notation:
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
        common = get_common_name(name1, name2)
        common += '_'

        return name2.replace(common, '', 1)


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
                new_params.append(f'{param_name}: {anno}')

            param_names.append(param_name)

        anno = convert_annotation(sig.return_annotation)

        ret_val = f' -> {anno}'

        new_func_name = get_uncommon_name(match['name'], func_name)
        match['methods'][new_func_name] = {
            'name': func_name,
            'ret_val': ret_val,
            'params': ', '.join(new_params),
            'param_names': ', '.join(param_names)
        }


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

        matched_enums = {}

        for enum1, val1 in list(cont['enums'].items()):
            matches = []
            matched_name = ''

            for enum2, val2 in list(cont['enums'].items()):
                if enum1 == enum2:
                    continue

                common = get_common_name(enum1, enum2, 2)
                if not common:
                    continue

                if len(common) > len(matched_name):
                    matched_name = common
                    matches = [(enum1, val1)]

                matches.append((enum2, val2))

            if matched_name:
                m_enums = {}

                for match, val in matches:
                    del cont['enums'][match]
                    new_enum_name = get_uncommon_name(matched_name, match)
                    m_enums[new_enum_name] = [match, val]

                matched_enums[matched_name] = m_enums

        cont['enums'] = matched_enums


    enum_classes = []

    used = []

    def sort_enums(match_name=None):
        for enum_name1, value1 in list(enum_items.items()):
            if enum_name1 in used:
                continue

            if match_name is not None:
                common = get_common_name(enum_name1, match_name, 2)
                if common and common == match_name:
                    matched_common_name = common
                    matches = [(enum_name1, value1)]
                else:
                    matched_common_name = ''
                    matches = []
            else:
                matched_common_name = ''
                matches = []

            for enum_name2, value2 in list(enum_items.items()):
                if enum_name2 in used:
                    continue

                if enum_name1 == enum_name2:
                    continue

                if matched_common_name and matched_common_name not in (
                    'COLOR_FORMAT',
                    'ALIGN',
                    'PALETTE',
                    'TEXT_FLAG',
                    'STYLE',
                    '_STYLE',
                    'STATE',
                    'EVENT',
                    'DISP',
                    'FS_RES',
                    'DRAW_MASK_RES',
                    'INDEV_TYPE',
                    '_BTNMATRIX',
                    'FLEX_ALIGN',
                    'GRID',
                    'DRAW_MASK'
                ):
                    for enum_name3, _ in matches:
                        common = get_common_name(enum_name2, enum_name3, 2)
                        if common and len(common) > len(matched_common_name):
                            print(matched_common_name)
                            return common

                common = get_common_name(enum_name1, enum_name2, 2)

                if common in ('DISP_ROTATION', 'DISP_RENDER_MODE', 'FONT_SUBPX', 'COLOR', 'FONT', 'FONT_FMT_TXT'):
                    continue

                if not common:
                    continue

                if len(common) > len(matched_common_name):
                    matches = [(enum_name1, value1)]
                    matched_common_name = common

                matches.append((enum_name2, value2))

            if not matched_common_name:
                enum_classes.append({'name': enum_name1, 'enums': [(enum_name1, value1)]})
            else:
                m_enums = []

                for enum_name, val in matches:
                    try:
                        del enum_items[enum_name]
                    except KeyError:
                        continue

                    new_enum_name = get_uncommon_name(matched_common_name, enum_name)
                    m_enums.append((new_enum_name, val))

                enum_classes.append({'name': matched_common_name, 'enums': m_enums[:]})

            used.append(enum_name1)

            try:
                del enum_items[enum_name1]
            except KeyError:
                pass


    nm = sort_enums()
    import time
    while nm is not None:
        print(nm)
        time.sleep(1)
        nm = sort_enums(nm)


    class_template = '''\
    class {name}({parent_cls}):
    {enums}
        def __init__({args}):
            super().__init__({fp_name})
            cls = _lvgl.{create_func_name}({arg_names})
            cls.cast(self)
        
    {methods}'''


    method_template = '''\
        def {name}({args}){ret_val}:
            return _lvgl.{o_name}({arg_names})
    '''

    enum_template = '''
    class {name}:
    {items}'''

    enum_item_template = '    {name} = _lvgl.{o_name}'


    output = open(os.path.join(lvgl_path, 'mpy.py'), 'w')

    output.write('from typing import Union, Any, Callable, Optional, List  # NOQA\n\n')
    output.write('import lvgl as _lvgl\n\n\n')


    for name in structs_unions.keys():
        output.write(f'{name} = _lvgl.{name}\n')

    output.write('\n\n')

    for item in other:
        output.write(f'{item} = _lvgl.{item}\n')


    output.write('\n\n')


    for func_name in functions.keys():

        output.write(f'{func_name} = _lvgl.{func_name}\n')

    output.write('\n\n')

    used_enums = []

    for enm in enum_classes:
        name = enm['name']
        if name in used_enums:
            continue

        used_enums.append(name)

        items = enm['enums']
        new_items = []

        if len(items) == 1:
            if items[0] in used_enums:
                continue

            used_enums.append(items[0])
            output.write('{0} = _lvgl.{1}\n\n'.format(*items[0]))
        else:
            for e_name, o_name in items:
                used_enums.append(o_name)

                if e_name[0].isdigit():
                    e_name = f'_{e_name}'

                new_items.append(f'    {e_name} = _lvgl.{o_name}')

            tmpl = enum_template.format(
                name=name,
                items='\n'.join(new_items)
            )

            output.write(tmpl + '\n\n')

    output.write('\n')

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
            fp_name=value['arg_names'].split(',')[0]
        )

        output.write(cls + '\n\n')


    output.close()