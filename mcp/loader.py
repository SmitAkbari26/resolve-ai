import pkgutil
import tools
import importlib


def load_tools():
    """
    Load all submodules in the 'tools' package.

    Iterates over each module found in the package's path and imports it,
    ensuring that all tool modules are loaded and available for use.
    """

    for _, module_name, is_pkg in pkgutil.walk_packages(
        tools.__path__, prefix=f"{tools.__name__}."
    ):
        if not is_pkg:
            importlib.import_module(module_name)
