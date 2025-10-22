from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules, get_package_paths

pkg_base, pkg_dir = get_package_paths("arcade")
pkg_dir = Path(pkg_dir)

datas = [
    (pkg_dir / "VERSION", "arcade"),
    (pkg_dir / "resources", "arcade/resources"),
]
hiddenimports = collect_submodules("arcade.gl")
