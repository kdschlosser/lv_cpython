import os
import sys

project_path = os.path.dirname(__file__)
sys.path.insert(0, project_path)

import pycparser  # NOQA
from pycparser import c_ast, c_generator  # NOQA
import cffi  # NOQA

from setuptools import setup
from builder import utils, build, install


if '--debug' in sys.argv:
    debug = True
    sys.argv.remove('--debug')
else:
    debug = False


build_path = os.path.relpath(os.path.join(project_path, 'build'))
build_temp = os.path.join(build_path, 'temp')

fake_libc_path = os.path.join(project_path, 'builder', 'fake_libc_include')
lvgl_path = os.path.relpath(os.path.join(project_path, 'src', 'lvgl'))
lvgl_src_path = os.path.join(lvgl_path, 'src')
lvgl_header_path = os.path.join(lvgl_path, 'demos', 'lv_demos.h')
lvgl_config_path = os.path.relpath(
    os.path.join(project_path, 'src', 'lv_conf.h')
)

if not os.path.exists(build_temp):
    os.makedirs(build_temp)


library_dirs = []
include_dirs = ['.']
linker_args = []
libraries = ['SDL2']
cpp_args = ['-DCPYTHON_SDL']


if sys.platform.startswith('win'):
    from builder import get_sdl2

    import pyMSVC  # NOQA

    environment = pyMSVC.setup_environment()
    print(environment)

    # compiler to use
    cpp_path = 'cl'
    sdl2_include, sdl2_dll = get_sdl2.get_sdl2(build_temp)
    include_dirs += [sdl2_include]
    library_dirs += [os.path.split(sdl2_dll)[0]]
    libraries.append('legacy_stdio_definitions')

    build.sdl2_dll = sdl2_dll
    cpp_args.insert(0, '-std:c11')
    cpp_args.extend([
        '/wd4996',
        '/wd4244',
        '/wd4267'
    ])
    include_path_env_key = 'INCLUDE'

    if '-debug' in sys.argv:
        linker_args.append('/DEBUG')
        cpp_args.append('/Zi')


elif sys.platform.startswith('darwin'):
    include_path_env_key = 'C_INCLUDE_PATH'

    cpp_path = 'clang'
    cpp_args.insert(0, '-std=c11')

    if debug:
        cpp_args.append('-ggdb')


else:
    include_path_env_key = 'C_INCLUDE_PATH'

    cpp_path = 'gcc'
    cpp_args.insert(0, '-std=c11')
    cpp_args.append('-Wno-incompatible-pointer-types')
    if debug:
        cpp_args.append('-ggdb')



build.extra_includes = include_dirs


if include_path_env_key in os.environ:
    os.environ[include_path_env_key] = (
        fake_libc_path + os.pathsep + os.environ[include_path_env_key]
    )
else:
    os.environ[include_path_env_key] = fake_libc_path + os.pathsep

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
    if utils.is_lib_c_node(node):
        return ''

    method = f'visit_{node.__class__.__name__}'
    ret = getattr(self, method, self.generic_visit)(node)
    return '' if ret.strip() == ';' else ret


# turns function definitions into declarations.
def visit_FuncDef(self, n):
    decl = self.visit(n.decl)  # NOQA
    self.indent_level = 0
    if n.param_decls:
        knrdecls = ';\n'.join(self.visit(p) for p in n.param_decls)
        res = decl + '\n' + knrdecls + ';\n'
    else:
        res = decl + ';\n'

    return res


callback_names = []


def visit_Typedef(self, n):
    s = ''
    if n.storage:
        s += ' '.join(n.storage) + ' '

    s += self._generate_type(n.type)

    node = n
    for type_ in (
        c_ast.PtrDecl,
        c_ast.FuncDecl,
        (c_ast.TypeDecl, c_ast.PtrDecl)
    ):
        if isinstance(node.type, type_):
            node = node.type
        else:
            return s

    while isinstance(node, c_ast.PtrDecl):
        node = node.type

    name = node.declname
    for item in ('_cb_t', '_f_t'):
        if not name.endswith(item):
            continue

        if f'py_{name}' in callback_names:
            return ''

        callback_names.append(f'py_{name}')

        s = s.replace(f'(*{name})', f'py_{name}') + ';\n' + s

        if s.startswith('typedef'):
            s = '\n\nextern "Python"' + s[7:]
        else:
            s = '\n\nextern "Python"' + s

        break

    return s


CDEF = """
#define INT32_MAX 2147483647
typedef char* va_list;

{ast}

"""

# read the lvgl header files so we can generate the information
# that CFFI needs I know that LVGL was written for c99 and thata I
# am using c11. This is because the MSVC compiler does not support c99.
# c11 seems to work without any issues.
ast = pycparser.parse_file(
    lvgl_header_path,
    use_cpp=True,
    cpp_path=cpp_path,
    cpp_args=cpp_args + ['-E', '-DPYCPARSER', '-I"{0}"'.format(fake_libc_path)],
    parser=None
)


build.ast = ast


# saving the old generator functions so they can be put
# back in place before cffi runs. cffi uses pycparser and I do not
# know if it uses the generator at all. so better safe then sorry
old_visit = c_generator.CGenerator.visit
old_visit_FuncDecl = c_generator.CGenerator.visit_FuncDecl
old_visit_Typedef = c_generator.CGenerator.visit_Typedef

# putting the updated functions in place
setattr(c_generator.CGenerator, 'visit', visit)
setattr(c_generator.CGenerator, 'visit_FuncDef', visit_FuncDef)
setattr(c_generator.CGenerator, 'visit_Typedef', visit_Typedef)

generator = c_generator.CGenerator()
ffibuilder = cffi.FFI()

# create the definitions that cffi needs to make the binding

cdef = CDEF.format(ast=str(generator.visit(ast)))

# putting the old functions back in place
setattr(c_generator.CGenerator, 'visit', old_visit)
setattr(c_generator.CGenerator, 'visit_FuncDecl', old_visit_FuncDecl)
setattr(c_generator.CGenerator, 'visit_Typedef', old_visit_Typedef)

# my monkey patchs were not perfect and when I removed all of the
# typedefs put in place from the fake lib c header files
# I was not able to remove the trailing semicolon. So thaat is what is
# being done here.
cdef = '\n'.join(
    line for line in cdef.split('\n') if line.strip() != ';'
)

# set the definitions into cffi
ffibuilder.cdef(cdef)

os.environ[include_path_env_key] = os.environ[include_path_env_key].replace(fake_libc_path + os.pathsep, '')

# set the name of the c extension and also tell cffi what
# we need to compile
ffibuilder.set_source(
    "__lib_lvgl",
    '#include "src/lvgl/demos/lv_demos.h"',
    sources=(
            iter_sources(lvgl_src_path) +
            iter_sources(os.path.join(lvgl_path, 'demos'))
    ),
    define_macros=[('CPYTHON_SDL', 1)],
    library_dirs=library_dirs,
    libraries=libraries,
    include_dirs=include_dirs + [project_path, lvgl_path],
    extra_compile_args=cpp_args,
    extra_link_args=linker_args,
    language='c'
)


ext_modules = [ffibuilder.distutils_extension()]

setup(
    name='lvgl',
    author='Kevin G. Schlosser',
    version='0.1.1b',
    zip_safe=False,
    packages=['lvgl'],
    install_requires=['cffi>=1.15.1'],
    ext_modules=ext_modules,
    cmdclass=dict(build=build, install=install)
)
