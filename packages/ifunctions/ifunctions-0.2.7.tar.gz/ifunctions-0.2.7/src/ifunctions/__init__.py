# src/ifunctions/__init__.py
from importlib import import_module
from pkgutil import walk_packages


def _public_names(mod):
    if hasattr(mod, "__all__"):
        return list(mod.__all__)
    return [n for n in mod.__dict__ if not n.startswith("_")]


for _, fullname, _ in walk_packages(__path__, prefix=__name__ + "."):
    short = fullname.rsplit(".", 1)[-1]
    if short.startswith("_"):
        continue
    mod = import_module(fullname)
    for name in _public_names(mod):
        if name in globals():
            raise RuntimeError(
                f"Nama '{name}' bentrok antara modul dalam paket: sumber={fullname}"
            )
        globals()[name] = getattr(mod, name)


def main() -> None:
    print("Hello from ifunctions!")
    __import__('pprint').pprint(globals())

__import__('pprint').pprint(globals())


