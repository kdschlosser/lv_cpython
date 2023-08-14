# -*- coding: utf-8 -*-

import os
import sys
from setuptools.command.build import build as _build  # NOQA

import shutil
import pycparser  # NOQA
from . import py_builder


DLLMAIN_H = '''
#include <windows.h>

extern BOOL WINAPI DllMain(
    HINSTANCE const instance, DWORD const reason, LPVOID const reserved
);

'''


DLL_MAIN = '''
#include "dllmain.h"

extern BOOL WINAPI DllMain(
    HINSTANCE const instance, DWORD const reason, LPVOID const reserved
);

extern BOOL WINAPI DllMain (
    HINSTANCE const instance,  // handle to DLL module
    DWORD     const reason,    // reason for calling function
    LPVOID    const reserved)  // reserved
{
    // Perform actions based on the reason for calling.
    switch (reason)
    {
    case DLL_PROCESS_ATTACH:
        // Initialize once for each new process.
        // Return FALSE to fail DLL load.
        break;

    case DLL_THREAD_ATTACH:
        // Do thread-specific initialization.
        break;

    case DLL_THREAD_DETACH:
        // Do thread-specific cleanup.
        break;

    case DLL_PROCESS_DETACH:
        // Perform any necessary cleanup.
        break;
    }
    return TRUE;  // Successful DLL_PROCESS_ATTACH.
}

'''

if not sys.platform.startswith('win'):
    DLLMAIN_H = ''
    DLL_MAIN = '#include "dllmain.h"\n\n'


IGNORE_DIRS = (
    'osal', 'micropython', 'arm2d', 'gd32_ipa',
    'nxp', 'stm32_dma2d', 'swm341_dma2d', 'tiny_ttf',
    'rlottie', 'freetype', 'ffmpeg'
)
IGNORE_FILES = (
)


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
            if not f.endswith('.h'):
                continue

            res.append(file)

    for folder in folders:
        res.extend(iter_sources(folder))

    return res


