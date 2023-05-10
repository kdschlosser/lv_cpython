import os
import sys
import shutil

import pyi_builder


#  path to where thgis script is located
base_path = os.path.dirname(__file__)

# make sure we are in the correct directory
os.chdir(base_path)

# set the output folder for the so/pyd and any other files.
build_path = os.path.join(base_path, 'build')

if os.path.exists(build_path):
    try:
        shutil.rmtree(build_path)
    except:
        pass

try:
    os.mkdir(build_path)
except:
    pass

if sys.platform.startswith('win'):
    # this library is what make building on Windows possible. both
    # distutils and setuptools do not properly set up a build environment
    # on Windows using the MSVC compiler. It does everything that is needed
    # to set up the build system and it works, plain and simple.
    # the library is available on pypi
    # https://pypi.org/project/pyMSVC/
    # and it is also on Github
    # https://github.com/kdschlosser/python_msvc

    try:
        import pyMSVC
    except ImportError:
        raise RuntimeError(
            'pyMSVC needs to be installed into python to compile under windows.'
        )

    environment = pyMSVC.setup_environment()
    print(environment)

    # compiler to use
    cpp_path = 'cl'

    sdl_include_path = os.path.join(base_path, 'sdl_temp')
    if not os.path.exists('sdl_temp'):
        os.mkdir('sdl_temp')

    sdl_dst_path = os.path.join(sdl_include_path, 'SDL2')
    if not os.path.exists(sdl_dst_path):
        os.mkdir(sdl_dst_path)

        sdl_src_path = os.path.join(base_path, 'SDL2', 'include')
        if not os.path.exists(sdl_src_path):
            raise RuntimeError(
                'SDL2 needs to be placed into the folder of '
                'this script in a folder named "SDL2"'
            )


        def _iter_copy(src_p, dst_p):
            directories = []
            for file_name in os.listdir(src_p):
                src = os.path.join(src_p, file_name)
                dst = os.path.join(dst_p, file_name)
                if os.path.isdir(src):
                    directories.append((src, dst))
                else:
                    shutil.copyfile(src, dst)
            for paths in directories:
                _iter_copy(*paths)


        _iter_copy(sdl_src_path, sdl_dst_path)

    sdl_lib_path = os.path.join(base_path, 'SDL2', 'lib', 'x64')
    sdl_dll = os.path.join(sdl_lib_path, 'SDL2.dll')

    shutil.copyfile(sdl_dll, os.path.join(build_path, 'SDL2.dll'))

    include_dirs = [sdl_include_path]
    library_dirs = [sdl_lib_path]
    libraries = ['SDL2']
    cpp_args = ['-std:c11']

    # os.environ['INCLUDE'] += ';' + sdl_include_path
    # os.environ['LIB'] += ';' + sdl_lib_path
else:
    # compiler to use
    cpp_path = 'gcc'
    libraries = ['SDL2']
    library_dirs = []
    include_dirs = []
    cpp_args = ['-std=c11']

# file/directory paths
lvgl_path = os.path.join(base_path, 'lvgl')
lvgl_src_path = os.path.join(lvgl_path, 'src')
lvgl_header_path = os.path.join(lvgl_path, 'lvgl.h')

if not os.path.exists(lvgl_path):
    raise RuntimeError(
        'lvgl needs to be placed into the same '
        'folder as this script in order to compile the binding.'
    )

os.chdir(base_path)
# technically we do not need to package pycparser with the builder.
# The fake lib c files are not included if pycparser is installed into python
# and that is the reason for packaging it with the binding. Since I
# had to modify those files they are packaged. I just left it as it is but it
# will be removed in the future.

try:
    import pycparser  # NOQA
except ImportError:
    pycparser_path = os.path.join(base_path, 'pycparser')
    sys.path.insert(0, pycparser_path)
    try:
        import pycparser  # NOQA
    except ImportError:
        raise RuntimeError(
            '"pycparser" needs to be installed into '
            'Python to compile the binding'
        )

try:
    from cffi import FFI  # NOQA
except ImportError:
    raise RuntimeError(
        '"cffi" needs to be installed into Python to compile the binding'
    )

from pycparser import c_generator, c_ast  # NOQA


# some paths/files we do not need to compile the source files for.
IGNORE_DIRS = (
    'disp', 'arm2d', 'gd32_ipa', 'nxp', 'stm32_dma2d', 'swm341_dma2d'
)
IGNORE_FILES = ()


