from setuptools.command import build_ext as _build_ext
from setuptools.command import build_clib
from setuptools import dep_util
from setuptools.extension import Library
import threading
import os

log = build_clib.log  # NOQA
DistutilsSetupError = build_clib.DistutilsSetupError  # NOQA


class build_ext(_build_ext.build_ext):

    def get_ext_filename(self, fullname):
        ext_name = _build_ext.build_ext.get_ext_filename(self, fullname)
        name, ext = os.path.splitext(ext_name)
        name = name.split('.')[0]
        return name + ext

    def build_extension(self, ext):
        print(self.debug)

        if self.debug:
            _build_ext.build_ext.build_extension(self, ext)
            return

        ext._convert_pyx_sources_to_lang()  # NOQA
        _compiler = self.compiler
        try:
            if isinstance(ext, Library):
                self.compiler = self.shlib_compiler
            self.__build_extension(ext)
            if ext._needs_stub:  # NOQA
                build_lib = self.get_finalized_command('build_py').build_lib
                self.write_stub(build_lib, ext)
        finally:
            self.compiler = _compiler

    def __build_extension(self, ext):
        sources = ext.sources
        if sources is None or not isinstance(sources, (list, tuple)):
            raise DistutilsSetupError(
                "in 'ext_modules' option (extension '%s'), "
                "'sources' must be present and must be "
                "a list of source filenames" % ext.name
            )
        # sort to make the resulting .so file build reproducible
        sources = sorted(sources)

        ext_path = self.get_ext_fullpath(ext.name)
        depends = sources + ext.depends
        if not (self.force or dep_util.newer_group(depends, ext_path, 'newer')):  # NOQA
            log.debug("skipping '%s' extension (up-to-date)", ext.name)
            return
        else:
            log.info("building '%s' extension", ext.name)

        # First, scan the sources for SWIG definition files (.i), run
        # SWIG on 'em to create .c files, and modify the sources list
        # accordingly.
        sources = self.swig_sources(sources, ext)

        # Next, compile the source code to object files.

        # XXX not honouring 'define_macros' or 'undef_macros' -- the
        # CCompiler API needs to change to accommodate this, and I
        # want to do one thing at a time!

        # Two possible sources for extra compiler arguments:
        #   - 'extra_compile_args' in Extension object
        #   - CFLAGS environment variable (not particularly
        #     elegant, but people seem to expect it and I
        #     guess it's useful)
        # The environment variable should take precedence, and
        # any sensible compiler will give precedence to later
        # command line args.  Hence we combine them in order:
        extra_args = ext.extra_compile_args or []

        macros = ext.define_macros[:]
        for undef in ext.undef_macros:
            macros.append((undef,))

        exit_event = threading.Event()
        thread_error_event = threading.Event()
        threads = []
        objects = []
        err = []
        object_lock = threading.Lock()

        num_threaads = os.cpu_count()

        num_files = int(len(sources) / num_threaads)
        if num_files % 2:
            num_files += 1

        def run(srcs):
            for src in srcs:
                if thread_error_event.is_set():
                    break

                try:
                    obj = self.compiler.compile(
                        [src],
                        output_dir=self.build_temp,
                        macros=macros,
                        include_dirs=ext.include_dirs,
                        debug=self.debug,
                        extra_postargs=extra_args,
                        depends=ext.depends,
                    )
                except Exception as error:
                    err.append(error)
                    thread_error_event.set()
                else:
                    with object_lock:
                        objects.extend(obj)

            threads.remove(threading.current_thread())
            if not threads:
                exit_event.set()

        while sources:
            t_sources = []
            for _ in range(min(num_files, len(sources))):
                t_sources.append(sources.pop(0))

            t = threading.Thread(target=run, args=(t_sources[:],))
            t.daemon = True
            threads.append(t)
            t.start()

        exit_event.wait()

        if err:
            raise err[0]

        # XXX outdated variable, kept here in case third-part code
        # needs it.
        self._built_objects = objects[:]

        # Now link the object files together into a "shared object" --
        # of course, first we have to figure out all the other things
        # that go into the mix.
        if ext.extra_objects:
            objects.extend(ext.extra_objects)
        extra_args = ext.extra_link_args or []

        # Detect target language, if not provided
        language = ext.language or self.compiler.detect_language(sources)

        self.compiler.link_shared_object(
            objects,
            ext_path,
            libraries=self.get_libraries(ext),
            library_dirs=ext.library_dirs,
            runtime_library_dirs=ext.runtime_library_dirs,
            extra_postargs=extra_args,
            export_symbols=self.get_export_symbols(ext),
            debug=self.debug,
            build_temp=self.build_temp,
            target_lang=language,
        )
