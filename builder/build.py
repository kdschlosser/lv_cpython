# -*- coding: utf-8 -*-

import os
import sys
from setuptools.command.build import build as _build  # NOQA

import shutil
from . import py_builder
from . import mpy_builder


class build(_build):
    ast = None
    sdl2_dll = None
    extra_includes = []

    user_options = [
        ('debug', None, 'adds debugging output to the compilation')
    ] + _build.user_options

    boolean_options = ['debug'] + _build.boolean_options

    def finalize_options(self):
        _build.finalize_options(self)
        self.distribution.include_dirs = self.extra_includes

    def run(self):
        _build.run(self)

        lvgl_output_path = os.path.join(self.build_lib, 'lvgl')
        if not os.path.exists(lvgl_output_path):
            os.mkdir(lvgl_output_path)

        py_builder.run(lvgl_output_path, self.ast)

        for file in os.listdir(self.build_lib):
            if file.endswith('pyd') or file.endswith('pdb'):
                src = os.path.join(self.build_lib, file)
                dst = os.path.join(lvgl_output_path, file)
                if os.path.exists(dst):
                    os.remove(dst)

                shutil.copyfile(src, dst)
                os.remove(src)

        if sys.platform.startswith('win'):
            dst = os.path.join(lvgl_output_path, 'SDL2.dll')

            if os.path.exists(dst):
                os.remove(dst)

            shutil.copyfile(self.sdl2_dll, dst)

        mpy_builder.run(self.build_lib)