# # function that iterates over the LVGL/src directory to
# locate all of the ".c" files as these files need to be compiled
def iter_sources(p):
    res = []  # NOQA
    folders = []
    for f in os.listdir(p):  # NOQA
        file = os.path.join(p, f)
        if os.path.isdir(file):
            if f in IGNORE_DIRS:
                continue

            folders.append(file)
        elif f not in IGNORE_FILES:
            if not f.endswith('.c'):
                continue

            res.append(file)

    for folder in folders:
        res.extend(iter_sources(folder))

    return res


# read the lvgl header files so we can generate the information that CFFI needs
# I know that LVGL was written for c99 and thata I am using c11. This is
# because the MSVC compiler does not support c99. c11 seems to work without
# any issues.
ast = pycparser.parse_file(
    lvgl_header_path,
    use_cpp=True,
    cpp_path=cpp_path,
    cpp_args=['-E', '-DCPYTHON_SDL', '-DPYCPARSER',
              '-Ifake_libc_include'] + cpp_args,
    parser=None
)

log = open('log.txt', 'w')


callback_template = '''\
@_lib_lvgl.ffi.def_extern(name='py_lv_{func_name}')
def __{func_name}_callback_func(*args):
    if len(args):
        try:
            cb_store = _lib_lvgl.ffi.from_handle(args[0].user_data)

            if '{func_name}' in cb_store:
                func = cb_store['{func_name}']
                try:
                    return {func_name}._callback_func(func, *args)  # NOQA
                    
                except Exception:
                    import traceback

                    traceback.print_exc()

            else:
                print('"{func_name}" is not registered')
        
        except AttributeError:
            print('No "user_data" field available')
    else:
        print('No structure available')


class _{func_name}(_CallbackWrapper):

    def __call__(self, func):
        return _{func_name}(self.ctype, func)


{func_name} = _{func_name}('lv_{func_name}', None)

'''

pyi_callback_template = '''
class {func_name}:
    def __init__(self, func: Callable[{param_types}, {ret_type}]):
        ...'''


def is_lib_c_node(n):
    if hasattr(n, 'coord') and n.coord is not None:
        if 'fake_libc_include' in n.coord.file:
            return True
    return False


# monkeypatched functions in pycparser.c_generator.CGenerator
# I used the CGenerator to output declarations that CFFI uses to make
# the Python C extension. I am using only the header files and not the C
# source files for the preprocessing. There are however some functions that are
# defined in the header files and I needed to change those to declaractions.

# this function removes any of the declarations that get added from the
# fake lib c header files. we do not wnat to use that information because it
# declares things like uint_8t as int which it 3 bytes larger then it should be.
# this causes problems in the c extension.
def visit(self, node):
    if is_lib_c_node(node):
        return ''

    method = 'visit_' + node.__class__.__name__
    ret = getattr(self, method, self.generic_visit)(node)
    if ret.strip() == ';':
        return ''

    return ret


# turns function definitions into declarations.
def visit_FuncDef(self, n):
    decl = self.visit(n.decl)  # NOQA
    self.indent_level = 0
    if n.param_decls:
        knrdecls = ';\n'.join(self.visit(p) for p in n.param_decls)
        res = decl + '\n' + knrdecls + ';\n'  # + body + '\n'  # NOQA
    else:
        res = decl + ';\n'  # NOQA

    return res


callbacks = []


