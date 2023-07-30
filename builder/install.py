from setuptools.command import install as _orig_install


class install(_orig_install.install):

    def initialize_options(self):
        _orig_install.orig.install.initialize_options(self)
        self.old_and_unmanageable = None
        self.single_version_externally_managed = None
