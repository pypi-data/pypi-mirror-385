from dektools.typer import command_mixin
from dektools.cfg import ObjectCfg
from dektools.dict import string_to_map_list
from ..core.repository import Repository
from . import app


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
def sync(registry, username, password, versions=''):
    repo_default = Repository('default')
    repo_sync = Repository('pypi', registry, username, password)
    print(f"packages: {list(repo_default.packages)}", flush=True)
    versions = string_to_map_list(versions)
    for name, package in repo_default.packages.items():
        all_versions = sorted({*package.versions[:3], *versions.get(name, [])})
        print(f"versions({name}): {all_versions}", flush=True)
        for version in all_versions:
            version = version or 'latest'
            package_coding = repo_sync.packages[name]
            if version != 'latest' and package_coding.exist(version):
                print(f"skip {name}-{version} as exist", flush=True)
                continue
            path = package.pull(version)
            print(f"pulled {name}-{version}: {path}", flush=True)
            repo_sync.packages[name].push(path, version)
            print(f"pushed {name}-{version}", flush=True)