def visit_Typedef(self, n):
    s = ''
    if n.storage:
        s += ' '.join(n.storage) + ' '

    s += self._generate_type(n.type)

    if isinstance(n.type, c_ast.PtrDecl):
        if isinstance(n.type.type, c_ast.FuncDecl):
            if isinstance(n.type.type.type, (c_ast.TypeDecl, c_ast.PtrDecl)):
                if isinstance(n.type.type.type, c_ast.PtrDecl):
                    type_ = n.type.type.type.type
                    ptr = True
                else:
                    type_ = n.type.type.type
                    ptr = False

                name = type_.declname
                for item in ('_cb_t', '_f_t'):
                    if name.replace('lv_', '', 1) in pyi_builder.pyi_callback_names:
                        return ''

                    if name.endswith(item):
                        s = s.replace('(*' + name + ')', 'py_' + name).replace(
                            '(* ' + name + ')',
                            'py_' + name
                            ) + ';\n' + s
                        if s.startswith('typedef'):
                            s = '\n\nextern "Python"' + s[7:]
                        else:
                            s = '\n\nextern "Python"' + s

                        callbacks.append(
                            callback_template.format(
                                func_name=name.replace('lv_', '', 1)
                            )
                        )

                        try:
                            ret_type = pyi_builder.get_py_type(type_.type.names[0])
                            if ret_type == 'None' and ptr:
                                ret_type = 'Any'
                        except:
                            ret_type = pyi_builder.get_py_type(type_.type.name)

                        param_types = []

                        params = n.type.type.args.params
                        for param in params:
                            if isinstance(param, c_ast.Typename):
                                if isinstance(param.type, c_ast.PtrDecl):
                                    if isinstance(
                                        param.type.type.type,
                                        c_ast.IdentifierType
                                    ):
                                        param_type = pyi_builder.get_py_type(
                                            param.type.type.type.names[0]
                                        )

                                    elif isinstance(
                                        param.type.type.type,
                                        c_ast.Struct
                                    ):
                                        param_type = pyi_builder.get_py_type(
                                            param.type.type.type.name
                                        )
                                    else:
                                        raise RuntimeError(
                                            str(type(param.type.type.type))
                                        )

                                elif isinstance(param.type, c_ast.TypeDecl):
                                    param_type = pyi_builder.get_py_type(
                                        param.type.type.names[0]
                                    )
                                else:
                                    raise RuntimeError(str(type(param.type)))

                            elif isinstance(param, c_ast.Decl):
                                if isinstance(param.type, c_ast.PtrDecl):
                                    if isinstance(
                                        param.type.type,
                                        c_ast.IdentifierType
                                    ):
                                        param_type = pyi_builder.get_py_type(
                                            param.type.type.names[0]
                                        )

                                    elif isinstance(
                                        param.type.type,
                                        c_ast.TypeDecl
                                    ):
                                        if isinstance(
                                            param.type.type.type,
                                            c_ast.IdentifierType
                                        ):
                                            param_type = (
                                                pyi_builder.get_py_type(
                                                    param.type.type.type.names[0]  # NOQA
                                                )
                                            )

                                        elif isinstance(
                                            param.type.type.type,
                                            c_ast.Struct
                                        ):
                                            param_type = (
                                                pyi_builder.get_py_type(
                                                    param.type.type.type.name
                                                )
                                            )
                                        else:
                                            raise RuntimeError(
                                                str(type(param.type.type.type))
                                            )
                                    else:
                                        raise RuntimeError(
                                            str(type(param.type.type))
                                        )

                                elif isinstance(param.type, c_ast.TypeDecl):
                                    param_type = pyi_builder.get_py_type(
                                        param.type.type.names[0]
                                    )

                                elif isinstance(param.type, c_ast.ArrayDecl):
                                    param_type = (
                                        'list[' + pyi_builder.get_py_type(
                                            param.type.type.type.names[0]
                                        ) + ']'
                                    )

                                else:
                                    raise RuntimeError(str(type(param.type)))
                            else:
                                raise RuntimeError(str(type(param)))

                            param_types.append(param_type)

                        if param_types:
                            param_types = '[' + (', '.join(param_types)) + ']'
                        else:
                            param_types = '...'

                        pyi_builder.pyi_callbacks.append(
                            pyi_callback_template.format(
                                func_name=name.replace('lv_', '', 1),
                                param_types=param_types,
                                ret_type=ret_type
                            )
                        )

                        pyi_builder.pyi_callback_names.append(
                            name.replace('lv_', '', 1)
                        )
                        break
    return s


# saving the old generator functions so they can be put back in place before
# cffi runs. cffi uses pycparser and I do not know if it uses the generator at
# all. so better safe then sorry
old_visit = c_generator.CGenerator.visit
old_visit_FuncDecl = c_generator.CGenerator.visit_FuncDecl
old_visit_Typedef = c_generator.CGenerator.visit_Typedef

# putting the updated functions in place
setattr(c_generator.CGenerator, 'visit', visit)
setattr(c_generator.CGenerator, 'visit_FuncDef', visit_FuncDef)
setattr(c_generator.CGenerator, 'visit_Typedef', visit_Typedef)

generator = c_generator.CGenerator()
ffibuilder = FFI()

# create the definitions that cffi needs to make the binding
cdef = """
#define INT32_MAX 2147483647
typedef char* va_list;

{ast}


"""
cdef = cdef.format(ast=str(generator.visit(ast)))
# my monkey patchs were not perfect and when I removed all of the
# typedefs put in place from the fake lib c header files I was not able to
# remove the trailing semicolon. So thaat is what is being done here.
cdef = '\n'.join(line for line in cdef.split('\n') if line.strip() != ';')

