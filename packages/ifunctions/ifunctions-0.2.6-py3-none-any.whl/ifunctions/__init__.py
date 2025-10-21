import pkgutil
import importlib

for loader, module_name, is_pkg in pkgutil.walk_packages(__path__, __name__ + "."):
    module = importlib.import_module(module_name)
    for attr in dir(module):
        if not attr.startswith("_"):
            globals()[attr] = getattr(module, attr)


def main() -> None:
    print("Hello from ifunctions!")
