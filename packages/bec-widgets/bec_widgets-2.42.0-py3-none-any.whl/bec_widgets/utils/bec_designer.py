import importlib.metadata
import json
import os
import site
import sys
import sysconfig
from pathlib import Path

from bec_qthemes import material_icon
from qtpy import PYSIDE6
from qtpy.QtGui import QIcon

from bec_widgets.utils.bec_plugin_helper import user_widget_plugin

if PYSIDE6:
    from PySide6.scripts.pyside_tool import (
        _extend_path_var,
        init_virtual_env,
        is_pyenv_python,
        is_virtual_env,
        qt_tool_wrapper,
        ui_tool_binary,
    )

import bec_widgets


def designer_material_icon(icon_name: str) -> QIcon:
    """
    Create a QIcon for the BECDesigner with the given material icon name.

    Args:
        icon_name (str): The name of the material icon.

    Returns:
        QIcon: The QIcon for the material icon.
    """
    return QIcon(material_icon(icon_name, filled=True, convert_to_pixmap=True))


def list_editable_packages() -> set[str]:
    """
    List all editable packages in the environment.

    Returns:
        set: A set of paths to editable packages.
    """

    editable_packages = set()

    # Get site-packages directories
    site_packages = site.getsitepackages()
    if hasattr(site, "getusersitepackages"):
        site_packages.append(site.getusersitepackages())

    for dist in importlib.metadata.distributions():
        location = dist.locate_file("").resolve()
        is_editable = all(not str(location).startswith(site_pkg) for site_pkg in site_packages)

        if is_editable:
            editable_packages.add(str(location))

    for packages in site_packages:
        # all dist-info directories in site-packages that contain a direct_url.json file
        dist_info_dirs = Path(packages).rglob("*.dist-info")
        for dist_info_dir in dist_info_dirs:
            direct_url = dist_info_dir / "direct_url.json"
            if not direct_url.exists():
                continue
            # load the json file and get the path to the package
            with open(direct_url, "r", encoding="utf-8") as f:
                data = json.load(f)
                path = data.get("url", "")
                if path.startswith("file://"):
                    path = path[7:]
                    editable_packages.add(path)

    return editable_packages


def patch_designer(cmd_args: list[str] = []):  # pragma: no cover
    if not PYSIDE6:
        print("PYSIDE6 is not available in the environment. Cannot patch designer.")
        return

    init_virtual_env()

    major_version = sys.version_info[0]
    minor_version = sys.version_info[1]
    os.environ["PY_MAJOR_VERSION"] = str(major_version)
    os.environ["PY_MINOR_VERSION"] = str(minor_version)

    if sys.platform == "win32":
        if is_virtual_env():
            _extend_path_var("PATH", os.fspath(Path(sys._base_executable).parent), True)
    else:
        if sys.platform == "linux":
            env_var = "LD_PRELOAD"
            current_pid = os.getpid()
            with open(f"/proc/{current_pid}/maps", "rt") as f:
                for line in f:
                    if "libpython" in line:
                        lib_path = line.split()[-1]
                        os.environ[env_var] = lib_path
                        break

        elif sys.platform == "darwin":
            suffix = ".dylib"
            env_var = "DYLD_INSERT_LIBRARIES"
            version = f"{major_version}.{minor_version}"
            library_name = f"libpython{version}{suffix}"
            lib_path = str(Path(sysconfig.get_config_var("LIBDIR")) / library_name)
            os.environ[env_var] = lib_path
        else:
            raise RuntimeError(f"Unsupported platform: {sys.platform}")

        if is_pyenv_python() or is_virtual_env():
            # append all editable packages to the PYTHONPATH
            editable_packages = list_editable_packages()
            for pckg in editable_packages:
                _extend_path_var("PYTHONPATH", pckg, True)
    qt_tool_wrapper(ui_tool_binary("designer"), cmd_args)


def find_plugin_paths(base_path: Path):
    """
    Recursively find all directories containing a .pyproject file.
    """
    plugin_paths = []
    for path in base_path.rglob("*.pyproject"):
        plugin_paths.append(str(path.parent))
    return plugin_paths


def set_plugin_environment_variable(plugin_paths):
    """
    Set the PYSIDE_DESIGNER_PLUGINS environment variable with the given plugin paths.
    """
    current_paths = os.environ.get("PYSIDE_DESIGNER_PLUGINS", "")
    if current_paths:
        current_paths = current_paths.split(os.pathsep)
    else:
        current_paths = []

    current_paths.extend(plugin_paths)
    os.environ["PYSIDE_DESIGNER_PLUGINS"] = os.pathsep.join(current_paths)


# Patch the designer function
def open_designer(cmd_args: list[str] = []):  # pragma: no cover
    if not PYSIDE6:
        print("PYSIDE6 is not available in the environment. Exiting...")
        return
    base_dir = Path(os.path.dirname(bec_widgets.__file__)).resolve()

    plugin_paths = find_plugin_paths(base_dir)
    if (plugin_repo := user_widget_plugin()) and isinstance(plugin_repo.__file__, str):
        plugin_repo_dir = Path(os.path.dirname(plugin_repo.__file__)).resolve()
        plugin_paths.extend(find_plugin_paths(plugin_repo_dir))

    set_plugin_environment_variable(plugin_paths)

    patch_designer(cmd_args)


def main():
    open_designer(sys.argv[1:])


if __name__ == "__main__":  # pragma: no cover
    main()