# putting the old functions back in place
setattr(c_generator.CGenerator, 'visit', old_visit)
setattr(c_generator.CGenerator, 'visit_FuncDecl', old_visit_FuncDecl)
setattr(c_generator.CGenerator, 'visit_Typedef', old_visit_Typedef)

# this is what generates the lvgl.pyi file. without this file
# none of the coding insights in a Python IDE will work because of the dynamic
# nature of this binding.
pyi_builder.setup()

for child in ast:
    # check to see if this "child" (node) is from the fake_lib_c includes
    # if it is then we skip it since it is not needed
    if is_lib_c_node(child):
        continue

    # The way I wrote the pyi builder is rather crafty actually.
    # There is some smoke and mirrors to it but not too bad.
    # I wrote a class that overrides the module import of pyi_builder.
    # I did this to allow dynamic loading of the nodes that I wanted to use
    # from pycparser. The nodes I don't use I didn't have to define specifically
    # and instead it gets dumped into a CaatchAll class that does nothing.
    # The string representation of the nodes has been monkey pathed to flatten
    # the output. I use this output in a dynamic way using eval and setting the
    # globals dictionary to that module class I made which is a subclass of a
    # dict. This allow me to pull the requested c_ast classes which are
    # version that I wrote located in the pyi_builder module. Doing this makes
    # for a smaller code footprint because I don't have to have all kinds of
    # crazy instance checking to see what I am dealing with.
    test = eval('Root' + str(child), pyi_builder)
    test.gen_pyi()


with open('lvgl.pyi', 'w') as f:
    f.write('from typing import List, Optional, Callable, Any\n\n\n')
    f.write('class va_list(list):\n    pass\n\n\n')
    f.write('# ****************  ENUMERATIONS  ****************\n')
    f.write('\n\n\n'.join(pyi_builder.pyi_enums))
    f.write('\n# ************************************************\n')
    f.write('\n\n# ********************  TYPES  *******************\n')
    f.write(('\n'.join(pyi_builder.pyi_types)))
    f.write('\n# ************************************************\n')
    f.write('\n\n# *****************  CALLBACKS  ******************\n')
    f.write(('\n\n'.join(pyi_builder.pyi_callbacks)))
    f.write('\n# ************************************************\n')
    f.write('\n\n# ***************  STRUCTS/UNIONS  ***************\n')
    f.write(('\n\n\n'.join(pyi_builder.pyi_structs)))
    f.write('\n# ************************************************\n')
    f.write('\n\n# ******************  TYPEDEFS  ******************\n')
    f.write('\n\n'.join(pyi_builder.pyi_typedefs) + '\n')
    f.write('\n# ************************************************\n')
    f.write('\n\n# *****************  FUNCTIONS  ******************\n')
    f.write('\n\n'.join(pyi_builder.pyi_funcs))
    f.write('\n# ************************************************\n')


# set the definitions into cffi
ffibuilder.cdef(cdef)

# set the name of the c extension and also tell cffi what we need to compile
ffibuilder.set_source(
    "_lib_lvgl",
    '#include "lvgl.h"',
    sources=iter_sources(lvgl_src_path),
    define_macros=[('CPYTHON_SDL', 1)],
    library_dirs=library_dirs,
    libraries=libraries,
    include_dirs=include_dirs,
    extra_compile_args=cpp_args,
    language='c'
)

# change the path into the lvgl directory
os.chdir(lvgl_path)

# start the compilation
try:
    res = ffibuilder.compile(verbose=True)
except:  # NOQA
    import traceback

    traceback.print_exc()
    sys.exit(1)

os.chdir(base_path)

with open('lvgl.py.template', 'r') as f:
    lvgl_template = f.read()

with open('lvgl.py', 'w') as f:
    f.write(lvgl_template.replace('~!~!CALLBACKS!~!~', '\n'.join(callbacks)))

out_file_name = os.path.split(res)[-1]

shutil.copyfile(res, os.path.join(build_path, out_file_name))
shutil.copyfile('lvgl.py', os.path.join(build_path, 'lvgl.py'))
shutil.copyfile('lvgl.pyi', os.path.join(build_path, 'lvgl.pyi'))

print('extension module is located here: "' + build_path + '"')
