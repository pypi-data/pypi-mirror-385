import os
from dektools.file import write_file
from dekartifacts.registry.staticfiles import StaticfilesRegistry
from .base import PackageBase, register_package

name = __name__.partition('.')[0]


@register_package('pypi')
class PypiPackage(PackageBase):
    @property
    def registry(self):
        return self.args[0]

    @property
    def auth(self):
        if len(self.args) >= 3:
            return dict(username=self.args[1], password=self.args[2])
        return {}

    @property
    def is_remote(self):
        return True

    def exist(self, version):
        registry = StaticfilesRegistry(self.registry)
        return registry.exist(None, name=self.meta['name'], version=version)

    def _pull(self, version):
        registry = StaticfilesRegistry(self.registry)
        registry.login(name=name, **self.auth)
        path = os.path.join(write_file(None), self.filename)
        registry.pull(path, name=self.meta['name'], version=version)
        return path

    def push(self, path, version):
        registry = StaticfilesRegistry(self.registry)
        registry.login(name=name, **self.auth)
        registry.push(path, name=self.meta['name'], version=version)