class build(_build):
    sdl2_dll = None
    lvgl_include_path_env_key = ''
    lvgl_cpp_path = ''
    lvgl_cpp_args = []
    lvgl_libraries = []
    lvgl_include_dirs = []
    lvgl_linker_args = []

    lvgl_header_file = ''
    lvgl_header_path = ''

    lvgl_interface_path = ''
    lvgl_interface_file = ''

    lvgl_output_header_path = ''

    lvgl_path = ''
    lvgl_src_path = ''
    lvgl_config_path = ''
    lvgl_fake_libc_path = ''

    lvgl_output_path = ''

    user_options = [
        ('debug', None, 'adds debugging output to the compilation')
    ] + _build.user_options

    boolean_options = ['debug'] + _build.boolean_options

    def finalize_options(self):
        _build.finalize_options(self)

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        self.lvgl_interface_path = os.path.abspath(
            os.path.join(self.build_temp, 'lvgl.i')
        )
        self.lvgl_fake_libc_path = os.path.abspath(
            self.lvgl_fake_libc_path
        )
        self.lvgl_output_path = os.path.abspath(
            os.path.join(self.build_lib, 'lvgl')
        )
        self.lvgl_output_header_path = os.path.abspath(
            os.path.join(self.build_temp, 'lvgl.h')
        )

        if not os.path.exists(self.lvgl_output_path):
            os.makedirs(self.lvgl_output_path)

        self.distribution.include_dirs = self.lvgl_include_dirs

    def run(self):
        lvgl_header_path = os.path.abspath(self.lvgl_header_path)
        lvgl_src_path = os.path.abspath(self.lvgl_src_path)

        cwd = os.getcwd()
        os.chdir(self.build_temp)

        def _rel_path(p):
            return os.path.relpath(p).replace('\\', '/')

        if sys.platform.startswith('win'):
            sdl_include = f'"{_rel_path(self.lvgl_include_dirs[1])}/SDL2/SDL.h"'
            macros = (
                '#define SDLCALL\n' 
                '#define DECLSPEC\n' 
                '#define SDL_NORETURN\n'
                '#define SDL_INLINE inline\n'
                '#define SDL_FORCE_INLINE static SDL_INLINE\n'
                '#ifdef __cdecl\n'
                '#undef __cdecl\n'
                '#endif\n'
                '#define __cdecl\n'
                '#ifdef __stdcall\n'
                '#undef __stdcall\n'
                '#endif\n'
                '#define __stdcall\n'
                '#define _CRT_BEGIN_C_HEADER\n'
                '#define _CRT_END_C_HEADER\n'
            )

        else:
            sdl_include = 'LV_SDL_INCLUDE_PATH'
            macros = ''

        # {macros}
        # define SDL_MAIN_HANDLED
        # #include {sdl_include}

        files = iter_sources(lvgl_src_path)

        lvgl_header_file = ''
        print(lvgl_header_path)

        dll_main_h = f'''
#include "{_rel_path(lvgl_header_path)}"
// #include "{_rel_path(lvgl_src_path)}/disp/lv_disp_private.h"
// #include "{_rel_path(lvgl_src_path)}/indev/lv_indev_private.h"
'''
        for f in files:
            lvgl_header_file += f'#include "{_rel_path(f)}"\n'
            dll_main_h += f'#include "{_rel_path(f)}"\n'

        os.chdir(cwd)

        with open(self.lvgl_output_header_path, 'w') as f:
            f.write(lvgl_header_file)

        if self.lvgl_include_path_env_key in os.environ:
            os.environ[self.lvgl_include_path_env_key] = (
                self.lvgl_fake_libc_path +
                os.pathsep +
                os.environ[self.lvgl_include_path_env_key]
            )
        else:
            os.environ[self.lvgl_include_path_env_key] = (
                self.lvgl_fake_libc_path + os.pathsep
            )

        ast = pycparser.parse_file(
            self.lvgl_output_header_path,
            use_cpp=True,
            cpp_path=self.lvgl_cpp_path,
            cpp_args=(
                self.lvgl_cpp_args[:] +
                ['-E', '-DPYCPARSER', f'-I"{self.lvgl_fake_libc_path}"']
            ),
            parser=None
        )

        py_builder.run(self.lvgl_output_path, ast)

        # py_builder.export_symbols

        h_template = DLLMAIN_H
        h_template += dll_main_h  # .replace(macros, '')
        h_template += '\n'.join(
            line for line in py_builder.func_decls if line.strip() != ';'
        ) + '\n'

        h_template += '\n'.join(py_builder.exported_variables)

        c_template = DLL_MAIN
        c_template += '\n'.join(
            line for line in py_builder.func_decls if line.strip() != ';'
        ) + '\n'

        c_template += '\n'.join(
            line for line in py_builder.func_defs if line.strip() != ';'
        )

        dllmain_source_path = os.path.join(self.build_temp, 'dllmain.c')
        dllmain_header_path = os.path.join(self.build_temp, 'dllmain.h')

        with open(dllmain_source_path, 'w') as f:
            f.write(c_template)

        with open(dllmain_header_path, 'w') as f:
            f.write(h_template)

        os.environ[self.lvgl_include_path_env_key] = (
            os.environ[self.lvgl_include_path_env_key].replace(
                self.lvgl_fake_libc_path + os.pathsep,
                ''
            )
        )

        build_ext = self.get_finalized_command('build_ext')

        full_name = build_ext.get_ext_fullname(
            self.distribution.ext_modules[0].name
        )
        library_name = build_ext.get_ext_filename(full_name)
        self.distribution.ext_modules[0].sources.append(
            f"{dllmain_source_path}"
        )

        _build.run(self)
        file_name = os.path.splitext(library_name)[0]

        for f in os.listdir(self.build_lib):
            if f.startswith(file_name):
                dst = os.path.join(self.lvgl_output_path, f)
                src = os.path.join(self.build_lib, f)

                if os.path.exists(dst):
                    os.remove(dst)

                print('copy file:', src, ' -> ', dst)
                shutil.copyfile(src, dst)
                os.remove(src)

        if sys.platform.startswith('win'):
            dst = os.path.join(self.lvgl_output_path, 'SDL2.dll')

            if os.path.exists(dst):
                os.remove(dst)

            print('copy file:', self.sdl2_dll, ' -> ', dst)

            shutil.copyfile(self.sdl2_dll, dst)

        # mpy_builder.run(self.build_lib)
