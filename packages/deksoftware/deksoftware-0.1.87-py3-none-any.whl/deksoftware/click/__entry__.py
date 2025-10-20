import typer
from typing_extensions import Annotated
from dektools.typer import command_mixin, command_version
from dektools.cfg import ObjectCfg
from dektools.dict import string_to_map_list
from dektools.web.url import Url
from ..core.repository import Repository
from . import app

command_version(app, __name__)


def main():
    app()


cfg = ObjectCfg(__name__, 'install', module=True)


@command_mixin(app)
def config(args, typed=''):
    if not args and not typed:
        data = None
    else:
        data = dict(args=args, typed=typed)
    cfg.set(data)


@command_mixin(app)
def install(args, name, version='', path='', typed='', extra=''):
    data = cfg.get()
    typed = typed or data.get('typed')
    args = args or data.get('args') or ''
    Repository(typed, *args.split(' ')).install(name, version, path, extra)


@app.command()
def sync(
        registry,
        username: Annotated[str, typer.Argument()] = "",
        password: Annotated[str, typer.Argument()] = "",
        versions=''):
    url = Url.new(registry)
    username = username or url.username
    password = password or url.password
    repo_default = Repository('default')
    repo_sync = Repository('pypi', registry, username, password)
    print(f"packages: {list(repo_default.packages)}", flush=True)
    versions = string_to_map_list(versions)
    for name, package in repo_default.packages.items():
        all_versions = sorted({*package.versions[:3], *versions.get(name, [])})
        print(f"versions({name}): {all_versions}", flush=True)
        for version in all_versions:
            package_sync = repo_sync.packages[name]
            if package_sync.exist(version):
                print(f"skip {name}-{version} as exist", flush=True)
                continue
            path = package.pull(version)
            print(f"pulled {name}-{version}: {path}", flush=True)
            package_sync.push(path, version)
            print(f"pushed {name}-{version}", flush=True)
