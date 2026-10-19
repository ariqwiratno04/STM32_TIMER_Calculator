"""Make Tcl/Tk library files available when Python ships them in zip files."""

import os
import sys
import zipfile
from pathlib import Path, PurePosixPath


def configure_tk() -> None:
    tcl_dir = Path(sys.base_prefix) / "tcl"
    tcl_zip = next(tcl_dir.glob("libtcl*.zip"), None)
    tk_zip = next(tcl_dir.glob("libtk*.zip"), None)
    if tcl_zip is None or tk_zip is None:
        return

    destination = Path(__file__).resolve().parent / ".runtime" / "tcl"
    libraries = (
        (tcl_zip, destination / "tcl_library", "init.tcl"),
        (tk_zip, destination / "tk_library", "tk.tcl"),
    )
    for archive_path, library_dir, required_file in libraries:
        if not (library_dir / required_file).is_file():
            with zipfile.ZipFile(archive_path) as archive:
                for name in archive.namelist():
                    path = PurePosixPath(name)
                    if path.is_absolute() or ".." in path.parts:
                        raise ValueError("Unsafe Tcl/Tk archive path.")
                archive.extractall(destination)

    os.environ.setdefault("TCL_LIBRARY", str(libraries[0][1]))
    os.environ.setdefault("TK_LIBRARY", str(libraries[1][1]))
