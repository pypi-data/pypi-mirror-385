import ast
from pathlib import Path

from .utils import get_builtin_modules, get_ignore_dirs


def traversal_directory(directory: str) -> tuple[set[str], set[str]]:
    """get all imports and local modules in a directory"""
    all_imports = set()
    local_modules = set()

    # recursive traversal directory
    for file in get_py_files(directory):
        imports = get_imports_from_file(file)
        all_imports.update(imports)

        update_local_modules(local_modules, file)

    return all_imports, local_modules


def get_py_files(directory: str):
    """yield .py files in a directory"""
    ignore_dirs = get_ignore_dirs()
    for file in Path(directory).iterdir():
        if file.is_file() and file.suffix == ".py":
            yield file
        elif file.is_dir():
            if file.name in ignore_dirs:
                continue
            yield from get_py_files(file)


def get_imports_from_file(file_path: Path) -> set[str]:
    """analyze imports in a single python file"""
    imports = set()

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            tree = ast.parse(file.read())

        for node in ast.walk(tree):
            # deal import xxx
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name.split(".")[0])

            # deal from xxx import yyy
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])

    except Exception as e:
        print(f"analyze {file_path} error: {str(e)}")

    return imports


def update_local_modules(local_modules: set[str], file: Path):
    """add local modules to set"""
    for p in file.parents:
        local_modules.add(p.name)
    local_modules.add(file.name.replace(".py", ""))


def filter_imports(imports: set[str], local_modules: set[str]) -> set[str]:
    """filter imports that are not in the local directory and not in the built-in modules"""
    built_in_modules = get_builtin_modules()

    return imports - local_modules - built_in_modules


def get_third_party_imports(dir: str) -> set[str]:
    """
    get all third party imports from a directory,
    exclude local modules and built-in modules
    """
    all_imports, local_modules = traversal_directory(dir)
    return filter_imports(all_imports, local_modules)
