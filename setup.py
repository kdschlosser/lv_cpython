import os
import sys

project_path = os.path.dirname(__file__)
sys.path.insert(0, project_path)

import pycparser  # NOQA
from pycparser import c_ast, c_generator  # NOQA
from setuptools import setup  # NOQA
from builder import build, install, build_ext  # NOQA
from setuptools.extension import Library  # NOQA
import time  # NOQA
import datetime  # NOQA


start_time = time.time()

if '-g' in sys.argv:
    debug = True
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

library_dirs = []
include_dirs = ['.']
linker_args = []
libraries = ['SDL2']
cpp_args = ['-DCPYTHON_SDL', '-DLV_LVGL_H_INCLUDE_SIMPLE']

for arg in sys.argv[:]:
    if arg.startswith('-D'):
        cpp_args.append(arg)
        sys.argv.remove(arg)

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
    libraries.append('shell32')
    libraries.append('user32')
    libraries.append('kernel32')
    libraries.append('ucrt')
    libraries.append('vcruntime')

    build.sdl2_dll = sdl2_dll
    cpp_args.insert(0, '-std:c11')
    cpp_args.extend([
        '/TC',
        '/MP',
        # '/MD',
        '/LD',
        '/wd4996',
        '/wd4244',
        '/wd4267'
    ])
    include_path_env_key = 'INCLUDE'

    linker_args.extend([
        '/DLL',
        '/ENTRY:DllMain',
        '/SUBSYSTEM:WINDOWS'
    ])

elif sys.platform.startswith('darwin'):
    include_path_env_key = 'C_INCLUDE_PATH'

    cpp_path = 'clang'
    cpp_args.insert(0, '-std=c11')

else:
    include_path_env_key = 'C_INCLUDE_PATH'

    cpp_path = 'gcc'
    cpp_args.insert(0, '-std=c11')
    cpp_args.append('-Wno-incompatible-pointer-types')
    if debug:
        cpp_args.append('-ggdb')

build.lvgl_include_path_env_key = include_path_env_key
build.lvgl_cpp_path = cpp_path
build.lvgl_cpp_args = cpp_args
build.lvgl_linker_args = linker_args
build.lvgl_libraries = libraries
build.lvgl_include_dirs = include_dirs
build.lvgl_header_path = lvgl_header_path
build.lvgl_config_path = lvgl_config_path
build.lvgl_src_path = lvgl_src_path
build.lvgl_path = lvgl_path
build.lvgl_fake_libc_path = fake_libc_path


# some paths/files we do not need to compile the source files for.
IGNORE_DIRS = (
    'osal', 'micropython', 'arm2d', 'gd32_ipa',
    'nxp', 'stm32_dma2d', 'swm341_dma2d'
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
            if f == 'disp' and p.endswith('dev'):
                continue

            folders.append(file)
        elif f not in IGNORE_FILES:
            if not f.endswith('.c'):
                continue

            res.append(file)

    for folder in folders:
        res.extend(iter_sources(folder))

    return res


extensions = [Library(
    "_lib_lvgl",
    sources=(
        iter_sources(lvgl_src_path) +
        iter_sources(os.path.join(lvgl_path, 'demos'))
    ),
    library_dirs=library_dirs,
    libraries=libraries,
    include_dirs=include_dirs + [project_path, lvgl_path],
    extra_compile_args=cpp_args,
    extra_link_args=linker_args,
    language='c'
)]

setup(
    name='lvgl',
    author='Kevin G. Schlosser',
    version='0.2.0b',
    zip_safe=False,
    packages=[],
    install_requires=[],
    ext_modules=extensions,
    cmdclass=dict(build=build, install=install, build_ext=build_ext)
)


def strfdelta(tdelta: datetime.timedelta, fmt):
    d = {}
    d['hours'], rem = divmod(tdelta.seconds, 3600)
    d['minutes'], d['seconds'] = divmod(rem, 60)
    d['milliseconds'] = str(int(round(tdelta.microseconds / 1000))).zfill(4)

    d['hours'] = str(d['hours']).zfill(2)
    d['minutes'] = str(d['minutes']).zfill(2)
    d['seconds'] = str(d['seconds']).zfill(2)

    return fmt.format(**d)


stop_time = time.time()

elapsed = datetime.timedelta(microseconds=(stop_time - start_time) * 1000000)

print(
    'build time: ',
    strfdelta(elapsed, '{hours}:{minutes}:{seconds}.{milliseconds}')
)
print('logical processors used:', os.cpu_count())
